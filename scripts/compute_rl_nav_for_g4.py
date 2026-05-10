"""Pre-compute RL NAV series for Phase G.4 switching rule.

Run this once per data refresh (e.g., monthly) or when RL checkpoint changes.

Saves to: data/switching/nav_rl_backtest.parquet

Usage
-----
.venv/bin/python scripts/compute_rl_nav_for_g4.py
.venv/bin/python scripts/compute_rl_nav_for_g4.py --start-date 2019-01-01 --end-date 2026-04-24
.venv/bin/python scripts/compute_rl_nav_for_g4.py --model-path artifacts/production/rl_e7_clean_promoted.zip
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
from run_phase_b5_final_gate import build_promoted_weights
from src.rl.nav_generator import generate_rl_nav_on_demand

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = REPO_ROOT / "data" / "switching"
OUTPUT_FILE = OUTPUT_DIR / "nav_rl_backtest.parquet"
DEFAULT_MODEL = REPO_ROOT / "artifacts" / "production" / "rl_e7_clean_promoted.zip"


def main():
    parser = argparse.ArgumentParser(description="Pre-compute RL NAV for G.4 switching rule")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--start-date", default="2019-01-01",
                        help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None,
                        help="Backtest end date (YYYY-MM-DD, defaults to max available)")
    parser.add_argument("--model-path", default=None,
                        help="Path to RL checkpoint (defaults to production E.7)")
    parser.add_argument("--cost-bps", type=float, default=10.0,
                        help="Transaction cost in basis points")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # Use default model if not specified
    model_path = Path(args.model_path) if args.model_path else DEFAULT_MODEL
    if not model_path.exists():
        logger.error("RL model not found at %s", model_path)
        return 1

    logger.info("=" * 80)
    logger.info("Phase G.4 — RL NAV Backtest Generation")
    logger.info("=" * 80)
    logger.info("Model: %s", model_path)
    logger.info("Start: %s", args.start_date)
    logger.info("End: %s", args.end_date or "max available")
    logger.info("Cost: %.1f bps", args.cost_bps)
    logger.info("")

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

    # Load sector features (required for RL environment)
    sector_features_path = REPO_ROOT / "data" / "features" / "sector_features.parquet"
    if not sector_features_path.exists():
        logger.error("Sector features not found at %s", sector_features_path)
        logger.error("Run Phase E training script first to generate sector features")
        return 1

    logger.info("Loading sector features from %s", sector_features_path)
    sector_features_df = pd.read_parquet(sector_features_path)

    # Generate RL NAV
    logger.info("")
    logger.info("Generating RL NAV via full episode (this may take 1-2 minutes) …")
    nav_rl = generate_rl_nav_on_demand(
        inputs=inputs,
        b5_weights_df=b5_weights_df,
        sector_features_df=sector_features_df,
        start_date=args.start_date,
        end_date=str(validation_end.date()),
        model_path=model_path,
        cost_bps=args.cost_bps,
    )

    logger.info(
        "RL NAV computed: %d records, %.2f → %.2f (%.1f%% total return)",
        len(nav_rl),
        float(nav_rl.iloc[0]),
        float(nav_rl.iloc[-1]),
        (float(nav_rl.iloc[-1]) / float(nav_rl.iloc[0]) - 1.0) * 100,
    )

    # Save to parquet
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nav_df = nav_rl.reset_index()
    nav_df.columns = ["as_of_date", "nav"]
    nav_df.to_parquet(OUTPUT_FILE, index=False)

    logger.info("RL NAV saved to %s (%.1fs)", OUTPUT_FILE, time.perf_counter() - t0)
    logger.info("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
