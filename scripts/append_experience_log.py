"""Phase H.6 — Append one transition to the paper trading experience log.

Writes data/paper_trading/experience_log.parquet — one row per rebalance.
Called from run_daily_paper_ops.py on rebalance days only.

Two-pass design:
  Pass 1 (same day as rebalance): write row with T-fields + T+1 fills;
          T+14 outcome columns are left null.
  Pass 2 (14 days later, on next rebalance): backfill T+14 outcome columns
          for the prior row using accumulated daily positions snapshots.

The log is write-once / append-only during Phase H. No retraining is triggered.
It is a dataset for future offline RL training/evaluation only.

Usage
-----
    python scripts/append_experience_log.py --date 2026-05-10
"""
import argparse
import json
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.rl.reward_v2 import compute_reward_v2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PT_DIR = REPO_ROOT / "data" / "paper_trading"
ALLOC_DIR = REPO_ROOT / "data" / "allocations"
DRIFT_FLAGS_PATH = REPO_ROOT / "data" / "drift" / "flags.parquet"
B5_NAV_PATH = REPO_ROOT / "data" / "switching" / "nav_b5_backtest.parquet"
SPY_PATH = REPO_ROOT / "data" / "raw" / "SPY.parquet"
LOG_PATH = PT_DIR / "experience_log.parquet"

# T+14 outcome columns — null until backfilled
_T14_COLS = [
    "nav_t_plus_14",
    "realized_return_14d",
    "realized_vol_14d",
    "drawdown_14d",
    "tracking_error_vs_b5",
    "tracking_error_vs_spy",
    "reward_offline_t",
    "offline_advantage_t",   # reward_offline_t - value_estimate_t; filled in pass2
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_allocation(date_str: str) -> dict:
    for p in [ALLOC_DIR / f"{date_str}.json", ALLOC_DIR / "latest.json"]:
        if p.exists():
            with open(p) as f:
                return json.load(f)
    raise FileNotFoundError(f"No allocation JSON for {date_str}")


def _load_drift_flags(date_str: str) -> str:
    """Return latest drift flag row as JSON string, or '{}'."""
    if not DRIFT_FLAGS_PATH.exists():
        return "{}"
    df = pd.read_parquet(DRIFT_FLAGS_PATH)
    if df.empty:
        return "{}"
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    if not flag_cols:
        return "{}"
    latest = df.iloc[-1][flag_cols]
    return json.dumps({k: bool(v) for k, v in latest.items()})


def _load_orders(date_str: str) -> tuple[str, float]:
    """Return (orders JSON blob, rebalance turnover ratio)."""
    path = PT_DIR / f"orders_{date_str}.csv"
    if not path.exists():
        return "{}", 0.0
    df = pd.read_csv(path)
    orders = dict(zip(df["ticker"], df["delta_shares"].round(6)))
    nav = (df["notional_usd"] / df["delta_shares"].abs().clip(lower=1e-12)).mean()
    total_notional = df["notional_usd"].sum()
    nav_est = df.apply(lambda r: r["notional_usd"] / max(abs(r["delta_shares"]), 1e-9) * r.get("target_shares", 1), axis=1).mean()
    # turnover = sum(|notional|) / nav; use target_weight * nav if available
    if "notional_usd" in df.columns and "est_fill_price" in df.columns:
        est_nav = (df["target_shares"] * df["est_fill_price"]).sum() if "target_shares" in df.columns else 50_000.0
        turnover = float(df["notional_usd"].sum() / max(est_nav, 1.0))
    else:
        turnover = 0.0
    return json.dumps(orders), round(turnover, 6)


def _load_fills(date_str: str) -> tuple[str, float]:
    """Return (fills JSON blob, portfolio-level weighted avg slippage bps)."""
    path = PT_DIR / f"fills_{date_str}.csv"
    if not path.exists():
        return "{}", 0.0
    df = pd.read_csv(path)
    fills = dict(zip(df["ticker"], df["fill_price"].round(6)))
    if "actual_slippage_bps" in df.columns and "notional_usd" in df.columns:
        total_notional = df["notional_usd"].sum()
        if total_notional > 0:
            avg_slip = float((df["actual_slippage_bps"] * df["notional_usd"]).sum() / total_notional)
        else:
            avg_slip = float(df["actual_slippage_bps"].mean())
    else:
        avg_slip = 0.0
    return json.dumps(fills), round(avg_slip, 4)


def _load_actual_weights(date_str: str) -> tuple[str, float]:
    """Return (actual_weights JSON blob, nav_t_plus_1) from positions_latest.parquet."""
    path = PT_DIR / "positions_latest.parquet"
    if not path.exists():
        return "{}", 0.0
    df = pd.read_parquet(path)
    weights = dict(zip(df["ticker"], df["portfolio_weight"].round(6)))
    nav = float(df["market_value"].sum())
    return json.dumps(weights), round(nav, 2)


def _tracking_error_vs_target(actual_json: str, target_json: str) -> float:
    """Sqrt(sum((w_actual - w_target)^2)) across common tickers."""
    actual = json.loads(actual_json)
    target = json.loads(target_json)
    tickers = set(actual) | set(target)
    diffs = [(actual.get(t, 0.0) - target.get(t, 0.0)) ** 2 for t in tickers]
    return round(float(np.sqrt(sum(diffs))), 6)


def _load_daily_nav_series(date_t: date, date_end: date) -> pd.Series:
    """Reconstruct daily NAV from positions_{date}.parquet snapshots."""
    navs = {}
    d = date_t
    while d <= date_end:
        p = PT_DIR / f"positions_{d.isoformat()}.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            navs[d] = float(df["market_value"].sum())
        d += timedelta(days=1)
    if not navs:
        return pd.Series(dtype=float)
    return pd.Series(navs)


def _annualised_te(portfolio_rets: pd.Series, bench_rets: pd.Series) -> float:
    aligned = pd.concat([portfolio_rets, bench_rets], axis=1, join="inner").dropna()
    if len(aligned) < 2:
        return float("nan")
    diff = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    return float(diff.std(ddof=1) * np.sqrt(252))


def _backfill_t14(row: pd.Series, date_t: date) -> dict:
    """Compute all T+14 outcome fields for a row written 14 days ago."""
    date_end = date_t + timedelta(days=14)
    nav_series = _load_daily_nav_series(date_t, date_end)

    if nav_series.empty or len(nav_series) < 2:
        logger.warning("Insufficient daily positions for T+14 backfill of %s", date_t)
        return {}

    nav_t = float(row["nav_t"])
    nav_t14 = float(nav_series.iloc[-1])
    daily_rets = nav_series.pct_change().dropna()

    realized_return = round(nav_t14 / nav_t - 1, 6) if nav_t > 0 else float("nan")
    realized_vol = round(float(daily_rets.std(ddof=1) * np.sqrt(252)), 6) if len(daily_rets) >= 2 else float("nan")
    drawdown = round(float(nav_series.min() / nav_series.max() - 1), 6)

    # Tracking error vs B.5
    te_b5 = float("nan")
    if B5_NAV_PATH.exists():
        b5 = pd.read_parquet(B5_NAV_PATH)
        b5["as_of_date"] = pd.to_datetime(b5["as_of_date"])
        b5 = b5.set_index("as_of_date")["nav"]
        b5_window = b5.loc[str(date_t):str(date_end)]
        b5_rets = b5_window.pct_change().dropna()
        nav_idx = pd.Series(nav_series.values, index=pd.to_datetime(nav_series.index))
        port_rets = nav_idx.pct_change().dropna()
        te_b5 = _annualised_te(port_rets, b5_rets)

    # Tracking error vs SPY
    te_spy = float("nan")
    if SPY_PATH.exists():
        spy = pd.read_parquet(SPY_PATH)
        spy.index = pd.to_datetime(spy.index)
        spy_window = spy["adj_close"].loc[str(date_t):str(date_end)]
        spy_rets = spy_window.pct_change().dropna()
        nav_idx = pd.Series(nav_series.values, index=pd.to_datetime(nav_series.index))
        port_rets = nav_idx.pct_change().dropna()
        te_spy = _annualised_te(port_rets, spy_rets)

    # Offline reward using realized nav window
    nav_series_pd = pd.Series(
        nav_series.values.astype(float),
        index=pd.to_datetime(nav_series.index),
    )
    reward = compute_reward_v2(
        daily_returns=daily_rets,
        portfolio_nav=nav_series_pd,
        equity_frac=float(row.get("equity_frac_t", 0.5)),
        prev_equity_frac=float(row.get("equity_frac_t", 0.5)),
        cash_frac=float(row.get("cash_frac_t", 0.0)),
        stress_score=float(row.get("stress_score_t", 0.0)),
        spy_trend_positive=bool(row.get("spy_trend_positive_t", True)),
    )

    # Offline advantage = realized reward - value estimate at decision time.
    # Positive: model was pessimistic (underestimated how good the state was).
    # Negative: model was optimistic (overestimated; the period turned out worse).
    value_est = row.get("value_estimate_t")
    offline_advantage = (
        round(reward - float(value_est), 6)
        if value_est is not None and not np.isnan(float(value_est))
        else None
    )

    return {
        "nav_t_plus_14":         round(nav_t14, 2),
        "realized_return_14d":   realized_return,
        "realized_vol_14d":      realized_vol,
        "drawdown_14d":          drawdown,
        "tracking_error_vs_b5":  round(te_b5, 6) if not np.isnan(te_b5) else None,
        "tracking_error_vs_spy": round(te_spy, 6) if not np.isnan(te_spy) else None,
        "reward_offline_t":      round(reward, 6),
        "offline_advantage_t":   offline_advantage,
    }


# ---------------------------------------------------------------------------
# Main passes
# ---------------------------------------------------------------------------

def _load_log() -> pd.DataFrame:
    if LOG_PATH.exists():
        return pd.read_parquet(LOG_PATH)
    return pd.DataFrame()


def _save_log(df: pd.DataFrame) -> None:
    PT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(LOG_PATH, index=False)


def pass1_append_row(date_str: str) -> None:
    """Build and append the T-row for today's rebalance."""
    alloc = _load_allocation(date_str)

    # T-fields from allocation JSON
    state_vec = alloc.get("rl_state_vector", [])
    rl_action = alloc.get("rl_raw_action")
    target_weights = json.dumps(alloc.get("stock_weights", {}))

    drift_flags = _load_drift_flags(date_str)
    orders_json, turnover = _load_orders(date_str)
    fills_json, slippage_bps = _load_fills(date_str)
    actual_weights_json, nav_t1 = _load_actual_weights(date_str)
    te_target = _tracking_error_vs_target(actual_weights_json, target_weights)

    diag = alloc.get("rl_policy_diagnostics", {})

    row = {
        # T-fields
        "date_t": date_str,
        "state_vector_t": json.dumps(state_vec),
        "mode_t": alloc.get("mode", "unknown"),
        "rl_action_t": json.dumps(rl_action),
        "target_weights_t": target_weights,
        "nav_t": alloc.get("nav", 0.0),
        "equity_frac_t": alloc.get("equity_frac", None),
        "cash_frac_t": alloc.get("cash_frac", None),
        "stress_score_t": alloc.get("stress_score", None),
        "spy_trend_positive_t": alloc.get("spy_trend_positive", None),
        "model_id_t": alloc.get("model_id", None),
        "switch_reason_t": alloc.get("switch_reason", None),
        "drift_flags_t": drift_flags,
        # Policy internals — logged at decision time for post-hoc analysis.
        # value_estimate_t: V(s) from critic. State-dependent — varies per rebalance.
        # action_log_prob_t / policy_entropy_t: fixed learned params in DiagGaussian,
        #   constant across runs of same model. Logged once for reference.
        # offline_advantage_t: reward_offline_t - value_estimate_t, filled in pass2
        #   once T+14 outcome is known. Positive = model underestimated; negative = overestimated.
        "value_estimate_t": diag.get("value_estimate", None),
        "action_log_prob_t": diag.get("action_log_prob", None),
        "policy_entropy_t": diag.get("policy_entropy", None),
        # T+1 fill fields
        "actual_weights_t": actual_weights_json,
        "orders_t": orders_json,
        "fills_t": fills_json,
        "slippage_bps_t": slippage_bps,
        "rebalance_turnover_t": turnover,
        "tracking_error_vs_target": te_target,
        "nav_t_plus_1": nav_t1,
        # T+14 fields — null until backfilled
        **{col: None for col in _T14_COLS},
    }

    df = _load_log()
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    _save_log(df)
    logger.info("Experience log: appended T-row for %s (%d total rows)", date_str, len(df))


def pass2_backfill_t14(date_str: str) -> None:
    """Backfill T+14 outcomes for the row written 14 days ago."""
    df = _load_log()
    if df.empty:
        return

    target_date = (date.fromisoformat(date_str) - timedelta(days=14)).isoformat()
    mask = df["date_t"] == target_date

    if not mask.any():
        logger.info("Experience log: no row found for T-14 date %s — skipping backfill", target_date)
        return

    idx = df.index[mask][0]
    row = df.loc[idx]

    if pd.notna(row.get("nav_t_plus_14")):
        logger.info("Experience log: T+14 fields already filled for %s — skipping", target_date)
        return

    updates = _backfill_t14(row, date.fromisoformat(target_date))
    if not updates:
        return

    for col, val in updates.items():
        df.at[idx, col] = val

    _save_log(df)
    logger.info(
        "Experience log: backfilled T+14 for %s — return=%.4f reward=%.4f",
        target_date,
        updates.get("realized_return_14d", float("nan")),
        updates.get("reward_offline_t", float("nan")),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Append/backfill experience log")
    parser.add_argument("--date", required=True, help="Rebalance date YYYY-MM-DD")
    args = parser.parse_args()

    # Always attempt T+14 backfill first (idempotent, skips if already done)
    pass2_backfill_t14(args.date)
    # Then append today's T-row
    pass1_append_row(args.date)


if __name__ == "__main__":
    main()
