import pandas as pd
import numpy as np
import yaml
from pathlib import Path

def build_pit_universe(config_path: str, output_path: str):
    print(f"Loading universe from {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    tickers = list(config['tickers'].keys())
    
    # Date range 2006-01-01 to 2026-12-31
    dates = pd.date_range(start='2006-01-01', end='2026-12-31', freq='B')
    
    # Start with all True
    df = pd.DataFrame(True, index=dates, columns=tickers)
    
    # Simulate a few additions/removals
    np.random.seed(42)
    
    # Pick 5 tickers to "add" later
    late_additions = np.random.choice(tickers, size=5, replace=False)
    for ticker in late_additions:
        add_date = pd.Timestamp('2006-01-01') + pd.to_timedelta(np.random.randint(1000, 4000), unit='D')
        df.loc[:add_date, ticker] = False
        print(f"Ticker {ticker} added on {add_date.date()}")
        
    # Pick 5 tickers to "remove" earlier
    remaining = [t for t in tickers if t not in late_additions]
    early_removals = np.random.choice(remaining, size=5, replace=False)
    for ticker in early_removals:
        remove_date = pd.Timestamp('2026-12-31') - pd.to_timedelta(np.random.randint(1000, 4000), unit='D')
        df.loc[remove_date:, ticker] = False
        print(f"Ticker {ticker} removed on {remove_date.date()}")

    # Ensure output directory exists
    out_dir = Path(output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as parquet
    df.to_parquet(output_path)
    print(f"Saved PIT universe mask to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/universes/sp100.yaml")
    parser.add_argument("--output", type=str, default="data/artifacts/universe_mask.parquet")
    args = parser.parse_args()
    
    build_pit_universe(args.config, args.output)
