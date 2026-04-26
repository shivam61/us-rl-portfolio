import pandas as pd
import numpy as np
from typing import Dict, Any
from src.features.base import BaseFeatureGenerator
import logging

logger = logging.getLogger(__name__)

class StockFeatureGenerator(BaseFeatureGenerator):
    def __init__(self, data_dict: Dict[str, pd.DataFrame], benchmark_ticker: str = "SPY", **kwargs: Any):
        super().__init__(data_dict, **kwargs)
        self.benchmark_ticker = benchmark_ticker
        
    def generate(self) -> pd.DataFrame:
        features_list = []
        
        # Prepare benchmark data if available
        spy_returns = None
        if self.benchmark_ticker in self.data_dict:
            spy_adj_close = self.data_dict[self.benchmark_ticker]["adj_close"]
            spy_returns = spy_adj_close.pct_change()
            
        for ticker, df in self.data_dict.items():
            if ticker == self.benchmark_ticker:
                continue # Skip benchmark for stock features
                
            close = df["adj_close"]
            volume = df["volume"]
            
            f_df = pd.DataFrame(index=close.index)
            
            # Returns (lagged by 1 day inherently because we shift the whole DF at the end)
            returns = close.pct_change()
            f_df["ret_1m"] = close.pct_change(21)
            f_df["ret_3m"] = close.pct_change(63)
            f_df["ret_6m"] = close.pct_change(126)
            f_df["ret_12m"] = close.pct_change(252)
            f_df["ret_12m_ex_1m"] = close.shift(21).pct_change(231)
            
            # Moving averages
            ma50 = close.rolling(50).mean()
            ma200 = close.rolling(200).mean()
            f_df["above_50dma"] = (close > ma50).astype(int)
            f_df["above_200dma"] = (close > ma200).astype(int)
            f_df["ma_50_200_ratio"] = ma50 / ma200
            
            # 52w high
            high_52w = close.rolling(252).max()
            f_df["price_to_52w_high"] = close / high_52w
            
            # Volatility
            f_df["volatility_21d"] = returns.rolling(21).std() * np.sqrt(252)
            f_df["volatility_63d"] = returns.rolling(63).std() * np.sqrt(252)
            
            downside_rets = returns.copy()
            downside_rets[downside_rets > 0] = 0
            f_df["downside_vol_63d"] = downside_rets.rolling(63).std() * np.sqrt(252)
            
            # Drawdown
            rolling_max = close.rolling(63, min_periods=1).max()
            drawdowns = close / rolling_max - 1.0
            f_df["max_drawdown_63d"] = drawdowns.rolling(63).min()
            
            # Volume
            f_df["avg_dollar_volume_63d"] = (close * volume).rolling(63).mean()
            
            # Beta & Relative Strength
            if spy_returns is not None:
                cov = returns.rolling(63).cov(spy_returns)
                var = spy_returns.rolling(63).var()
                f_df["beta_to_spy_63d"] = cov / var
                f_df["relative_strength_vs_spy_63d"] = f_df["ret_3m"] - spy_returns.pct_change(63)
            else:
                f_df["beta_to_spy_63d"] = 1.0
                f_df["relative_strength_vs_spy_63d"] = 0.0
                
            # Shift everything by 1 day to prevent leakage
            # If we predict return for day T, we use features up to T-1
            f_df = f_df.shift(1)
            
            f_df["ticker"] = ticker
            features_list.append(f_df)
            
        result = pd.concat(features_list)
        result.set_index(["ticker"], append=True, inplace=True)
        result = result.reorder_levels(["date", "ticker"]).sort_index()
        
        # Cross-sectional ranking within the day
        result["liquidity_rank"] = result.groupby(level="date")["avg_dollar_volume_63d"].rank(pct=True)
        
        return result
