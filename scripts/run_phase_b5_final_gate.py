import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_trend_overlay import TREND_ASSETS, build_trend_weight_paths, load_inputs  # noqa: E402
from run_phase_b1_simulator_reproduction import (  # noqa: E402
    MAX_GROSS_LIMIT,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (  # noqa: E402
    B1_COST_BPS,
    COST_BPS,
    Variant,
    run_execution_simulator,
)
from run_phase_b3_exposure_control import (  # noqa: E402
    build_b2_candidate,
    realized_beta,
    rolling_beta_matrix,
)
from run_phase_b4_risk_engine import (  # noqa: E402
    BETA_MAX_BASE,
    BETA_MAX_SENSITIVITY,
    BETA_MIN,
    TREND_STRESS_SCALE_MAX,
    TREND_STRESS_THRESHOLD,
    B4Variant,
    _NON_BENCHMARK_TREND,
    apply_b4_constraints,
    apply_trend_scaling,
    build_stress_series,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# B.4 promoted candidate (b4_stress_cap_trend_boost, sp500, clipped 2026-04-24)
B4_CAGR = 0.1604
B4_SHARPE = 1.078
B4_MAX_DD = -0.3298
B4_TURNOVER = 84.12
B4_MAX_GROSS = 1.500
B4_AVG_DYNAMIC_CAP = 0.829
B4_MIN_DYNAMIC_CAP = 0.700

# B.1 equal-weight reference Sharpe (10 bps)
B1_EQUAL_WEIGHT_SHARPE = 0.619

# Phase B exit gates
GATE_MAX_DD = -0.40
GATE_SHARPE_50BPS = 0.90
GATE_SHARPE_PREFERRED = 1.00
GATE_MAX_GROSS = 1.50

# Attribution chain (sp500, clipped to 2026-04-24, evaluation 2008–2026)
ATTRIBUTION_CHAIN = [
    {
        "step": "A.7.3 unlagged (research headline)",
        "cagr": 0.2351,
        "sharpe": 1.538,
        "max_dd": -0.2636,
        "turnover": None,
        "note": "same-day signal/return alignment; not a valid backtest baseline",
    },
    {
        "step": "B.1 production open/next-day (10 bps)",
        "cagr": 0.1756,
        "sharpe": 1.116,
        "max_dd": -0.2698,
        "turnover": 230.72,
        "note": "execution lag + realistic simulator costs",
    },
    {
        "step": "B.2 every_2_rebalances (10 bps)",
        "cagr": 0.1833,
        "sharpe": 1.144,
        "max_dd": -0.3369,
        "turnover": 89.62,
        "note": "turnover reduction −61.2% vs B.1",
    },
    {
        "step": "B.3.1 band_50_90 (10 bps)",
        "cagr": 0.1649,
        "sharpe": 1.075,
        "max_dd": -0.3369,
        "turnover": 85.36,
        "note": "beta compliance [0.50, 0.90] at rebalance dates",
    },
    {
        "step": "B.4 stress_cap_trend_boost (10 bps) — promoted",
        "cagr": 0.1604,
        "sharpe": 1.078,
        "max_dd": -0.3298,
        "turnover": 84.12,
        "note": "dynamic beta_cap = 0.90 − 0.20 × stress + trend boost",
    },
]

# Regime windows (inclusive)
REGIMES = [
    ("2008 financial crisis", "2008-01-01", "2009-12-31"),
    ("2015–16 vol stress", "2015-06-01", "2016-12-31"),
    ("2020 COVID", "2020-01-01", "2020-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("2023–2026 recovery", "2023-01-01", "2026-04-24"),
    ("full 2008–2026", "2008-01-01", "2026-04-24"),
]

B5_PROMOTED = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)


def build_promoted_weights(
    inputs: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, list[pd.Timestamp]]:
    base_weights = build_b2_candidate(inputs, validation_end)
    target_turnover = base_weights.diff().abs().sum(axis=1)
    if not base_weights.empty:
        target_turnover.iloc[0] = base_weights.iloc[0].abs().sum()
    control_dates = list(target_turnover[target_turnover > 1e-12].index)

    trend_tickers = [t for t in _NON_BENCHMARK_TREND if t in base_weights.columns]
    scaled = apply_trend_scaling(
        base_weights,
        stress_series,
        control_dates,
        trend_tickers,
        B5_PROMOTED.trend_stress_threshold,
        B5_PROMOTED.trend_stress_scale_max,
    )
    constrained, diagnostics = apply_b4_constraints(
        scaled,
        beta_frame,
        stress_series,
        B5_PROMOTED,
        control_dates,
        inputs["universe_config"].benchmark,
    )
    return constrained, diagnostics, control_dates


def compute_net_returns(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
    cost_bps: float,
) -> pd.Series:
    dates = constrained.index[constrained.index <= validation_end]
    weights = constrained.reindex(dates).fillna(0.0)
    executable = weights.shift(1).fillna(0.0)
    returns = (
        inputs["prices"]
        .pct_change()
        .fillna(0.0)
        .reindex(index=dates, columns=weights.columns)
        .fillna(0.0)
    )
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    return (1.0 - turnover * cost_bps / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0


def metrics_for_window(
    net_returns: pd.Series,
    start: str,
    end: str,
    initial_capital: float = 1.0,
) -> dict:
    mask = (net_returns.index >= pd.Timestamp(start)) & (
        net_returns.index <= pd.Timestamp(end)
    )
    sliced = net_returns[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod() * initial_capital
    m = calculate_metrics(nav)
    return {
        "cagr": m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def cost_sensitivity_table(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> pd.DataFrame:
    rows = []
    initial_capital = inputs["base_config"].portfolio.initial_capital
    for bps in COST_BPS:
        net_ret = compute_net_returns(inputs, constrained, validation_end, bps)
        nav = (1.0 + net_ret).cumprod() * initial_capital
        m = calculate_metrics(nav)
        sharpe = m.get("Sharpe", np.nan)
        rows.append(
            {
                "cost_bps": bps,
                "cagr": m.get("CAGR", np.nan),
                "sharpe": sharpe,
                "max_dd": m.get("Max Drawdown", np.nan),
                "beats_equal_weight": bool(
                    np.isfinite(sharpe) and sharpe >= B1_EQUAL_WEIGHT_SHARPE
                ),
                "passes_sharpe_gate": bool(
                    np.isfinite(sharpe) and sharpe >= GATE_SHARPE_50BPS
                ),
            }
        )
    return pd.DataFrame(rows)


def regime_breakdown_table(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> pd.DataFrame:
    initial_capital = inputs["base_config"].portfolio.initial_capital
    net_ret = compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    rows = []
    for label, start, end in REGIMES:
        m = metrics_for_window(net_ret, start, end, initial_capital)
        rows.append(
            {
                "regime": label,
                "start": start,
                "end": end,
                "cagr": m["cagr"],
                "sharpe": m["sharpe"],
                "max_dd": m["max_dd"],
                "n_days": m["n_days"],
            }
        )
    return pd.DataFrame(rows)


def beta_compliance_table(diagnostics: pd.DataFrame) -> dict:
    ctrl = diagnostics[diagnostics["is_control_date"]].copy() if "is_control_date" in diagnostics.columns else diagnostics
    n_total = len(ctrl)
    n_violations = int(ctrl["gate_violation_after"].sum()) if "gate_violation_after" in ctrl.columns else 0
    avg_beta = float(ctrl["beta_after"].mean()) if "beta_after" in ctrl.columns else np.nan
    min_beta = float(ctrl["beta_after"].min()) if "beta_after" in ctrl.columns else np.nan
    max_beta = float(ctrl["beta_after"].max()) if "beta_after" in ctrl.columns else np.nan
    avg_cap = float(ctrl["dynamic_beta_cap"].mean()) if "dynamic_beta_cap" in ctrl.columns else np.nan
    min_cap = float(ctrl["dynamic_beta_cap"].min()) if "dynamic_beta_cap" in ctrl.columns else np.nan
    return {
        "n_rebalance_dates": n_total,
        "n_gate_violations": n_violations,
        "avg_beta_after": avg_beta,
        "min_beta_after": min_beta,
        "max_beta_after": max_beta,
        "avg_dynamic_cap": avg_cap,
        "min_dynamic_cap": min_cap,
        "compliance_rate": (n_total - n_violations) / n_total if n_total > 0 else np.nan,
    }


def phase_b_exit_gates(cost_df: pd.DataFrame, beta_comp: dict, full_metrics: dict) -> pd.DataFrame:
    gates = []

    max_dd = full_metrics.get("max_dd", np.nan)
    gates.append(
        {
            "gate": "MaxDD < 40%",
            "value": f"{max_dd:.2%}" if np.isfinite(max_dd) else "N/A",
            "target": "< −40%",
            "pass": bool(np.isfinite(max_dd) and max_dd > GATE_MAX_DD),
        }
    )

    for bps_target in [50.0, 25.0, 10.0]:
        row = cost_df[cost_df["cost_bps"] == bps_target]
        if row.empty:
            continue
        sharpe = float(row["sharpe"].iloc[0])
        gates.append(
            {
                "gate": f"Sharpe > {GATE_SHARPE_50BPS:.1f} at {int(bps_target)} bps",
                "value": f"{sharpe:.3f}",
                "target": f">= {GATE_SHARPE_50BPS:.2f}",
                "pass": bool(sharpe >= GATE_SHARPE_50BPS),
            }
        )

    row_10 = cost_df[cost_df["cost_bps"] == 10.0]
    if not row_10.empty:
        sharpe_10 = float(row_10["sharpe"].iloc[0])
        gates.append(
            {
                "gate": f"Beats equal-weight Sharpe at 10 bps (EW = {B1_EQUAL_WEIGHT_SHARPE:.3f})",
                "value": f"{sharpe_10:.3f}",
                "target": f">= {B1_EQUAL_WEIGHT_SHARPE:.3f}",
                "pass": bool(sharpe_10 >= B1_EQUAL_WEIGHT_SHARPE),
            }
        )

    gates.append(
        {
            "gate": "Max gross <= 1.5",
            "value": f"{B4_MAX_GROSS:.3f}",
            "target": "<= 1.500",
            "pass": bool(B4_MAX_GROSS <= GATE_MAX_GROSS + 1e-9),
        }
    )

    n_violations = beta_comp["n_gate_violations"]
    gates.append(
        {
            "gate": "Zero rebalance-date beta band violations",
            "value": str(n_violations),
            "target": "0",
            "pass": bool(n_violations == 0),
        }
    )

    gates.append(
        {
            "gate": "Turnover stable (sum <= 90)",
            "value": f"{B4_TURNOVER:.2f}",
            "target": "<= 90.0",
            "pass": bool(B4_TURNOVER <= 90.0),
        }
    )

    return pd.DataFrame(gates)


def render_report(
    full_metrics: dict,
    cost_df: pd.DataFrame,
    regime_df: pd.DataFrame,
    beta_comp: dict,
    gates_df: pd.DataFrame,
) -> str:
    all_pass = bool(gates_df["pass"].all())
    verdict = "PASS — proceed to Phase C" if all_pass else "FAIL — address failing gates before Phase C"

    attr_df = pd.DataFrame(ATTRIBUTION_CHAIN)

    lines = [
        "# Phase B.5 — Final Phase B Gate Run",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Candidate: `b4_stress_cap_trend_boost` (Phase B.4 promoted).",
        "- Universe: sp500, clipped to `2026-04-24`, evaluation window 2008–2026.",
        "- Cost at reporting: 10 bps (cost sweep at 10/25/50 bps below).",
        "- Scope: no `volatility_score` changes, no new alpha, RL disabled.",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    lines += ["## Phase B Exit Gates", ""]
    lines.append(gates_df[["gate", "value", "target", "pass"]].to_markdown(index=False))
    lines.append("")

    lines += [
        "## Full-Period Performance (10 bps)",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| CAGR | {full_metrics.get('cagr', np.nan):.2%} |",
        f"| Sharpe | {full_metrics.get('sharpe', np.nan):.3f} |",
        f"| MaxDD | {full_metrics.get('max_dd', np.nan):.2%} |",
        f"| Max gross | {full_metrics.get('max_target_gross', np.nan):.3f} |",
        f"| Turnover sum | {full_metrics.get('turnover_sum', np.nan):.2f} |",
        f"| Min selected names | {full_metrics.get('min_selected', np.nan)} |",
        "",
    ]

    lines += ["## Cost Sensitivity", ""]
    lines.append(cost_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Regime Breakdown (10 bps)", ""]
    lines.append(regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")
    lines += [
        "Notes:",
        "- 2008 and 2022 Sharpe are expected to be below 1.0 (confirmed from B.3.1/B.4 history); treat as capital-preservation regimes.",
        "- MaxDD gate applies full-period only.",
        "",
    ]

    lines += ["## Beta Compliance (rebalance dates)", ""]
    for k, v in beta_comp.items():
        lines.append(f"- {k}: {v:.4f}" if isinstance(v, float) else f"- {k}: {v}")
    lines.append("")

    lines += ["## Phase B Attribution Chain", ""]
    attr_display = attr_df.copy()
    attr_display["cagr"] = attr_display["cagr"].apply(lambda x: f"{x:.2%}")
    attr_display["sharpe"] = attr_display["sharpe"].apply(lambda x: f"{x:.3f}")
    attr_display["max_dd"] = attr_display["max_dd"].apply(lambda x: f"{x:.2%}")
    attr_display["turnover"] = attr_display["turnover"].apply(
        lambda x: f"{x:.1f}" if x is not None else "—"
    )
    lines.append(attr_display[["step", "cagr", "sharpe", "max_dd", "turnover", "note"]].to_markdown(index=False))
    lines.append("")

    if all_pass:
        lines += [
            "## Decision",
            "",
            "- All Phase B exit criteria pass.",
            f"- Candidate `b4_stress_cap_trend_boost`: CAGR `{B4_CAGR:.2%}`, Sharpe `{B4_SHARPE:.3f}`, MaxDD `{B4_MAX_DD:.2%}`, turnover `{B4_TURNOVER:.2f}`, avg dynamic beta cap `{B4_AVG_DYNAMIC_CAP:.3f}` (min `{B4_MIN_DYNAMIC_CAP:.3f}`).",
            "- Proceed to Phase C — model refinement: LightGBM tuning and feature improvements.",
            "",
        ]
    else:
        failing = gates_df[~gates_df["pass"]]["gate"].tolist()
        lines += [
            "## Decision",
            "",
            f"- FAIL: the following gates did not pass: {', '.join(failing)}.",
            "- Do not proceed to Phase C. Identify and address failing gates, then re-run B.5.",
            "",
        ]

    lines += [
        "## Output Files",
        "",
        "- `artifacts/reports/phase_b5_final_gate.md`",
        "- `artifacts/reports/phase_b5_cost_sensitivity.csv`",
        "- `artifacts/reports/phase_b5_regime_breakdown.csv`",
        "- `artifacts/reports/phase_b5_attribution.csv`",
        "- `artifacts/reports/phase_b5_beta_compliance.csv`",
    ]
    return "\n".join(lines) + "\n"


def run_universe(
    config_path: str,
    universe_path: str,
    trend_assets: list[str],
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    validation_end = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    logger.info(
        "Phase B.5 final gate for %s through %s",
        inputs["universe_config"].name,
        validation_end.date(),
    )

    t0 = time.perf_counter()
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)
    logger.info("Built beta/stress frames in %.1fs", time.perf_counter() - t0)

    t1 = time.perf_counter()
    constrained, diagnostics, control_dates = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("Built promoted weights in %.1fs", time.perf_counter() - t1)

    # Full-period metrics at 10 bps via simulator
    t2 = time.perf_counter()
    full_metrics = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant("b4_stress_cap_trend_boost", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    logger.info(
        "Full-period: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%% in %.1fs",
        full_metrics["cagr"] * 100,
        full_metrics["sharpe"],
        full_metrics["max_dd"] * 100,
        time.perf_counter() - t2,
    )

    # Realized beta overlay on diagnostics
    dates = constrained.index[constrained.index <= validation_end]
    executable = constrained.reindex(dates).fillna(0.0).shift(1).fillna(0.0)
    returns = (
        inputs["prices"]
        .pct_change()
        .fillna(0.0)
        .reindex(index=dates, columns=executable.columns)
        .fillna(0.0)
    )
    turnover_series = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover_series.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    net_ret = (1.0 - turnover_series * B1_COST_BPS / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0
    spy_ret = inputs["prices"][inputs["universe_config"].benchmark].pct_change().reindex(dates)
    realized = realized_beta(net_ret, spy_ret)
    if "date" in diagnostics.columns:
        diagnostics["realized_beta_63d"] = realized.reindex(diagnostics["date"]).values

    # Cost sensitivity
    cost_df = cost_sensitivity_table(inputs, constrained, validation_end)
    logger.info("Cost sensitivity: %s", cost_df[["cost_bps", "sharpe"]].to_dict("records"))

    # Regime breakdown
    regime_df = regime_breakdown_table(inputs, constrained, validation_end)
    logger.info("Regime breakdown done")

    # Beta compliance
    beta_comp = beta_compliance_table(diagnostics)
    logger.info(
        "Beta compliance: %d dates, %d violations, avg beta %.3f",
        beta_comp["n_rebalance_dates"],
        beta_comp["n_gate_violations"],
        beta_comp["avg_beta_after"],
    )

    # Phase B exit gates
    gates_df = phase_b_exit_gates(cost_df, beta_comp, full_metrics)
    for _, row in gates_df.iterrows():
        status = "PASS" if row["pass"] else "FAIL"
        logger.info("Gate [%s] %s: %s (target %s)", status, row["gate"], row["value"], row["target"])

    return full_metrics, cost_df, regime_df, beta_comp, gates_df


def main():
    parser = argparse.ArgumentParser(description="Phase B.5 final Phase B gate run")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    full_metrics, cost_df, regime_df, beta_comp, gates_df = run_universe(
        args.config, args.universe, args.trend_assets
    )

    cost_df.to_csv(reports_dir / "phase_b5_cost_sensitivity.csv", index=False)
    regime_df.to_csv(reports_dir / "phase_b5_regime_breakdown.csv", index=False)
    pd.DataFrame(ATTRIBUTION_CHAIN).to_csv(reports_dir / "phase_b5_attribution.csv", index=False)
    pd.DataFrame([beta_comp]).to_csv(reports_dir / "phase_b5_beta_compliance.csv", index=False)
    (reports_dir / "phase_b5_final_gate.md").write_text(
        render_report(full_metrics, cost_df, regime_df, beta_comp, gates_df)
    )
    logger.info("Phase B.5 artifacts saved to %s", reports_dir)

    all_pass = bool(gates_df["pass"].all())
    if all_pass:
        logger.info("Phase B.5 PASS — all exit criteria met. Ready for Phase C.")
    else:
        failing = gates_df[~gates_df["pass"]]["gate"].tolist()
        logger.warning("Phase B.5 FAIL — gates not met: %s", failing)


if __name__ == "__main__":
    main()
