import argparse
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_1_drawdown_control import TREND_NAME, stress_frame  # noqa: E402
from run_phase_a7_2_robustness import stress_variant_frame  # noqa: E402
from run_phase_a7_trend_overlay import TREND_ASSETS, build_trend_weight_paths, load_inputs  # noqa: E402
from run_phase_b1_simulator_reproduction import (  # noqa: E402
    MAX_GROSS_LIMIT,
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (  # noqa: E402
    B1_COST_BPS,
    Variant,
    apply_execution_controls,
    build_vol_path_fast,
    candidate_weights_with_persistence,
    run_execution_simulator,
    signal_dates_for_frequency,
)
from run_phase_b3_exposure_control import (  # noqa: E402
    ExposureVariant,
    apply_exposure_constraints,
    build_b2_candidate,
    portfolio_beta,
    project_weights,
    realized_beta,
    rolling_beta_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# B.3.1 promoted policy reference metrics (b3_band_50_90, sp500, clipped to 2026-04-24)
B3_1_CAGR = 0.164900
B3_1_SHARPE = 1.075000
B3_1_MAX_DD = -0.336900
B3_1_TURNOVER = 85.360000
B3_1_MAX_GROSS = 1.500000

# B.4 dynamic beta-cap parameters
BETA_MIN = 0.50          # keep B.3.1 floor — do not introduce lower beta floor
BETA_MAX_BASE = 0.90     # cap at zero stress (same as B.3.1 upper bound)
BETA_MAX_SENSITIVITY = 0.20  # beta_cap = 0.9 - 0.2 * stress_score

# Optional trend scaling parameters
TREND_STRESS_THRESHOLD = 0.50   # start boosting trend when stress > 0.5
TREND_STRESS_SCALE_MAX = 0.10   # max trend boost fraction (+10%) at stress = 1.0

# B.4 success gates (relative to B.3.1)
GATE_SHARPE_DROP = 0.05
GATE_CAGR_DROP = 0.01

# Non-benchmark trend assets (SPY excluded; it is the benchmark and beta-floor vehicle)
_NON_BENCHMARK_TREND = [t for t in TREND_ASSETS if t != "SPY"]


@dataclass(frozen=True)
class B4Variant:
    name: str
    beta_min: float = BETA_MIN
    beta_max_base: float = BETA_MAX_BASE
    beta_max_sensitivity: float = BETA_MAX_SENSITIVITY
    trend_stress_boost: bool = False
    trend_stress_threshold: float = TREND_STRESS_THRESHOLD
    trend_stress_scale_max: float = TREND_STRESS_SCALE_MAX

    def beta_max_at_stress(self, stress: float) -> float:
        raw = self.beta_max_base - self.beta_max_sensitivity * float(np.clip(stress, 0.0, 1.0))
        return float(np.clip(raw, self.beta_min + 0.01, self.beta_max_base))


def build_stress_series(inputs: dict) -> pd.Series:
    base = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    sv = stress_variant_frame(base, "weighted_50_50", 0.5, 0.5)
    return sv["stress_score"]


def apply_trend_scaling(
    target_weights: pd.DataFrame,
    stress_series: pd.Series,
    control_dates: list[pd.Timestamp],
    trend_tickers: list[str],
    threshold: float,
    max_scale: float,
) -> pd.DataFrame:
    """Boost non-benchmark trend ticker weights on high-stress rebalance dates."""
    if max_scale <= 0 or not trend_tickers:
        return target_weights

    scaled = target_weights.copy()
    stress_aligned = stress_series.reindex(scaled.index).fillna(0.0)
    range_size = max(1.0 - threshold, 1e-9)

    for date in control_dates:
        if date not in scaled.index:
            continue
        s = float(stress_aligned.get(date, 0.0))
        if s <= threshold:
            continue
        boost = 1.0 + max_scale * (s - threshold) / range_size
        row = scaled.loc[date].copy()
        active_trend = [t for t in trend_tickers if t in row.index and abs(row.get(t, 0.0)) > 1e-12]
        if not active_trend:
            continue
        for t in active_trend:
            row[t] = row[t] * boost
        new_gross = float(row.abs().sum())
        if new_gross > MAX_GROSS_LIMIT:
            row = row * (MAX_GROSS_LIMIT / new_gross)
        scaled.loc[date] = row

    return scaled


def apply_b4_constraints(
    target_weights: pd.DataFrame,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    variant: B4Variant,
    control_dates: list[pd.Timestamp],
    benchmark: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply stress-aware dynamic beta cap on rebalance dates."""
    rows = []
    diagnostics = []
    current = pd.Series(dtype=float)
    control_set = set(control_dates)
    stress_aligned = stress_series.reindex(target_weights.index).fillna(0.0)

    for date, row in target_weights.iterrows():
        is_control_date = date in control_set
        weights = row[row.abs() > 1e-12]
        gross_before = float(weights.abs().sum())
        beta_before = portfolio_beta(weights, beta_frame.loc[date]) if date in beta_frame.index else np.nan

        stress_val = float(stress_aligned.get(date, 0.0))
        dynamic_beta_max = variant.beta_max_at_stress(stress_val)

        if is_control_date:
            ev = ExposureVariant(
                name=f"_b4_dynamic_{variant.name}",
                beta_min=variant.beta_min,
                beta_max=dynamic_beta_max,
                beta_tolerance=0.0,
                allow_spy_floor=True,
            )
            current, scale, overlay, reason = project_weights(
                weights,
                beta_frame.loc[date],
                benchmark=benchmark,
                variant=ev,
            )
        else:
            scale, overlay, reason = 1.0, 0.0, "held"

        gross_after = float(current.abs().sum())
        beta_after = portfolio_beta(current, beta_frame.loc[date]) if date in beta_frame.index else np.nan

        beta_violation_after = False
        gate_violation_after = False
        if is_control_date and np.isfinite(beta_after) and gross_after > 1e-12:
            beta_violation_after = beta_after > dynamic_beta_max + 1e-6 or beta_after < variant.beta_min - 1e-6
            gate_violation_after = gross_after > MAX_GROSS_LIMIT + 1e-9 or beta_violation_after

        rows.append(current.rename(date))
        diagnostics.append(
            {
                "date": date,
                "variant": variant.name,
                "is_control_date": is_control_date,
                "stress_score": stress_val,
                "dynamic_beta_cap": dynamic_beta_max if is_control_date else np.nan,
                "beta_min": variant.beta_min,
                "gross_before": gross_before,
                "gross_after": gross_after,
                "beta_before": beta_before,
                "beta_after": beta_after,
                "scale": scale,
                "spy_overlay": overlay,
                "projection_reason": reason,
                "gross_violation_before": gross_before > MAX_GROSS_LIMIT + 1e-9,
                "gross_violation_after": gross_after > MAX_GROSS_LIMIT + 1e-9,
                "beta_violation_after": beta_violation_after,
                "gate_violation_after": gate_violation_after,
            }
        )

    return pd.DataFrame(rows).fillna(0.0), pd.DataFrame(diagnostics)


def evaluate_b4_variant(
    inputs: dict,
    validation_end: pd.Timestamp,
    base_weights: pd.DataFrame,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    variant: B4Variant,
    control_dates: list[pd.Timestamp],
) -> tuple[dict, pd.DataFrame]:
    weights_in = base_weights

    if variant.trend_stress_boost:
        trend_tickers = [t for t in _NON_BENCHMARK_TREND if t in base_weights.columns]
        weights_in = apply_trend_scaling(
            base_weights,
            stress_series,
            control_dates,
            trend_tickers,
            variant.trend_stress_threshold,
            variant.trend_stress_scale_max,
        )

    constrained, diagnostics = apply_b4_constraints(
        weights_in,
        beta_frame,
        stress_series,
        variant,
        control_dates,
        inputs["universe_config"].benchmark,
    )

    metrics = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant(variant.name, update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )

    # Realized beta overlay
    dates = constrained.index[constrained.index <= validation_end]
    executable = constrained.reindex(dates).fillna(0.0).shift(1).fillna(0.0)
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=dates, columns=executable.columns).fillna(0.0)
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    net_ret = (1.0 - turnover * B1_COST_BPS / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0
    spy_ret = inputs["prices"][inputs["universe_config"].benchmark].pct_change().reindex(dates)
    realized = realized_beta(net_ret, spy_ret)
    diagnostics["realized_beta_63d"] = realized.reindex(diagnostics["date"]).values

    n_control_violations = int(diagnostics.loc[diagnostics["is_control_date"], "gate_violation_after"].sum())
    metrics.update(
        {
            "variant": variant.name,
            "beta_min": variant.beta_min,
            "beta_max_base": variant.beta_max_base,
            "beta_max_sensitivity": variant.beta_max_sensitivity,
            "trend_stress_boost": variant.trend_stress_boost,
            "avg_dynamic_cap": float(
                diagnostics.loc[diagnostics["is_control_date"], "dynamic_beta_cap"].mean()
            ),
            "min_dynamic_cap": float(
                diagnostics.loc[diagnostics["is_control_date"], "dynamic_beta_cap"].min()
            ),
            "avg_beta_before": float(diagnostics["beta_before"].mean()),
            "avg_beta_after": float(diagnostics["beta_after"].mean()),
            "min_beta_after": float(diagnostics["beta_after"].min()),
            "max_beta_after": float(diagnostics["beta_after"].max()),
            "control_gate_violations": n_control_violations,
            "avg_control_scale": float(
                diagnostics.loc[diagnostics["is_control_date"], "scale"].mean()
            ),
            "turnover_vs_b3_1_delta": metrics["turnover_sum"] - B3_1_TURNOVER,
            "sharpe_vs_b3_1_delta": metrics["sharpe"] - B3_1_SHARPE,
            "cagr_vs_b3_1_delta": metrics["cagr"] - B3_1_CAGR,
            "max_dd_vs_b3_1_delta": metrics["max_dd"] - B3_1_MAX_DD,
            "passes_b4": bool(
                n_control_violations == 0
                and metrics["max_target_gross"] <= MAX_GROSS_LIMIT + 1e-9
                and metrics["sharpe"] >= B3_1_SHARPE - GATE_SHARPE_DROP
                and metrics["cagr"] >= B3_1_CAGR - GATE_CAGR_DROP
                and metrics["turnover_sum"] <= B3_1_TURNOVER * 1.05
            ),
        }
    )

    return metrics, diagnostics


def build_b3_1_reference(
    inputs: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    base_weights: pd.DataFrame,
    control_dates: list[pd.Timestamp],
    stress_series: pd.Series,
) -> tuple[dict, pd.DataFrame]:
    """Rebuild B.3.1 b3_band_50_90 as the reference row."""
    ev = ExposureVariant("b3_1_reference", beta_min=0.50, beta_max=0.90, allow_spy_floor=True)
    constrained, diag = apply_exposure_constraints(
        base_weights, beta_frame, ev, control_dates, inputs["universe_config"].benchmark
    )
    metrics = run_execution_simulator(
        inputs,
        constrained,
        validation_end,
        Variant("b3_1_reference", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    dates = constrained.index[constrained.index <= validation_end]
    executable = constrained.reindex(dates).fillna(0.0).shift(1).fillna(0.0)
    returns = inputs["prices"].pct_change().fillna(0.0).reindex(index=dates, columns=executable.columns).fillna(0.0)
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    net_ret = (1.0 - turnover * B1_COST_BPS / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0
    spy_ret = inputs["prices"][inputs["universe_config"].benchmark].pct_change().reindex(dates)
    realized = realized_beta(net_ret, spy_ret)
    diag["realized_beta_63d"] = realized.reindex(diag["date"]).values
    diag["stress_score"] = stress_series.reindex(diag["date"]).values
    diag["dynamic_beta_cap"] = 0.90
    metrics.update(
        {
            "variant": "b3_1_reference",
            "beta_min": 0.50,
            "beta_max_base": 0.90,
            "beta_max_sensitivity": 0.0,
            "trend_stress_boost": False,
            "avg_dynamic_cap": 0.90,
            "min_dynamic_cap": 0.90,
            "avg_beta_before": float(diag["beta_before"].mean()),
            "avg_beta_after": float(diag["beta_after"].mean()),
            "min_beta_after": float(diag["beta_after"].min()),
            "max_beta_after": float(diag["beta_after"].max()),
            "control_gate_violations": int(diag.loc[diag["is_control_date"], "gate_violation_after"].sum()),
            "avg_control_scale": float(diag.loc[diag["is_control_date"], "scale"].mean()),
            "turnover_vs_b3_1_delta": 0.0,
            "sharpe_vs_b3_1_delta": 0.0,
            "cagr_vs_b3_1_delta": 0.0,
            "max_dd_vs_b3_1_delta": 0.0,
            "passes_b4": True,
        }
    )
    return metrics, diag


def render_report(
    summary: pd.DataFrame,
    beta_cap_df: pd.DataFrame,
) -> str:
    passing = summary[summary["passes_b4"]].copy()
    b4_variants = summary[summary["variant"] != "b3_1_reference"].copy()
    lines = [
        "# Phase B.4 — Risk Engine Formalization",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Baseline: B.3.1 `b3_band_50_90` (CAGR `16.49%`, Sharpe `1.075`, MaxDD `-33.69%`, turnover `85.36`).",
        "- Scope: no `volatility_score` changes, no trend-signal changes, no new alpha, RL disabled.",
        "- Method: replace the static B.3.1 beta cap (0.90) with a stress-aware dynamic cap:",
        "  `beta_cap = 0.90 - 0.20 × stress_score`  (range ~0.70 at max stress → 0.90 at zero stress).",
        "  Beta floor held at 0.50; gross ≤ 1.5 preserved.",
        "",
        "## Gates",
        "",
        "- Gross exposure must stay `≤ 1.5`.",
        "- No rebalance-date gate violations.",
        f"- Sharpe drop vs B.3.1 must be `≤ {GATE_SHARPE_DROP:.2f}` (floor {B3_1_SHARPE - GATE_SHARPE_DROP:.3f}).",
        f"- CAGR drop vs B.3.1 must be `≤ {GATE_CAGR_DROP:.1%}` (floor {B3_1_CAGR - GATE_CAGR_DROP:.2%}).",
        "- MaxDD must be improved or unchanged vs B.3.1.",
        f"- Turnover must not increase vs B.3.1 (≤ {B3_1_TURNOVER:.2f} × 1.05 = {B3_1_TURNOVER * 1.05:.2f}).",
        "",
        "## Performance Comparison",
        "",
        summary[
            [
                "variant",
                "cagr",
                "sharpe",
                "max_dd",
                "turnover_sum",
                "max_target_gross",
                "control_gate_violations",
                "avg_dynamic_cap",
                "min_dynamic_cap",
                "cagr_vs_b3_1_delta",
                "sharpe_vs_b3_1_delta",
                "max_dd_vs_b3_1_delta",
                "passes_b4",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Stress-Beta-Cap Dynamics",
        "",
        "Dynamic cap statistics (rebalance dates only):",
        "",
    ]

    cap_stats = (
        beta_cap_df[beta_cap_df["is_control_date"] & beta_cap_df["variant"].str.startswith("b4")]
        .groupby("variant")[["stress_score", "dynamic_beta_cap", "beta_after"]]
        .describe()
    )
    if not cap_stats.empty:
        lines.append(cap_stats.to_string())
    else:
        lines.append("No B.4 control-date diagnostics found.")

    lines += [
        "",
        "## Interpretation",
        "",
    ]

    if passing.empty:
        lines.append("- FAIL: no B.4 variant cleared all gates. Stay at B.3.1 and revise the dynamic cap formula.")
    else:
        b4_passing = passing[passing["variant"] != "b3_1_reference"]
        if b4_passing.empty:
            lines.append("- Only the B.3.1 reference row passed gates; no B.4 improvement confirmed.")
        else:
            best = b4_passing.sort_values(["sharpe", "cagr"], ascending=[False, False]).iloc[0]
            lines.append(
                f"- PASS: `{best['variant']}` — CAGR `{best['cagr']:.2%}`, Sharpe `{best['sharpe']:.3f}`, "
                f"MaxDD `{best['max_dd']:.2%}`, turnover `{best['turnover_sum']:.2f}`, "
                f"avg dynamic cap `{best['avg_dynamic_cap']:.3f}` (min `{best['min_dynamic_cap']:.3f}`)."
            )
            dd_improved = [
                v["variant"]
                for _, v in b4_passing.iterrows()
                if v["max_dd"] >= B3_1_MAX_DD - 1e-4
            ]
            if dd_improved:
                lines.append(f"- MaxDD improved or unchanged in: {', '.join(dd_improved)}.")

    lines += [
        "",
        "## Decision",
        "",
    ]
    b4_pass = passing[passing["variant"] != "b3_1_reference"]
    if b4_pass.empty:
        lines.append(
            "- No B.4 variant improves on B.3.1 within gates. "
            "Consider narrowing sensitivity or adjusting stress threshold before B.5."
        )
    else:
        best = b4_pass.sort_values(["sharpe", "cagr"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- Promote `{best['variant']}` as the Phase B.4 candidate. "
            f"Carry it into B.5 final gate run."
        )

    lines += [
        "",
        "## Output Files",
        "",
        "- `artifacts/reports/phase_b4_risk_engine.md`",
        "- `artifacts/reports/beta_cap_tracking.csv`",
        "- `artifacts/reports/stress_vs_exposure.csv`",
        "- `artifacts/reports/performance_vs_b3_1.csv`",
    ]
    return "\n".join(lines) + "\n"


def run_universe(
    config_path: str,
    universe_path: str,
    trend_assets: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    validation_end = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    logger.info(
        "Phase B.4 risk engine for %s through %s",
        inputs["universe_config"].name,
        validation_end.date(),
    )

    t0 = time.perf_counter()
    base_weights = build_b2_candidate(inputs, validation_end)
    logger.info("Built B.2 candidate in %.1fs", time.perf_counter() - t0)

    target_turnover = base_weights.diff().abs().sum(axis=1)
    if not base_weights.empty:
        target_turnover.iloc[0] = base_weights.iloc[0].abs().sum()
    control_dates = list(target_turnover[target_turnover > 1e-12].index)

    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    # --- B.3.1 reference ---
    ref_metrics, ref_diag = build_b3_1_reference(
        inputs, validation_end, beta_frame, base_weights, control_dates, stress_series
    )

    # --- B.4 variants ---
    b4_variants = [
        B4Variant(
            name="b4_stress_beta_cap",
            beta_min=BETA_MIN,
            beta_max_base=BETA_MAX_BASE,
            beta_max_sensitivity=BETA_MAX_SENSITIVITY,
            trend_stress_boost=False,
        ),
        B4Variant(
            name="b4_stress_cap_trend_boost",
            beta_min=BETA_MIN,
            beta_max_base=BETA_MAX_BASE,
            beta_max_sensitivity=BETA_MAX_SENSITIVITY,
            trend_stress_boost=True,
            trend_stress_threshold=TREND_STRESS_THRESHOLD,
            trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
        ),
    ]

    summaries = [ref_metrics]
    all_diag = [ref_diag]

    for v in b4_variants:
        logger.info("Evaluating B.4 variant: %s", v.name)
        m, d = evaluate_b4_variant(
            inputs, validation_end, base_weights, beta_frame, stress_series, v, control_dates
        )
        summaries.append(m)
        all_diag.append(d)
        logger.info(
            "  %s: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%% turnover=%.2f violations=%d passes=%s",
            v.name,
            m["cagr"] * 100,
            m["sharpe"],
            m["max_dd"] * 100,
            m["turnover_sum"],
            m["control_gate_violations"],
            m["passes_b4"],
        )

    summary_df = pd.DataFrame(summaries)
    diag_all = pd.concat(all_diag, ignore_index=True)

    # beta_cap_tracking: per-date, per-variant diagnostics with stress and dynamic cap
    beta_cap_cols = [
        "date", "variant", "is_control_date", "stress_score", "dynamic_beta_cap",
        "beta_before", "beta_after", "scale", "projection_reason",
        "gross_before", "gross_after", "gate_violation_after", "realized_beta_63d",
    ]
    available = [c for c in beta_cap_cols if c in diag_all.columns]
    beta_cap_tracking = diag_all[available].copy()

    # stress_vs_exposure: control-date view of stress vs portfolio exposure per variant
    sve_cols = ["date", "variant", "stress_score", "dynamic_beta_cap", "beta_after", "gross_after"]
    available_sve = [c for c in sve_cols if c in diag_all.columns]
    stress_vs_exposure = (
        diag_all[diag_all["is_control_date"]][available_sve].copy()
        if "is_control_date" in diag_all.columns
        else diag_all[available_sve].copy()
    )

    # performance_vs_b3_1: tidy comparison table
    compare_cols = [
        "variant", "cagr", "sharpe", "max_dd", "turnover_sum", "max_target_gross",
        "control_gate_violations", "avg_dynamic_cap", "min_dynamic_cap",
        "cagr_vs_b3_1_delta", "sharpe_vs_b3_1_delta", "max_dd_vs_b3_1_delta",
        "turnover_vs_b3_1_delta", "passes_b4",
    ]
    avail_compare = [c for c in compare_cols if c in summary_df.columns]
    performance_vs_b3_1 = summary_df[avail_compare].copy()

    return summary_df, beta_cap_tracking, stress_vs_exposure, performance_vs_b3_1


def main():
    parser = argparse.ArgumentParser(description="Phase B.4 risk engine formalization")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary, beta_cap_tracking, stress_vs_exposure, performance_vs_b3_1 = run_universe(
        args.config, args.universe, args.trend_assets
    )

    performance_vs_b3_1.to_csv(reports_dir / "performance_vs_b3_1.csv", index=False)
    beta_cap_tracking.to_csv(reports_dir / "beta_cap_tracking.csv", index=False)
    stress_vs_exposure.to_csv(reports_dir / "stress_vs_exposure.csv", index=False)
    (reports_dir / "phase_b4_risk_engine.md").write_text(render_report(summary, beta_cap_tracking))
    logger.info("Phase B.4 artifacts saved to %s", reports_dir)


if __name__ == "__main__":
    main()
