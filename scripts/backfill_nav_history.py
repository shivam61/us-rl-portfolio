"""Backfill nav_history in current_state.json from fills + raw price data.

The production pipeline never computed daily mark-to-market NAV, leaving
nav_history frozen at [1.0, 2026-05-10]. This means state_builder_v2 indices
39/40/41 (portfolio drawdown, vol, 21d return z-score) were permanently zero
at every rebalance — the model had no self-awareness of its own P&L.

This script reconstructs the daily NAV series from first principles:
  - Cumulative share ledger built from fills_*.csv (all trades, in order)
  - Cash ledger tracked as: initial_nav - net_buy_notional
  - Each business day repriced at actual adj_close from data/raw/{ticker}.parquet

Writes the result into current_state.json and prints a summary.

Usage:
    .venv/bin/python scripts/backfill_nav_history.py [--dry-run]
"""
import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

FILLS_DIR = REPO_ROOT / "data" / "paper_trading"
RAW_DIR = REPO_ROOT / "data" / "raw"
STATE_FILE = REPO_ROOT / "data" / "prod_state" / "current_state.json"
INITIAL_NAV = 50_000.0


def load_all_fills() -> pd.DataFrame:
    files = sorted(FILLS_DIR.glob("fills_*.csv"))
    frames = []
    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        if df.empty or "ticker" not in df.columns:
            continue
        frames.append(df)
    if not frames:
        raise RuntimeError("No fill files found")
    all_fills = pd.concat(frames, ignore_index=True)
    all_fills["date"] = pd.to_datetime(all_fills["date"])
    all_fills = all_fills.sort_values("date")
    return all_fills


def load_close(ticker: str) -> pd.Series:
    path = RAW_DIR / f"{ticker}.parquet"
    if not path.exists():
        return pd.Series(dtype=float)
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df["close"].sort_index()


def build_nav_series(fills: pd.DataFrame) -> pd.Series:
    """Reconstruct daily mark-to-market NAV from fills + raw closes."""
    # Build daily share ledger snapshots: for each business day, what shares are held?
    # Walk forward: apply fills on their fill date, then reprice at that day's close.

    # 1. Collect all dates we need to price: every fill date + every trading day after T=0
    all_fill_dates = sorted(fills["date"].dt.normalize().unique())
    t0 = all_fill_dates[0]

    # Business days from T=0 to last fill date
    bdays = pd.bdate_range(start=t0, end=all_fill_dates[-1])

    # 2. Load closes for all tickers in fills
    tickers = [t for t in fills["ticker"].unique() if t != "__CASH__"]
    close_data: dict[str, pd.Series] = {}
    for t in tickers:
        s = load_close(t)
        if not s.empty:
            close_data[t] = s

    # 3. Walk forward day by day
    shares: dict[str, float] = {}
    cash = INITIAL_NAV  # start fully in cash
    nav_dates = []
    nav_values = []

    fills_by_date = fills.groupby(fills["date"].dt.normalize())

    for day in bdays:
        # Apply any fills for this day
        if day in fills_by_date.groups:
            day_fills = fills_by_date.get_group(day)
            for _, row in day_fills.iterrows():
                t = row["ticker"]
                # shares_filled is signed: positive = buy, negative = sell
                qty = float(row["shares_filled"])
                fill_px = float(row["fill_price"])
                signed_notional = qty * fill_px  # positive subtracts cash, negative adds
                shares[t] = shares.get(t, 0.0) + qty
                cash -= signed_notional

        # Mark-to-market: reprice all holdings at today's close
        invested = 0.0
        for t, qty in shares.items():
            if qty <= 0:
                continue
            cs = close_data.get(t)
            if cs is None:
                continue
            avail = cs[cs.index <= day]
            if avail.empty:
                continue
            invested += qty * float(avail.iloc[-1])

        nav = round(invested + cash, 4)
        nav_dates.append(day)
        nav_values.append(nav)

    return pd.Series(nav_values, index=pd.DatetimeIndex(nav_dates), name="nav")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logger.info("Loading fills …")
    fills = load_all_fills()
    logger.info("Loaded %d fill rows across %d dates", len(fills),
                fills["date"].dt.normalize().nunique())

    logger.info("Building NAV series …")
    nav = build_nav_series(fills)

    # Summary
    ret = nav.iloc[-1] / INITIAL_NAV - 1
    peak = nav.max()
    trough_idx = nav.idxmin()
    max_dd = (nav.iloc[nav.index.get_loc(trough_idx)] / nav[:trough_idx].max() - 1) if len(nav) > 1 else 0.0

    logger.info("NAV series: %d days, first=%s last=%s", len(nav),
                nav.index[0].date(), nav.index[-1].date())
    logger.info("NAV: start=$%.2f  end=$%.2f  total_return=%.2f%%",
                INITIAL_NAV, nav.iloc[-1], ret * 100)
    logger.info("Peak NAV: $%.2f  Max drawdown: %.2f%%", peak, max_dd * 100)

    print("\nDAILY NAV (first 5 / last 5):")
    print(nav.head().to_string())
    print("  ...")
    print(nav.tail().to_string())

    if args.dry_run:
        logger.info("--dry-run: not writing to current_state.json")
        return

    # Load existing state and update nav_history
    with open(STATE_FILE) as f:
        state = json.load(f)

    state["nav_history_dates"] = [str(d.date()) for d in nav.index]
    state["nav_history_values"] = [round(float(v), 4) for v in nav.values]

    STATE_FILE.write_text(json.dumps(state, indent=2))
    logger.info("Written %d NAV entries to %s", len(nav), STATE_FILE)


if __name__ == "__main__":
    main()
