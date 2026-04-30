import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_3_membership_coverage_artifacts import active_matrix, load_inputs  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASELINE_COHORT = "baseline_current_mask"


def data_window_row(config_path: str, universe_path: str, trend_assets: list[str]) -> dict:
    inputs = load_inputs(config_path, universe_path, trend_assets)
    active = active_matrix(inputs)
    active_counts = active.sum(axis=1)
    nonzero = active_counts[active_counts > 0]
    prices = inputs["prices"]
    last_price_date = pd.Timestamp(prices.index.max()) if not prices.empty else pd.NaT
    last_nonzero_active_date = pd.Timestamp(nonzero.index.max()) if not nonzero.empty else pd.NaT
    zero_active_dates = active_counts[active_counts == 0]
    trailing_zero_dates = zero_active_dates[zero_active_dates.index > last_nonzero_active_date] if not pd.isna(last_nonzero_active_date) else zero_active_dates
    recommended_end = min(last_price_date, last_nonzero_active_date) if not pd.isna(last_nonzero_active_date) else last_price_date
    return {
        "universe_path": universe_path,
        "universe": inputs["universe_config"].name,
        "configured_tickers": len(inputs["universe_config"].tickers),
        "first_price_date": pd.Timestamp(prices.index.min()).date().isoformat(),
        "last_price_date": last_price_date.date().isoformat(),
        "first_mask_date": pd.Timestamp(active.index.min()).date().isoformat(),
        "last_mask_eval_date": pd.Timestamp(active.index.max()).date().isoformat(),
        "last_nonzero_active_date": last_nonzero_active_date.date().isoformat() if not pd.isna(last_nonzero_active_date) else "",
        "recommended_validation_end": recommended_end.date().isoformat(),
        "zero_active_days": int((active_counts == 0).sum()),
        "trailing_zero_active_days": int(len(trailing_zero_dates)),
        "active_min_nonzero": int(nonzero.min()) if not nonzero.empty else 0,
        "active_median": float(active_counts.median()),
        "active_latest": int(active_counts.iloc[-1]) if not active_counts.empty else 0,
        "needs_clip_or_mask_refresh": bool(len(trailing_zero_dates) > 0),
    }


def baseline_lock_rows() -> pd.DataFrame:
    path = Path("artifacts/reports/artifact_sensitivity.csv")
    if not path.exists():
        raise FileNotFoundError("A.7.3 artifact_sensitivity.csv is required before B.0")
    sensitivity = pd.read_csv(path)
    rows = sensitivity[sensitivity["cohort"] == BASELINE_COHORT].copy()
    keep = [
        "universe",
        "cohort",
        "cagr",
        "sharpe",
        "max_dd",
        "volatility",
        "turnover_sum",
        "avg_gross",
        "max_gross",
        "avg_candidates",
        "min_candidates",
        "avg_score_non_null",
        "min_score_non_null",
        "avg_selected",
        "min_selected",
        "passes_drawdown",
        "passes_sharpe",
        "passes_selection_depth",
    ]
    return rows[[c for c in keep if c in rows.columns]]


def render_report(window: pd.DataFrame, baseline: pd.DataFrame) -> str:
    needs_action = bool(window["needs_clip_or_mask_refresh"].any()) if not window.empty else True
    lines = [
        "# Phase B.0 Baseline Guard",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "- Purpose: lock the Phase A.7.3 baseline before Phase B portfolio stabilization.",
        "- Baseline expression: `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.",
        "- Scope: no `volatility_score` changes, no new alpha, no historical membership import, RL disabled.",
        "",
        "## Baseline Lock",
        "",
        baseline.to_markdown(index=False, floatfmt=".4f") if not baseline.empty else "No baseline rows.",
        "",
        "## Data Window Guard",
        "",
        window.to_markdown(index=False, floatfmt=".4f") if not window.empty else "No data-window rows.",
        "",
        "## Decision",
        "",
    ]
    if needs_action:
        lines.append("- WATCH: Phase B can proceed, but production validation must clip to `recommended_validation_end` or refresh the PIT mask before using trailing dates.")
    else:
        lines.append("- PASS: no data-window clipping required before Phase B production validation.")
    lines.extend(
        [
            "- Use these baseline rows as the comparison anchor for all Phase B turnover, optimizer, and risk-engine experiments.",
            "",
            "## Output Files",
            "",
            "- `artifacts/reports/phase_b0_baseline_guard.md`",
            "- `artifacts/reports/phase_b0_data_window_guard.csv`",
            "- `artifacts/reports/phase_b0_baseline_lock.csv`",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run Phase B.0 baseline and data-window guard")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universes", nargs="+", default=["config/universes/sp100.yaml", "config/universes/sp500.yaml"])
    parser.add_argument("--trend-assets", nargs="+", default=["SPY", "TLT", "GLD", "UUP"])
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    window = pd.DataFrame([data_window_row(args.config, universe, args.trend_assets) for universe in args.universes])
    baseline = baseline_lock_rows()
    window.to_csv(reports_dir / "phase_b0_data_window_guard.csv", index=False)
    baseline.to_csv(reports_dir / "phase_b0_baseline_lock.csv", index=False)
    (reports_dir / "phase_b0_baseline_guard.md").write_text(render_report(window, baseline))
    logger.info("Saved Phase B.0 baseline guard artifacts to %s", reports_dir)


if __name__ == "__main__":
    main()
