"""Phase H — Incremental market data refresh.

Appends only the missing trading days to each data/raw/{ticker}.parquet,
then rebuilds all feature parquets. Safe to re-run — skips tickers that
are already up to date. Much faster than a full re-download.

Usage
-----
    .venv/bin/python scripts/refresh_market_data.py
    .venv/bin/python scripts/refresh_market_data.py --as-of 2026-05-09   # backfill to specific date
    .venv/bin/python scripts/refresh_market_data.py --skip-features       # price refresh only
"""
import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.providers.yfinance_provider import YFinanceProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = REPO_ROOT / "data" / "raw"
FEATURES_DIR = REPO_ROOT / "data" / "features"
N_WORKERS = 8


def load_universe_tickers() -> list[str]:
    sp500_path = REPO_ROOT / "config" / "universes" / "sp500.yaml"
    with open(sp500_path) as f:
        u = yaml.safe_load(f)
    raw = u.get("tickers", {})
    tickers = list(raw.keys()) if isinstance(raw, dict) else list(raw)
    tickers += u.get("sector_etfs", [])
    tickers += u.get("macro_etfs", [])
    tickers += [u.get("benchmark", "SPY"), u.get("vix_proxy", "^VIX")]
    return sorted(set(tickers))


def last_cached_date(ticker: str) -> date | None:
    path = RAW_DIR / f"{ticker}.parquet"
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path, columns=["adj_close"])
        df.index = pd.to_datetime(df.index)
        return df.index.max().date()
    except Exception:
        return None


def refresh_ticker(ticker: str, target_date: date, provider: YFinanceProvider) -> tuple[str, str]:
    """Fetch missing days and append to existing parquet. Returns (ticker, status)."""
    last = last_cached_date(ticker)
    if last is not None and last >= target_date:
        return ticker, "up_to_date"

    fetch_start = (last + timedelta(days=1)).isoformat() if last else "2006-01-01"
    fetch_end = (target_date + timedelta(days=1)).isoformat()  # yfinance end is exclusive

    try:
        new_df = provider.download_ticker(ticker, fetch_start, fetch_end)
        if new_df.empty:
            return ticker, "no_new_data"

        new_df.index = pd.to_datetime(new_df.index)
        new_df.index.name = "date"

        path = RAW_DIR / f"{ticker}.parquet"
        if path.exists() and last is not None:
            existing = pd.read_parquet(path)
            existing.index = pd.to_datetime(existing.index)
            combined = pd.concat([existing, new_df])
            combined = combined[~combined.index.duplicated(keep="last")].sort_index()
        else:
            combined = new_df

        combined.to_parquet(path)
        n_new = len(new_df)
        return ticker, f"+{n_new} rows"
    except Exception as e:
        return ticker, f"ERROR: {e}"


def refresh_all_prices(target_date: date) -> tuple[int, int, int]:
    """Refresh all tickers in parallel. Returns (updated, up_to_date, errors)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    tickers = load_universe_tickers()
    logger.info("Refreshing prices for %d tickers up to %s ...", len(tickers), target_date)

    provider = YFinanceProvider()
    updated = up_to_date = errors = 0

    with ThreadPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {pool.submit(refresh_ticker, t, target_date, provider): t for t in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                _, status = future.result()
                if status == "up_to_date" or status == "no_new_data":
                    up_to_date += 1
                elif status.startswith("ERROR"):
                    errors += 1
                    logger.warning("  %s: %s", ticker, status)
                else:
                    updated += 1
                    logger.debug("  %s: %s", ticker, status)
            except Exception as e:
                errors += 1
                logger.warning("  %s: exception %s", ticker, e)

    logger.info("Price refresh done: %d updated, %d already current, %d errors", updated, up_to_date, errors)
    return updated, up_to_date, errors


def rebuild_features() -> bool:
    """Run build_features.py for sp500 universe. Returns True on success."""
    import subprocess
    logger.info("Rebuilding features from refreshed prices ...")
    result = subprocess.run(
        [
            str(REPO_ROOT / ".venv" / "bin" / "python"),
            str(REPO_ROOT / "scripts" / "build_features.py"),
            "--config", str(REPO_ROOT / "config" / "base.yaml"),
            "--universe", str(REPO_ROOT / "config" / "universes" / "sp500.yaml"),
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=str(REPO_ROOT),
    )
    if result.returncode == 0:
        logger.info("Features rebuilt successfully")
        return True
    last_err = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "non-zero exit"
    logger.error("Feature rebuild FAILED: %s", last_err)
    return False


def check_freshness(target_date: date) -> None:
    """Log freshness of key feature files after rebuild."""
    for name in ["stock_features", "sector_features", "macro_features"]:
        path = FEATURES_DIR / f"{name}.parquet"
        if not path.exists():
            logger.warning("  %s: MISSING", name)
            continue
        try:
            df = pd.read_parquet(path)
            idx = df.index
            if hasattr(idx, "get_level_values"):
                last = pd.to_datetime(idx.get_level_values("date")).max().date()
            else:
                last = pd.to_datetime(idx).max().date()
            lag = (target_date - last).days
            status = "✓" if lag <= 3 else "⚠ STALE"
            logger.info("  %s: last date %s (lag %d days) %s", name, last, lag, status)
        except Exception as e:
            logger.warning("  %s: could not read — %s", name, e)


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental market data + feature refresh")
    parser.add_argument("--as-of", default=None, help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--skip-features", action="store_true", help="Refresh prices only, skip feature rebuild")
    args = parser.parse_args()

    target_date = date.fromisoformat(args.as_of) if args.as_of else date.today()

    updated, _, errors = refresh_all_prices(target_date)

    if args.skip_features:
        logger.info("Skipping feature rebuild (--skip-features)")
        return

    if updated == 0 and errors == 0:
        # Check if features are already fresh before rebuilding unnecessarily
        feat_path = FEATURES_DIR / "stock_features.parquet"
        if feat_path.exists():
            df = pd.read_parquet(feat_path)
            idx = df.index
            last = pd.to_datetime(
                idx.get_level_values("date") if hasattr(idx, "get_level_values") else idx
            ).max().date()
            if (target_date - last).days <= 3:
                logger.info("Prices and features already current — skipping feature rebuild")
                return

    ok = rebuild_features()
    if not ok:
        logger.error("Feature rebuild failed — signal pipeline will use stale features")
        sys.exit(1)

    logger.info("Data freshness check:")
    check_freshness(target_date)


if __name__ == "__main__":
    main()
