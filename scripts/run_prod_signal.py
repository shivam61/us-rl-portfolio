"""Phase G.1 — Production Signal Generation Pipeline.

Runs nightly after market close. Deterministic: same market data → same output.

Outputs
-------
data/allocations/{YYYY-MM-DD}.json   Full allocation for as_of_date
data/allocations/latest.json         Symlink / copy of the most recent allocation
data/prod_state/current_state.json   Tracked portfolio state (equity/trend/cash fracs, NAV)

Output schema
-------------
{
  "as_of_date":        "YYYY-MM-DD",
  "mode":              "rl_e7" | "b5_only",
  "is_rebalance":      bool,
  "equity_frac":       float,
  "trend_frac":        float,
  "cash_frac":         float,
  "stock_weights":     {"TICKER": float, ...},
  "trend_weights":     {"TLT": float, "GLD": float, "UUP": float},
  "rl_state_vector":   [float × 42],
  "rl_raw_action":     [float × 3] | null,
  "stress_score":      float,
  "spy_trend_positive": bool,
  "nav":               float,
  "model_id":          "rl_e7_clean_promoted"
}

Usage
-----
# Rebalance mode (RL active):
    .venv/bin/python scripts/run_prod_signal.py

# B.5-only fallback (no RL):
    .venv/bin/python scripts/run_prod_signal.py --mode b5_only

# Specify date (for backtesting / validation):
    .venv/bin/python scripts/run_prod_signal.py --as-of 2026-04-24

# Force rebalance regardless of cadence:
    .venv/bin/python scripts/run_prod_signal.py --force-rebalance

# Dry run (compute but do not write):
    .venv/bin/python scripts/run_prod_signal.py --dry-run
"""
import argparse
import json
import logging
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (REPO_ROOT, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from stable_baselines3 import PPO

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from src.rl.audit_trail import append_decision
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import (
    BETA_MAX_BASE, BETA_MAX_SENSITIVITY, BETA_MIN,
    TREND_STRESS_SCALE_MAX, TREND_STRESS_THRESHOLD,
    B4Variant, _NON_BENCHMARK_TREND, apply_b4_constraints, build_stress_series,
)
from src.rl.environment_v2 import _initial_trend_frac
from src.rl.exposure_mix import apply_exposure_mix
from src.rl.state_builder_v2 import build_state_v2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────
PRODUCTION_MODEL     = REPO_ROOT / "artifacts" / "production" / "rl_e7_clean_promoted.zip"
ALLOCATIONS_DIR      = REPO_ROOT / "data" / "allocations"
PROD_STATE_DIR       = REPO_ROOT / "data" / "prod_state"
CURRENT_STATE_FILE   = PROD_STATE_DIR / "current_state.json"
SECTOR_FEATURES_PATH = REPO_ROOT / "data" / "features" / "sector_features.parquet"

# ── Rebalance cadence ─────────────────────────────────────────────────────
REBALANCE_CADENCE_DAYS = 14   # every ~2 calendar weeks (≈ every 2 trading weeks)

# ── B.5 variant (locked production) ─────────────────────────────────────
_B5_VARIANT = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)

_TREND_TICKERS = list(_NON_BENCHMARK_TREND)


# ── State persistence helpers ─────────────────────────────────────────────

def load_portfolio_state(as_of_date: pd.Timestamp, b5_weights_df: pd.DataFrame) -> dict:
    """Load tracked portfolio state; initialise from B.5 if no prior state exists."""
    if CURRENT_STATE_FILE.exists():
        with open(CURRENT_STATE_FILE) as f:
            state = json.load(f)
        nav_series = pd.Series(
            state["nav_history_values"],
            index=pd.to_datetime(state["nav_history_dates"]),
            name="nav",
        )
        last_rebalance = pd.Timestamp(state["last_rebalance_date"]) if state.get("last_rebalance_date") else None
        return {
            "equity_frac":       float(state["equity_frac"]),
            "trend_frac":        float(state["trend_frac"]),
            "cash_frac":         float(state["cash_frac"]),
            "nav_series":        nav_series,
            "last_rebalance_date": last_rebalance,
        }

    # Cold start — initialise from B.5 weights at or before as_of_date
    trend_f = _initial_trend_frac(b5_weights_df, as_of_date, _TREND_TICKERS)
    equity_f = max(0.25, 1.0 - trend_f)
    return {
        "equity_frac":         equity_f,
        "trend_frac":          trend_f,
        "cash_frac":           0.0,
        "nav_series":          pd.Series([1.0], index=pd.DatetimeIndex([as_of_date])),
        "last_rebalance_date": None,
    }


def save_portfolio_state(state: dict, allocation: dict) -> None:
    """Persist portfolio state to disk after each run."""
    PROD_STATE_DIR.mkdir(parents=True, exist_ok=True)
    nav = state["nav_series"]
    out = {
        "equity_frac":          state["equity_frac"],
        "trend_frac":           state["trend_frac"],
        "cash_frac":            state["cash_frac"],
        "nav_history_dates":    [str(d.date()) for d in nav.index],
        "nav_history_values":   nav.tolist(),
        "last_rebalance_date":  str(state["last_rebalance_date"].date()) if state.get("last_rebalance_date") else None,
        "last_run_date":        allocation["as_of_date"],
    }
    CURRENT_STATE_FILE.write_text(json.dumps(out, indent=2))


# ── Core computation ──────────────────────────────────────────────────────

def is_rebalance_date(as_of_date: pd.Timestamp, last_rebalance_date: pd.Timestamp | None) -> bool:
    """Return True if as_of_date triggers a rebalance."""
    if last_rebalance_date is None:
        return True
    days_since = (as_of_date - last_rebalance_date).days
    return days_since >= REBALANCE_CADENCE_DAYS


def _b5_weights_at(b5_weights_df: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
    avail = b5_weights_df[b5_weights_df.index <= date]
    if avail.empty:
        return pd.Series(dtype=float)
    return avail.iloc[-1].fillna(0.0)


def compute_allocation(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    sector_features_df: pd.DataFrame,
    model: PPO | None,
    portfolio_state: dict,
    as_of_date: pd.Timestamp,
    mode: str,
    force_rebalance: bool,
) -> tuple[dict, dict]:
    """Compute allocation for as_of_date. Returns (allocation_json, updated_state)."""

    rebalance = force_rebalance or is_rebalance_date(
        as_of_date, portfolio_state.get("last_rebalance_date")
    )

    # Current B.5 weights at as_of_date
    b5_snap = _b5_weights_at(b5_weights_df, as_of_date)

    # Stress score and SPY trend for today
    stress_avail = stress_series[stress_series.index <= as_of_date]
    stress_score = float(stress_avail.iloc[-1]) if not stress_avail.empty else 0.0

    prices = inputs["prices"]
    spy_col = inputs["universe_config"].benchmark
    if spy_col in prices.columns:
        spy_px = prices[prices.index <= as_of_date][spy_col].dropna()
        spy_ret_63 = float(spy_px.pct_change(63).iloc[-1]) if len(spy_px) >= 64 else 0.0
    else:
        spy_ret_63 = 0.0
    spy_trend_positive = spy_ret_63 > 0.0

    # Build RL state vector
    rl_state = build_state_v2(
        inputs=inputs,
        b5_weights=b5_weights_df,
        nav_series=portfolio_state["nav_series"],
        date=as_of_date,
        stress_series=stress_series,
        current_equity_frac=portfolio_state["equity_frac"],
        current_trend_frac=portfolio_state["trend_frac"],
        current_cash_frac=portfolio_state["cash_frac"],
        sector_features_df=sector_features_df,
    )

    # Determine action
    if mode == "b5_only" or not rebalance:
        raw_action = None
        equity_frac = portfolio_state["equity_frac"]
        trend_frac  = portfolio_state["trend_frac"]
        cash_frac   = portfolio_state["cash_frac"]
    elif model is not None:
        raw_action_arr, _ = model.predict(rl_state, deterministic=True)
        raw_action = [float(x) for x in raw_action_arr]
        _, exposure_info = apply_exposure_mix(b5_snap, _TREND_TICKERS, np.array(raw_action_arr))
        equity_frac = exposure_info["equity_frac"]
        trend_frac  = exposure_info["trend_frac"]
        cash_frac   = exposure_info["cash_frac"]
    else:
        logger.warning("No model loaded and mode is rl_e7 — falling back to B.5-only")
        raw_action = None
        equity_frac = portfolio_state["equity_frac"]
        trend_frac  = portfolio_state["trend_frac"]
        cash_frac   = portfolio_state["cash_frac"]

    # Apply exposure mix to get combined weights (only on rebalance or first run)
    if rebalance and mode == "rl_e7" and raw_action is not None:
        action_arr = np.array(raw_action, dtype=float)
        mixed_weights, _ = apply_exposure_mix(b5_snap, _TREND_TICKERS, action_arr)
        # Apply B.4 constraints as hard floor
        single_row   = pd.DataFrame([mixed_weights], index=[as_of_date])
        beta_slice   = beta_frame.reindex(index=[as_of_date]).fillna(0.0)
        if not beta_slice.empty and beta_slice.abs().sum().sum() > 1e-12:
            constrained, _ = apply_b4_constraints(
                single_row, beta_slice, stress_series, _B5_VARIANT,
                control_dates=[as_of_date], benchmark=spy_col,
            )
            final_weights = constrained.iloc[0].fillna(0.0)
        else:
            final_weights = mixed_weights
    else:
        final_weights = b5_snap

    # Split into stock vs trend weights
    trend_tickers_present = [t for t in _TREND_TICKERS if t in final_weights.index]
    stock_tickers = [t for t in final_weights.index
                     if t not in trend_tickers_present and t != spy_col
                     and abs(float(final_weights.get(t, 0.0))) > 1e-9]
    trend_weights_dict = {t: float(final_weights.get(t, 0.0)) for t in trend_tickers_present}
    stock_weights_dict  = {t: float(final_weights[t]) for t in stock_tickers}

    nav = float(portfolio_state["nav_series"].iloc[-1])

    allocation = {
        "as_of_date":         str(as_of_date.date()),
        "mode":               mode,
        "is_rebalance":       rebalance,
        "equity_frac":        round(equity_frac, 6),
        "trend_frac":         round(trend_frac, 6),
        "cash_frac":          round(cash_frac, 6),
        "stock_weights":      {k: round(v, 6) for k, v in stock_weights_dict.items()},
        "trend_weights":      {k: round(v, 6) for k, v in trend_weights_dict.items()},
        "rl_state_vector":    [float(x) for x in rl_state],
        "rl_raw_action":      raw_action,
        "stress_score":       round(stress_score, 6),
        "spy_trend_positive": spy_trend_positive,
        "nav":                round(nav, 6),
        "model_id":           "rl_e7_clean_promoted",
    }

    updated_state = {
        "equity_frac":           equity_frac,
        "trend_frac":            trend_frac,
        "cash_frac":             cash_frac,
        "nav_series":            portfolio_state["nav_series"],
        "last_rebalance_date":   as_of_date if rebalance else portfolio_state.get("last_rebalance_date"),
    }

    return allocation, updated_state


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase G.1 — Production Signal Generation")
    parser.add_argument("--config",    default="config/base.yaml")
    parser.add_argument("--universe",  default="config/universes/sp500.yaml")
    parser.add_argument("--mode",      choices=["rl_e7", "b5_only"], default="rl_e7")
    parser.add_argument("--as-of",     default=None,
                        help="Override date (YYYY-MM-DD); defaults to latest in price data")
    parser.add_argument("--force-rebalance", action="store_true",
                        help="Force a rebalance decision regardless of cadence")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Compute but do not write allocation or state files")
    parser.add_argument("--model-path", default=str(PRODUCTION_MODEL))
    args = parser.parse_args()

    t0 = time.perf_counter()
    logger.info("Phase G.1 — loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)

    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    as_of_date = (
        pd.Timestamp(args.as_of) if args.as_of
        else inputs["prices"].index.max()
    )
    logger.info("As-of date: %s", as_of_date.date())

    logger.info("Building beta / stress …")
    beta_frame    = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 weights …")
    from run_phase_b5_final_gate import build_promoted_weights
    b5_weights_df, _diag, _ctrl = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("B.5 built in %.1fs", time.perf_counter() - t0)

    logger.info("Loading sector features …")
    sector_features_df = pd.read_parquet(SECTOR_FEATURES_PATH)

    # Load production model (None in b5_only mode)
    model = None
    if args.mode == "rl_e7":
        model_path = Path(args.model_path)
        if model_path.exists():
            logger.info("Loading production model from %s …", model_path)
            model = PPO.load(str(model_path))
        else:
            logger.warning("Model not found at %s — switching to b5_only", model_path)
            args.mode = "b5_only"

    # Load or initialise portfolio state
    portfolio_state = load_portfolio_state(as_of_date, b5_weights_df)
    logger.info("Portfolio state: equity=%.3f trend=%.3f cash=%.3f nav=%.4f",
                portfolio_state["equity_frac"], portfolio_state["trend_frac"],
                portfolio_state["cash_frac"], float(portfolio_state["nav_series"].iloc[-1]))

    # Compute allocation
    allocation, updated_state = compute_allocation(
        inputs=inputs,
        b5_weights_df=b5_weights_df,
        beta_frame=beta_frame,
        stress_series=stress_series,
        sector_features_df=sector_features_df,
        model=model,
        portfolio_state=portfolio_state,
        as_of_date=as_of_date,
        mode=args.mode,
        force_rebalance=args.force_rebalance,
    )

    # Report
    logger.info(
        "Allocation: mode=%s is_rebalance=%s equity=%.3f trend=%.3f cash=%.3f "
        "stress=%.3f spy_trend=%s n_stocks=%d",
        allocation["mode"],
        allocation["is_rebalance"],
        allocation["equity_frac"],
        allocation["trend_frac"],
        allocation["cash_frac"],
        allocation["stress_score"],
        allocation["spy_trend_positive"],
        len(allocation["stock_weights"]),
    )

    if args.dry_run:
        logger.info("Dry run — skipping file writes")
        print(json.dumps({k: v for k, v in allocation.items() if k != "rl_state_vector"}, indent=2))
        return 0

    # Write allocation JSON
    ALLOCATIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ALLOCATIONS_DIR / f"{allocation['as_of_date']}.json"
    out_path.write_text(json.dumps(allocation, indent=2))
    logger.info("Allocation written to %s", out_path)

    # Update latest symlink / copy
    latest_path = ALLOCATIONS_DIR / "latest.json"
    shutil.copy2(out_path, latest_path)
    logger.info("Latest allocation updated at %s", latest_path)

    # Persist portfolio state
    save_portfolio_state(updated_state, allocation)
    logger.info("Portfolio state saved to %s", CURRENT_STATE_FILE)

    # Append to audit trail (G.2)
    append_decision(allocation)

    logger.info("G.1 complete in %.1fs", time.perf_counter() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
