import pandas as pd
import numpy as np
from typing import Dict, Any, List

class BaselineEngine:
    def __init__(self, config: Any, universe_config: Any, prices_dict: Dict[str, pd.DataFrame]):
        self.config = config
        self.universe_config = universe_config
        self.prices_adj_close = prices_dict["adj_close"].ffill()
        self.benchmark = universe_config.benchmark
        
    def run_baselines(self, rebalance_dates: List[pd.Timestamp]) -> pd.DataFrame:
        history_df = pd.DataFrame(index=self.prices_adj_close.index)
        
        # 1. SPY Buy and Hold
        if self.benchmark in self.prices_adj_close.columns:
            spy_prices = self.prices_adj_close[self.benchmark]
            start_date = rebalance_dates[0] if rebalance_dates else spy_prices.index[0]
            # Use asof to safely get the closest price before or on the start_date
            start_price = spy_prices.asof(start_date)
            history_df["SPY_BnH"] = (spy_prices / start_price) * self.config.portfolio.initial_capital
            
        # 2. Equal Weight Universe
        tickers = list(self.universe_config.tickers.keys())
        if tickers:
            univ_prices = self.prices_adj_close[tickers]
            returns = univ_prices.pct_change().fillna(0)
            
            # Simple daily rebalanced equal weight for baseline
            ew_ret = returns.mean(axis=1)
            ew_nav = (1 + ew_ret).cumprod()
            
            # Rebase to initial capital at first rebalance date
            if rebalance_dates:
                start_date = rebalance_dates[0]
                # Find the index position of the closest valid date
                idx = ew_nav.index.get_indexer([start_date], method='ffill')[0]
                if idx >= 0:
                    ew_nav = ew_nav / ew_nav.iloc[idx]
                    ew_nav.iloc[:idx] = np.nan
            
            history_df["Equal_Weight"] = ew_nav * self.config.portfolio.initial_capital
            
        # Add more baselines (top-20 momentum, sector rotation) here as needed.
        
        return history_df.dropna(how='all')
