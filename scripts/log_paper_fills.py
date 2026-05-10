"""Phase H.0 — Log Paper Trading Fills.

Simulates T+1 fills using next-day open prices. Computes actual slippage in bps
relative to the signal-day close, updates the running positions snapshot, and
appends to the cumulative slippage summary.

Inputs
------
data/paper_trading/orders_{date}.csv       (from compute_paper_orders.py)

Outputs
-------
data/paper_trading/fills_{date}.csv        per-trade fill record
data/paper_trading/slippage_summary.csv    cumulative slippage log (appended)
data/paper_trading/positions_latest.parquet updated portfolio snapshot

Fills CSV schema
----------------
date, ticker, sleeve, shares_filled, fill_price, signal_close_price,
actual_slippage_bps, slippage_flagged, notional_usd

Positions parquet schema
------------------------
as_of_date, ticker, sleeve, shares_held, current_price, market_value,
portfolio_weight, target_weight, weight_drift_pp

Usage
-----
# Simulate fills for a given signal date (next-day open used as fill price):
    .venv/bin/python scripts/log_paper_fills.py --signal-date 2026-05-10

# Use a specific fill date (defaults to signal_date + 1 business day):
    .venv/bin/python scripts/log_paper_fills.py --signal-date 2026-05-10 --fill-date 2026-05-11

# Dry run (compute fills, do not write):
    .venv/bin/python scripts/log_paper_fills.py --signal-date 2026-05-10 --dry-run
"""
import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_config() -> dict:
    path = REPO_ROOT / "config" / "paper_trading.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def next_business_day(date_str: str) -> str:
    ts = pd.Timestamp(date_str)
    return (ts + pd.offsets.BDay(1)).strftime("%Y-%m-%d")


def load_open_prices(date: str) -> pd.Series:
    """Load next-day open prices from processed data. Falls back to yfinance."""
    prices_path = REPO_ROOT / "data" / "processed" / "prices_open.parquet"
    if prices_path.exists():
        opens = pd.read_parquet(prices_path)
        opens.index = pd.to_datetime(opens.index)
        target = pd.Timestamp(date)
        if target in opens.index:
            return opens.loc[target].dropna()
        available = opens.index[opens.index <= target]
        if len(available) > 0:
            return opens.loc[available[-1]].dropna()

    # fallback: use close prices as proxy (conservative — avoids yfinance for opens)
    prices_path = REPO_ROOT / "data" / "processed" / "prices.parquet"
    if prices_path.exists():
        closes = pd.read_parquet(prices_path)
        closes.index = pd.to_datetime(closes.index)
        target = pd.Timestamp(date)
        available = closes.index[closes.index <= target]
        if len(available) > 0:
            logger.info("open prices not available — using close prices as fill proxy for %s", date)
            return closes.loc[available[-1]].dropna()

    try:
        import yfinance as yf
        logger.info("Fetching open prices via yfinance for %s", date)
        sp500_path = REPO_ROOT / "config" / "universes" / "sp500.yaml"
        with open(sp500_path) as f:
            univ = yaml.safe_load(f)
        tickers = univ.get("tickers", []) + ["SPY", "TLT", "GLD", "UUP"]
        end = (pd.Timestamp(date) + pd.offsets.BDay(1)).strftime("%Y-%m-%d")
        data = yf.download(tickers, start=date, end=end, auto_adjust=True, progress=False)
        if "Open" in data.columns:
            row = data["Open"].loc[data.index >= date]
            if not row.empty:
                return row.iloc[0].dropna()
    except Exception as e:
        raise RuntimeError(f"Could not load open prices for {date}: {e}") from e

    raise RuntimeError(f"No open prices found for {date}")


def compute_fills(
    orders: pd.DataFrame,
    close_prices: pd.Series,
    open_prices: pd.Series,
    signal_date: str,
    fill_date: str,
    cfg: dict,
) -> pd.DataFrame:
    flag_bps = cfg["slippage"]["flag_bps"]
    rows = []

    active = orders[orders["action"] != "hold"].copy()
    for _, row in active.iterrows():
        ticker = row["ticker"]
        if ticker not in open_prices.index:
            logger.warning("No open price for %s on %s — skipping fill", ticker, fill_date)
            continue
        if ticker not in close_prices.index:
            logger.warning("No close price for %s on %s — skipping fill", ticker, signal_date)
            continue

        fill_price = float(open_prices[ticker])
        signal_close = float(close_prices[ticker])
        shares = float(row["delta_shares"])

        # slippage: positive = paid more than close (worse for buys, better for sells)
        direction = 1 if row["action"] == "buy" else -1
        raw_slippage_bps = direction * (fill_price - signal_close) / signal_close * 10_000
        notional = abs(shares) * fill_price

        rows.append({
            "date": fill_date,
            "signal_date": signal_date,
            "ticker": ticker,
            "sleeve": row["sleeve"],
            "action": row["action"],
            "shares_filled": round(shares, 6),
            "fill_price": round(fill_price, 4),
            "signal_close_price": round(signal_close, 4),
            "actual_slippage_bps": round(raw_slippage_bps, 2),
            "slippage_flagged": bool(abs(raw_slippage_bps) > flag_bps),
            "notional_usd": round(notional, 2),
        })

    return pd.DataFrame(rows)


def update_positions(
    orders: pd.DataFrame,
    fills: pd.DataFrame,
    open_prices: pd.Series,
    fill_date: str,
    cfg: dict,
) -> pd.DataFrame:
    nav = cfg["capital"]["initial_nav"]

    # load existing positions
    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    pos_path = pt_dir / "positions_latest.parquet"
    if pos_path.exists():
        existing = pd.read_parquet(pos_path).set_index("ticker")
    else:
        existing = pd.DataFrame(columns=["sleeve", "shares_held"])

    # apply fills
    shares_map: dict[str, float] = {}
    sleeve_map: dict[str, str] = {}
    for _, row in existing.iterrows():
        shares_map[row.name] = float(row["shares_held"])
        sleeve_map[row.name] = row["sleeve"]

    for _, row in fills.iterrows():
        ticker = row["ticker"]
        shares_map[ticker] = shares_map.get(ticker, 0.0) + float(row["shares_filled"])
        sleeve_map[ticker] = row["sleeve"]

    # include all target tickers from orders even if zero fills (for weight tracking)
    for _, row in orders.iterrows():
        t = row["ticker"]
        if t not in sleeve_map:
            sleeve_map[t] = row["sleeve"]
        if t not in shares_map:
            shares_map[t] = 0.0

    # build positions snapshot
    rows = []
    total_mv = 0.0
    for ticker, shares in shares_map.items():
        if shares <= 0:
            continue
        price = float(open_prices[ticker]) if ticker in open_prices.index else 0.0
        mv = shares * price
        total_mv += mv
        rows.append({"ticker": ticker, "sleeve": sleeve_map.get(ticker, "equity"),
                     "shares_held": round(shares, 6), "current_price": round(price, 4),
                     "market_value": round(mv, 2)})

    pos_df = pd.DataFrame(rows)
    if pos_df.empty:
        return pos_df

    pos_df["portfolio_weight"] = (pos_df["market_value"] / nav).round(6)

    # attach target weights from orders
    target_map = {row["ticker"]: row["target_weight"] for _, row in orders.iterrows()}
    pos_df["target_weight"] = pos_df["ticker"].map(target_map).fillna(0.0).round(6)
    pos_df["weight_drift_pp"] = ((pos_df["portfolio_weight"] - pos_df["target_weight"]) * 100).round(3)
    pos_df.insert(0, "as_of_date", fill_date)

    return pos_df


def append_slippage_summary(fills: pd.DataFrame, cfg: dict) -> None:
    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    summary_path = pt_dir / "slippage_summary.csv"
    if not fills.empty:
        summary_cols = ["date", "signal_date", "ticker", "sleeve", "action",
                        "actual_slippage_bps", "slippage_flagged", "notional_usd"]
        row = fills[summary_cols]
        header = not summary_path.exists()
        row.to_csv(summary_path, mode="a", index=False, header=header)


def main() -> None:
    parser = argparse.ArgumentParser(description="Log paper trading fills")
    parser.add_argument("--signal-date", required=True, help="Signal date YYYY-MM-DD")
    parser.add_argument("--fill-date", default=None, help="Fill date YYYY-MM-DD (default: next business day)")
    parser.add_argument("--dry-run", action="store_true", help="Compute fills but do not write")
    args = parser.parse_args()

    fill_date = args.fill_date or next_business_day(args.signal_date)
    cfg = load_config()
    logger.info("Config: version=%s, NAV=%.2f, flag_bps=%d",
                cfg["version"], cfg["capital"]["initial_nav"], cfg["slippage"]["flag_bps"])

    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    orders_path = pt_dir / f"orders_{args.signal_date}.csv"
    if not orders_path.exists():
        raise FileNotFoundError(f"Orders file not found: {orders_path}. Run compute_paper_orders.py first.")
    orders = pd.read_csv(orders_path)
    logger.info("Loaded %d orders from %s", len(orders), orders_path)

    # close prices on signal date for slippage baseline
    prices_path = REPO_ROOT / "data" / "processed" / "prices.parquet"
    if prices_path.exists():
        closes_all = pd.read_parquet(prices_path)
        closes_all.index = pd.to_datetime(closes_all.index)
        target = pd.Timestamp(args.signal_date)
        available = closes_all.index[closes_all.index <= target]
        close_prices = closes_all.loc[available[-1]].dropna() if len(available) > 0 else pd.Series(dtype=float)
    else:
        close_prices = pd.Series(dtype=float)

    open_prices = load_open_prices(fill_date)
    logger.info("Loaded open prices for %d tickers on %s", len(open_prices), fill_date)

    fills = compute_fills(orders, close_prices, open_prices, args.signal_date, fill_date, cfg)
    logger.info("Fills: %d trades, avg slippage %.1f bps, flagged %d",
                len(fills),
                fills["actual_slippage_bps"].abs().mean() if not fills.empty else 0.0,
                fills["slippage_flagged"].sum() if not fills.empty else 0)

    positions = update_positions(orders, fills, open_prices, fill_date, cfg)
    max_drift = positions["weight_drift_pp"].abs().max() if not positions.empty else 0.0
    logger.info("Positions: %d holdings, max weight drift %.2f pp (H-4 gate: %.1f pp)",
                len(positions), max_drift, cfg["risk"]["target_weight_drift_pp"])

    if args.dry_run:
        print("\n--- FILLS ---")
        print(fills.to_string(index=False))
        print("\n--- POSITIONS (top 10 by drift) ---")
        if not positions.empty:
            print(positions.nlargest(10, "weight_drift_pp").to_string(index=False))
        return

    pt_dir.mkdir(parents=True, exist_ok=True)

    fills_path = pt_dir / f"fills_{args.signal_date}.csv"
    fills.to_csv(fills_path, index=False)
    logger.info("Fills written to %s", fills_path)

    append_slippage_summary(fills, cfg)
    logger.info("Slippage summary updated")

    if not positions.empty:
        pos_path = pt_dir / "positions_latest.parquet"
        positions.to_parquet(pos_path, index=False)
        logger.info("Positions snapshot written to %s", pos_path)

        snapshot_path = pt_dir / f"positions_{fill_date}.parquet"
        positions.to_parquet(snapshot_path, index=False)
        logger.info("Daily positions archive written to %s", snapshot_path)


if __name__ == "__main__":
    main()
