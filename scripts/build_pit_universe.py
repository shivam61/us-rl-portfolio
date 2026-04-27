"""
Builds a point-in-time universe mask using a rolling ADV liquidity filter.

A ticker is marked active on a given date when its 63-day rolling average
dollar volume meets the threshold, using only data available up to that date.
This naturally excludes pre-IPO periods, delisted stocks, and low-liquidity
names without needing external index membership data.
"""
import pandas as pd
import pandas_market_calendars as mcal
import yaml
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_pit_universe(config_path: str,
                       output_path: str,
                       cache_dir: str = 'data',
                       adv_threshold: float = 1e8,
                       adv_window: int = 63):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    tickers = list(config['tickers'].keys())
    raw_dir = Path(cache_dir) / 'raw'

    logger.info(f"Building ADV-based PIT mask: {len(tickers)} tickers, "
                f"threshold=${adv_threshold/1e6:.0f}M, window={adv_window}d")

    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date='2006-01-01', end_date='2026-12-31')
    dates = pd.DatetimeIndex(schedule.index)
    result = pd.DataFrame(False, index=dates, columns=tickers)

    active_summary = []
    missing = []
    for ticker in tickers:
        path = raw_dir / f"{ticker}.parquet"
        if not path.exists():
            missing.append(ticker)
            continue

        try:
            df = pd.read_parquet(path)
            close = df.get('adj_close', df.get('close'))
            volume = df.get('volume')
            if close is None or volume is None:
                missing.append(ticker)
                continue

            dollar_vol = (close * volume).rolling(adv_window, min_periods=21).mean()
            active = (dollar_vol >= adv_threshold) & close.notna()

            # Reindex to full date grid; dates before first data → False
            active = active.reindex(dates, fill_value=False)
            result[ticker] = active

            n = int(active.sum())
            active_summary.append(n)
        except Exception as e:
            logger.error(f"{ticker}: {e}")
            missing.append(ticker)

    if missing:
        logger.warning(f"{len(missing)} tickers had no cached data: {missing[:10]}{'...' if len(missing)>10 else ''}")

    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path)
    logger.info(f"Saved PIT mask → {output_path}")

    active_per_day = result.sum(axis=1)
    logger.info(f"Active tickers per day  avg={active_per_day.mean():.0f}  "
                f"min={active_per_day.min()}  max={active_per_day.max()}")
    logger.info(f"Sample (recent): {active_per_day.tail(5).to_dict()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build ADV-based PIT universe mask")
    parser.add_argument('--config', type=str, default='config/universes/sp500.yaml')
    parser.add_argument('--output', type=str, default='data/artifacts/universe_mask_sp500.parquet')
    parser.add_argument('--cache-dir', type=str, default='data')
    parser.add_argument('--adv-threshold', type=float, default=1e8,
                        help='Min rolling 63d ADV in dollars (default: $100M)')
    args = parser.parse_args()

    build_pit_universe(args.config, args.output, args.cache_dir, args.adv_threshold)
