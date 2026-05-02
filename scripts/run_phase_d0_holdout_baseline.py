"""Phase D.0 — Measure B.5 holdout baseline on 2019-01-01 → 2026-04-24.

Reuses build_promoted_weights from run_phase_b5_final_gate.py verbatim.
Produces phase_d0_holdout_baseline.md as the RL promotion benchmark.
"""
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

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b2_turnover_control import B1_COST_BPS, COST_BPS
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import (
    build_promoted_weights,
    compute_net_returns,
)
from src.reporting.metrics import calculate_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HOLDOUT_START = "2019-01-01"
HOLDOUT_END = "2026-04-24"

# Regime windows within the holdout only
HOLDOUT_REGIMES = [
    ("2019 bull market", "2019-01-01", "2019-12-31"),
    ("2020 COVID crash", "2020-01-01", "2020-12-31"),
    ("2021 recovery", "2021-01-01", "2021-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("2023–2026 recovery", "2023-01-01", "2026-04-24"),
    ("full holdout 2019–2026", "2019-01-01", "2026-04-24"),
]

# Promotion benchmark (from Phase B.5 full-period evaluation, sp500, 10 bps)
B5_FULL_SHARPE = 1.078
B5_FULL_MAXDD = -0.3298


def _metrics_for_window(net_returns: pd.Series, start: str, end: str) -> dict:
    mask = (net_returns.index >= pd.Timestamp(start)) & (
        net_returns.index <= pd.Timestamp(end)
    )
    sliced = net_returns[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod()
    m = calculate_metrics(nav)
    return {
        "cagr": m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def holdout_cost_sensitivity(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> pd.DataFrame:
    rows = []
    for bps in COST_BPS:
        full_net_ret = compute_net_returns(inputs, constrained, validation_end, bps)
        m = _metrics_for_window(full_net_ret, HOLDOUT_START, HOLDOUT_END)
        rows.append(
            {
                "cost_bps": bps,
                "cagr": m["cagr"],
                "sharpe": m["sharpe"],
                "max_dd": m["max_dd"],
            }
        )
    return pd.DataFrame(rows)


def holdout_regime_breakdown(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> pd.DataFrame:
    full_net_ret = compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    rows = []
    for label, start, end in HOLDOUT_REGIMES:
        m = _metrics_for_window(full_net_ret, start, end)
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


def render_report(
    holdout_metrics: dict,
    cost_df: pd.DataFrame,
    regime_df: pd.DataFrame,
) -> str:
    lines = [
        "# Phase D.0 — B.5 Holdout Baseline",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- System: `b4_stress_cap_trend_boost` (B.5 promoted)",
        f"- Universe: sp500",
        f"- Holdout window: {HOLDOUT_START} → {HOLDOUT_END}",
        f"- Cost at reporting: {B1_COST_BPS} bps (sweep at 10/25/50 bps below)",
        "",
        "## Purpose",
        "",
        "This report establishes the B.5 benchmark numbers on the **holdout window only**.",
        "The full-period Sharpe (1.078) is known from Phase B.5. This report measures the",
        "same system on the 2019–2026-04-24 slice that RL will be evaluated on in D.6.",
        "Any RL promotion comparison must use these numbers, not the full-period ones.",
        "",
        "## Holdout Performance (10 bps)",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| CAGR | {holdout_metrics['cagr']:.2%} |",
        f"| Sharpe | {holdout_metrics['sharpe']:.3f} |",
        f"| MaxDD | {holdout_metrics['max_dd']:.2%} |",
        f"| N days | {holdout_metrics['n_days']} |",
        "",
        "## Cost Sensitivity (holdout window only)",
        "",
    ]
    lines.append(cost_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Regime Breakdown (10 bps, holdout sub-windows)", ""]
    lines.append(regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += [
        "## RL Promotion Benchmarks",
        "",
        f"The following numbers are the B.5 **holdout** reference for D.6 promotion decisions:",
        "",
        f"| Metric | Holdout value | D.6 Path A gate | D.6 Path B gate |",
        f"|---|---|---|---|",
    ]
    h_sharpe = holdout_metrics["sharpe"]
    h_maxdd = holdout_metrics["max_dd"]
    path_a_sharpe = h_sharpe  # RL must match or beat holdout Sharpe
    path_b_sharpe = h_sharpe - 0.03
    path_a_maxdd = h_maxdd
    path_b_maxdd = h_maxdd + 0.015  # materially better (less negative)
    cost_50bps = cost_df[cost_df["cost_bps"] == 50.0]
    sharpe_50bps = float(cost_50bps["sharpe"].iloc[0]) if not cost_50bps.empty else np.nan
    lines += [
        f"| Sharpe (10 bps) | {h_sharpe:.3f} | ≥ {path_a_sharpe:.3f} | ≥ {path_b_sharpe:.3f} |",
        f"| MaxDD | {h_maxdd:.2%} | ≥ {path_a_maxdd:.2%} | ≥ {path_b_maxdd:.2%} |",
        f"| Sharpe (50 bps) | {sharpe_50bps:.3f} | ≥ 0.900 | ≥ 0.900 |",
        "",
        "> **Note:** Path A = clear Sharpe win (≥ B.5 holdout Sharpe AND MaxDD ≥ B.5 holdout MaxDD).",
        "> Path B = tail improvement (Sharpe ≥ B.5 − 0.03 AND MaxDD at least 1.5pp better).",
        "> Both paths require: 50 bps Sharpe ≥ 0.90, beats RL no-op, beats random bounded (50 seeds).",
        "",
        "## Notes",
        "",
        "- Full-period B.5 Sharpe (2008–2026, 10 bps): 1.078 — higher than holdout Sharpe",
        "  because 2008 crisis weights the full period; the holdout starts in 2019 (benign)",
        "  and includes 2020 COVID and 2022 bear. These are the hard regimes RL must navigate.",
        "- Holdout metrics are the apples-to-apples benchmark for D.6.",
        "- Do not use full-period B.5 metrics as D.6 comparison numbers.",
        "",
        "## Artifacts",
        "",
        "- `artifacts/reports/phase_d0_holdout_baseline.md` — this file",
        "- `artifacts/reports/d0_cost_sensitivity.csv`",
        "- `artifacts/reports/d0_regime_breakdown.csv`",
    ]
    return "\n".join(lines) + "\n"


def main():
    config_path = "config/base.yaml"
    universe_path = "config/universes/sp500.yaml"
    out_dir = REPO_ROOT / "artifacts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    inputs = load_inputs(config_path, universe_path, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    logger.info("Loaded inputs; validation_end=%s", validation_end.date())

    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)
    logger.info("Built beta/stress in %.1fs", time.perf_counter() - t0)

    t1 = time.perf_counter()
    constrained, _diagnostics, _control_dates = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("Built B.5 weights in %.1fs", time.perf_counter() - t1)

    t2 = time.perf_counter()
    full_net_ret = compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    holdout_metrics = _metrics_for_window(full_net_ret, HOLDOUT_START, HOLDOUT_END)
    logger.info(
        "Holdout CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%% in %.1fs",
        holdout_metrics["cagr"] * 100,
        holdout_metrics["sharpe"],
        holdout_metrics["max_dd"] * 100,
        time.perf_counter() - t2,
    )

    cost_df = holdout_cost_sensitivity(inputs, constrained, validation_end)
    regime_df = holdout_regime_breakdown(inputs, constrained, validation_end)

    cost_df.to_csv(out_dir / "d0_cost_sensitivity.csv", index=False)
    regime_df.to_csv(out_dir / "d0_regime_breakdown.csv", index=False)
    logger.info("Saved CSVs")

    report = render_report(holdout_metrics, cost_df, regime_df)
    (out_dir / "phase_d0_holdout_baseline.md").write_text(report)
    logger.info("Wrote phase_d0_holdout_baseline.md")
    logger.info("Total time: %.1fs", time.perf_counter() - t0)


if __name__ == "__main__":
    main()
