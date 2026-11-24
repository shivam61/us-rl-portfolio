import argparse
import logging
import sys
from pathlib import Path

# Allow `python scripts/download_data.py` from the repo root without PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config.loader import load_config
from src.data.ingestion import DataIngestion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Download historical data")
    parser.add_argument("--config", type=str, required=True, help="Path to base config")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml", help="Path to universe config")
    args = parser.parse_args()
    
    base_config, universe_config = load_config(args.config, args.universe)
    
    # Collect all tickers
    all_tickers = list(universe_config.tickers.keys()) + \
                  universe_config.sector_etfs + \
                  universe_config.macro_etfs + \
                  [universe_config.benchmark, universe_config.vix_proxy]
                  
    # Remove duplicates
    all_tickers = list(set(all_tickers))
    
    logger.info(f"Downloading data for {len(all_tickers)} tickers...")
    ingestion = DataIngestion(
        cache_dir=base_config.data.cache_dir,
        force_download=base_config.data.force_download,
        fundamental_provider=base_config.fundamentals.provider,
        fundamental_path=base_config.fundamentals.path,
    )
    
    # Fetch data
    _ = ingestion.fetch_universe_data(
        tickers=all_tickers,
        start_date=base_config.backtest.start_date,
        end_date=base_config.backtest.end_date,
        # Threaded yfinance downloads intermittently return truncated or
        # malformed frames, and the cache does not validate them. Fetch serially.
        n_workers=1,
    )

    logger.info("Downloading fundamental data...")
    stock_tickers = list(universe_config.tickers.keys())
    _ = ingestion.fetch_universe_fundamentals(
        tickers=stock_tickers,
        start_date=base_config.backtest.start_date,
        end_date=base_config.backtest.end_date,
        cache_key=universe_config.name,
    )
    
    logger.info("Data download complete.")

if __name__ == "__main__":
    main()
