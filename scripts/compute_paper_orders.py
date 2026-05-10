"""Phase H.0 — Compute Paper Trading Orders.

Reads the latest allocation JSON and current positions snapshot, then outputs
an orders CSV with fractional share quantities and estimated slippage.

Outputs
-------
data/paper_trading/orders_{date}.csv

Orders CSV schema
-----------------
date, ticker, sleeve, action, target_weight, current_weight,
target_shares, current_shares, delta_shares, est_fill_price,
est_slippage_bps, notional_usd

Usage
-----
# Initial T=0 allocation (no existing positions):
    .venv/bin/python scripts/compute_paper_orders.py --date 2026-05-10 --initial

# Subsequent rebalance:
    .venv/bin/python scripts/compute_paper_orders.py --date 2026-05-10

# Dry run (print orders, do not write):
    .venv/bin/python scripts/compute_paper_orders.py --date 2026-05-10 --dry-run
"""
import argparse
import json
import logging
import math
import sys
from pathlib import Path

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


def load_allocation(date: str, cfg: dict) -> dict:
    alloc_dir = REPO_ROOT / cfg["paths"]["allocations_dir"]
    dated = alloc_dir / f"{date}.json"
    latest = alloc_dir / "latest.json"
    path = dated if dated.exists() else latest
    if not path.exists():
        raise FileNotFoundError(f"No allocation found for {date} at {path}")
    with open(path) as f:
        return json.load(f)


def load_positions(cfg: dict) -> pd.DataFrame:
    """Load current positions. Returns empty DataFrame if none exist yet."""
    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    pos_path = pt_dir / "positions_latest.parquet"
    if not pos_path.exists():
        return pd.DataFrame(columns=[
            "ticker", "sleeve", "shares_held", "current_price",
            "market_value", "portfolio_weight", "target_weight", "weight_drift_pp",
        ])
    return pd.read_parquet(pos_path)


def load_close_prices(date: str) -> pd.Series:
    """Load EOD close prices.

    Priority:
      1. data/processed/prices.parquet (wide panel, fastest)
      2. data/raw/{ticker}.parquet per-ticker files (always present after feature pipeline)
    """
    target = pd.Timestamp(date)

    # 1. Wide panel
    prices_path = REPO_ROOT / "data" / "processed" / "prices.parquet"
    if prices_path.exists():
        prices = pd.read_parquet(prices_path)
        prices.index = pd.to_datetime(prices.index)
        available = prices.index[prices.index <= target]
        if len(available) > 0:
            return prices.loc[available[-1]].dropna()

    # 2. Per-ticker raw parquets
    raw_dir = REPO_ROOT / "data" / "raw"
    if raw_dir.exists():
        logger.info("Building price series from data/raw/ per-ticker parquets for %s", date)
        records: dict[str, float] = {}
        for parquet_file in raw_dir.glob("*.parquet"):
            ticker = parquet_file.stem
            try:
                df = pd.read_parquet(parquet_file, columns=["adj_close"])
                df.index = pd.to_datetime(df.index)
                avail = df.index[df.index <= target]
                if len(avail) > 0:
                    records[ticker] = float(df.loc[avail[-1], "adj_close"])
            except Exception:
                continue
        if records:
            logger.info("Loaded prices for %d tickers from raw parquets", len(records))
            return pd.Series(records)

    raise RuntimeError(f"Could not load close prices for {date}: no price source available")


def build_target_weights(alloc: dict) -> dict[str, tuple[float, str]]:
    """Return {ticker: (target_weight, sleeve)} for all sleeves."""
    targets: dict[str, tuple[float, str]] = {}
    for ticker, w in alloc.get("stock_weights", {}).items():
        targets[ticker] = (float(w), "equity")
    for ticker, w in alloc.get("trend_weights", {}).items():
        targets[ticker] = (float(w), "trend")
    return targets


def compute_orders(
    date: str,
    alloc: dict,
    positions: pd.DataFrame,
    prices: pd.Series,
    cfg: dict,
    initial: bool = False,
) -> pd.DataFrame:
    nav = cfg["capital"]["initial_nav"]
    assumption_bps = cfg["slippage"]["assumption_bps"]
    min_notional = cfg["broker"]["min_order_notional"]

    target_weights = build_target_weights(alloc)

    # Only normalise if weights sum > 1.0 (guards against old B.5 raw-weight bug where
    # stock_weights + trend_weights could sum to ~1.337, exceeding the NAV budget).
    # When weights sum < 1.0, the remainder is the intended cash allocation — do NOT
    # normalise it away, or cash gets stripped and sleeves inflate proportionally.
    total_weight = sum(w for w, _ in target_weights.values())
    if total_weight > 1.0 + 1e-9:
        target_weights = {t: (w / total_weight, s) for t, (w, s) in target_weights.items()}

    # current holdings indexed by ticker
    current_shares: dict[str, float] = {}
    current_weights: dict[str, float] = {}
    if not positions.empty and not initial:
        for _, row in positions.iterrows():
            current_shares[row["ticker"]] = float(row["shares_held"])
            current_weights[row["ticker"]] = float(row["portfolio_weight"])

    rows = []
    all_tickers = set(target_weights) | set(current_shares)

    for ticker in sorted(all_tickers):
        target_w, sleeve = target_weights.get(ticker, (0.0, "equity"))

        if ticker not in prices.index:
            logger.warning("No price for %s on %s — skipping", ticker, date)
            continue

        price = float(prices[ticker])
        if price <= 0:
            logger.warning("Zero/negative price for %s — skipping", ticker)
            continue

        current_w = current_weights.get(ticker, 0.0)
        current_s = current_shares.get(ticker, 0.0)
        target_s = math.floor(target_w * nav / price * 1_000_000) / 1_000_000  # floor at 6dp, never exceed budget
        delta_s = round(target_s - current_s, 6)
        notional = abs(delta_s) * price

        if notional < min_notional:
            action = "hold"
            delta_s = 0.0
        elif delta_s > 0:
            action = "buy"
        elif delta_s < 0:
            action = "sell"
        else:
            action = "hold"

        rows.append({
            "date": date,
            "ticker": ticker,
            "sleeve": sleeve,
            "action": action,
            "target_weight": round(target_w, 6),
            "current_weight": round(current_w, 6),
            "target_shares": target_s,
            "current_shares": round(current_s, 6),
            "delta_shares": delta_s,
            "est_fill_price": round(price, 4),
            "est_slippage_bps": assumption_bps if action != "hold" else 0,
            "notional_usd": round(notional, 2),
        })

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute paper trading orders")
    parser.add_argument("--date", required=True, help="Signal date YYYY-MM-DD")
    parser.add_argument("--initial", action="store_true", help="T=0: no existing positions")
    parser.add_argument("--dry-run", action="store_true", help="Print orders, do not write")
    args = parser.parse_args()

    cfg = load_config()
    logger.info("Paper trading config: version=%s, NAV=%.2f", cfg["version"], cfg["capital"]["initial_nav"])

    alloc = load_allocation(args.date, cfg)
    logger.info("Loaded allocation: date=%s, mode=%s, is_rebalance=%s",
                alloc["as_of_date"], alloc["mode"], alloc["is_rebalance"])

    positions = load_positions(cfg)
    if args.initial:
        logger.info("--initial flag: treating all current positions as zero")
        positions = positions.iloc[0:0]

    prices = load_close_prices(args.date)
    logger.info("Loaded prices for %d tickers", len(prices))

    orders = compute_orders(args.date, alloc, positions, prices, cfg, initial=args.initial)

    active = orders[orders["action"] != "hold"]
    logger.info("Orders: %d total, %d buys, %d sells, %d holds",
                len(orders),
                (orders["action"] == "buy").sum(),
                (orders["action"] == "sell").sum(),
                (orders["action"] == "hold").sum())
    if not active.empty:
        total_notional = active["notional_usd"].sum()
        logger.info("Total order notional: $%.2f (turnover: %.1f%%)",
                    total_notional, 100 * total_notional / cfg["capital"]["initial_nav"])

    if args.dry_run:
        print(orders.to_string(index=False))
        return

    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    pt_dir.mkdir(parents=True, exist_ok=True)
    out_path = pt_dir / f"orders_{args.date}.csv"
    orders.to_csv(out_path, index=False)
    logger.info("Orders written to %s", out_path)


if __name__ == "__main__":
    main()
