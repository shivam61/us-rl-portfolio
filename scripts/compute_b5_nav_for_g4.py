"""Pre-compute B.5 NAV series for Phase G.4 switching rule.

Run this once per data refresh (e.g., monthly) or when B.5 construction changes.

Saves to: data/switching/nav_b5_backtest.parquet

Usage
-----
.venv/bin/python scripts/compute_b5_nav_for_g4.py
.venv/bin/python scripts/compute_b5_nav_for_g4.py --start-date 2019-01-01 --end-date 2026-04-24
"""
import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (REPO_ROOT, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import build_promoted_weights, compute_net_returns, B1_COST_BPS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = REPO_ROOT / "data" / "switching"
OUTPUT_FILE = OUTPUT_DIR / "nav_b5_backtest.parquet"


def main():
    parser = argparse.ArgumentParser(description="Pre-compute B.5 NAV for G.4 switching rule")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--start-date", default=None,
                        help="Override backtest start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None,
                        help="Override backtest end date (YYYY-MM-DD)")
    args = parser.parse_args()

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)

    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name,
        inputs["prices"].index.max()
    )
    if args.end_date:
        validation_end = pd.Timestamp(args.end_date)

    logger.info("Building beta / stress …")
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 promoted weights …")
    b5_weights_df, _, _ = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )

    logger.info("Computing net returns (cost_bps=%.1f) …", B1_COST_BPS)
    net_ret = compute_net_returns(
        inputs, b5_weights_df, validation_end, B1_COST_BPS
    )

    # Convert to NAV series
    initial_capital = inputs["base_config"].portfolio.initial_capital
    nav_b5 = (1.0 + net_ret).cumprod() * initial_capital

    # Filter by start_date if provided
    if args.start_date:
        start_ts = pd.Timestamp(args.start_date)
        nav_b5 = nav_b5[nav_b5.index >= start_ts]

    logger.info(
        "B.5 NAV computed: %d records, %.2f → %.2f (%.1f%% total return)",
        len(nav_b5),
        float(nav_b5.iloc[0]),
        float(nav_b5.iloc[-1]),
        (float(nav_b5.iloc[-1]) / float(nav_b5.iloc[0]) - 1.0) * 100,
    )

    # Save to parquet
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nav_df = nav_b5.reset_index()
    nav_df.columns = ["as_of_date", "nav"]
    nav_df.to_parquet(OUTPUT_FILE, index=False)

    logger.info("B.5 NAV saved to %s (%.1fs)", OUTPUT_FILE, time.perf_counter() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
