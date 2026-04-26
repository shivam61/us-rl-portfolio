import argparse
import logging
import pandas as pd
from pathlib import Path
from src.config.loader import load_config
from src.data.ingestion import DataIngestion
from src.backtest.walk_forward import WalkForwardEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Generate Current Recommended Portfolio")
    parser.add_argument("--config", type=str, required=True, help="Path to base config")
    parser.add_argument("--universe", type=str, default="config/universes/sp100.yaml", help="Path to universe config")
    args = parser.parse_args()
    
    base_config, universe_config = load_config(args.config, args.universe)
    cache_dir = Path(base_config.data.cache_dir)
    features_dir = cache_dir / "features"
    artifacts_dir = cache_dir / "artifacts"
    
    # We assume data is freshly downloaded and features are built!
    # Run download_data.py and build_features.py before this!
    logger.info("Loading latest features and data...")
    stock_features = pd.read_parquet(features_dir / "stock_features.parquet")
    macro_features = pd.read_parquet(features_dir / "macro_features.parquet")
    targets = pd.read_parquet(features_dir / "targets.parquet")
    
    ingestion = DataIngestion(cache_dir=base_config.data.cache_dir, force_download=False)
    all_tickers = list(universe_config.tickers.keys())
    data_dict = ingestion.fetch_universe_data(tickers=all_tickers, start_date=base_config.backtest.start_date)
    prices = ingestion.build_matrices(data_dict, column="adj_close").ffill()
    
    engine = WalkForwardEngine(
        config=base_config,
        universe_config=universe_config,
        stock_features=stock_features,
        macro_features=macro_features,
        targets=targets,
        prices=prices
    )
    
    latest_date = prices.index[-1]
    logger.info(f"Generating recommendation for {latest_date}")
    
    # Generate weights
    current_weights = pd.Series(0.0, index=all_tickers)
    target_weights = engine._generate_target_weights(latest_date, current_weights)
    
    # Summary
    target_weights = target_weights[target_weights > 0.001].sort_values(ascending=False)
    cash = 1.0 - target_weights.sum()
    
    print("\n" + "="*50)
    print(f"CURRENT PORTFOLIO RECOMMENDATION - {latest_date.date()}")
    print("="*50)
    print(f"Cash Allocation: {cash*100:.2f}%")
    print("\nTop Holdings:")
    for ticker, weight in target_weights.head(15).items():
        print(f"{ticker:>6} : {weight*100:5.2f}%")
    print("="*50)
    
    target_weights.to_csv(artifacts_dir / "current_portfolio.csv")
    logger.info("Saved to artifacts/current_portfolio.csv")

if __name__ == "__main__":
    main()
