import argparse
import logging
import pandas as pd
from pathlib import Path
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.features.stock_features import StockFeatureGenerator
from src.features.sector_features import SectorFeatureGenerator
from src.features.macro_features import MacroFeatureGenerator
from src.features.fundamental_features import FundamentalFeatureGenerator
from src.labels.targets import TargetGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Build features and labels")
    parser.add_argument("--config", type=str, required=True, help="Path to base config")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml", help="Path to universe config")
    args = parser.parse_args()
    
    base_config, universe_config = load_config(args.config, args.universe)
    cache_dir = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)
    
    ingestion = DataIngestion(
        cache_dir=base_config.data.cache_dir,
        force_download=False,
        fundamental_provider=base_config.fundamentals.provider,
        fundamental_path=base_config.fundamentals.path,
    )
    
    all_tickers = list(universe_config.tickers.keys()) + \
                  universe_config.sector_etfs + \
                  universe_config.macro_etfs + \
                  [universe_config.benchmark, universe_config.vix_proxy]
    all_tickers = list(set(all_tickers))
    
    logger.info("Loading raw data from cache...")
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    
    # Load fundamental data from cache
    stock_tickers = list(universe_config.tickers.keys())
    fundamentals_df = ingestion.fetch_universe_fundamentals(
        tickers=stock_tickers,
        start_date=base_config.backtest.start_date,
        cache_key=universe_config.name,
    )
    
    sector_mapping = dict(universe_config.tickers)  # {ticker: sector_etf}

    logger.info("Generating stock features...")
    stock_fg = StockFeatureGenerator(data_dict, benchmark_ticker=universe_config.benchmark, sector_mapping=sector_mapping)
    stock_features = stock_fg.generate()
    
    logger.info("Generating fundamental features...")
    fund_fg = FundamentalFeatureGenerator(data_dict, fundamentals_df=fundamentals_df)
    fund_features = fund_fg.generate()
    
    if not fund_features.empty:
        # Merge fundamental features into stock features
        stock_features = stock_features.join(fund_features, how="left")
    
    logger.info("Generating sector features...")
    sector_fg = SectorFeatureGenerator(data_dict, sector_etfs=universe_config.sector_etfs)
    sector_features = sector_fg.generate()
    
    logger.info("Generating macro features...")
    macro_fg = MacroFeatureGenerator(data_dict, benchmark_ticker=universe_config.benchmark, vix_proxy=universe_config.vix_proxy)
    macro_features = macro_fg.generate()
    
    logger.info("Generating labels...")
    tg = TargetGenerator(data_dict, forward_horizon=21, sector_mapping=sector_mapping)
    targets = tg.generate()
    
    logger.info("Saving artifacts...")
    stock_features.to_parquet(features_dir / "stock_features.parquet")
    sector_features.to_parquet(features_dir / "sector_features.parquet")
    macro_features.to_parquet(features_dir / "macro_features.parquet")
    targets.to_parquet(features_dir / "targets.parquet")
    universe_key = universe_config.name.lower().replace(" ", "_")
    stock_features.to_parquet(features_dir / f"stock_features_{universe_key}.parquet")
    sector_features.to_parquet(features_dir / f"sector_features_{universe_key}.parquet")
    macro_features.to_parquet(features_dir / f"macro_features_{universe_key}.parquet")
    targets.to_parquet(features_dir / f"targets_{universe_key}.parquet")
    
    logger.info("Feature building complete.")

if __name__ == "__main__":
    main()
