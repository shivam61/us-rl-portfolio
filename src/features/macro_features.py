import pandas as pd
import numpy as np
from typing import Dict, Any
from src.features.base import BaseFeatureGenerator

class MacroFeatureGenerator(BaseFeatureGenerator):
    def __init__(self, data_dict: Dict[str, pd.DataFrame], benchmark_ticker: str = "SPY", vix_proxy: str = "^VIX", **kwargs: Any):
        super().__init__(data_dict, **kwargs)
        self.benchmark_ticker = benchmark_ticker
        self.vix_proxy = vix_proxy
        
    def generate(self) -> pd.DataFrame:
        if self.benchmark_ticker not in self.data_dict:
            return pd.DataFrame()
            
        spy_close = self.data_dict[self.benchmark_ticker]["adj_close"]
        f_df = pd.DataFrame(index=spy_close.index)
        
        # SPY features
        f_df["spy_ret_1m"] = spy_close.pct_change(21)
        f_df["spy_ret_6m"] = spy_close.pct_change(126)
        
        rolling_max = spy_close.rolling(252, min_periods=1).max()
        f_df["spy_drawdown"] = spy_close / rolling_max - 1.0
        f_df["realized_market_vol_63d"] = spy_close.pct_change().rolling(63).std() * np.sqrt(252)
        
        # VIX
        if self.vix_proxy in self.data_dict:
            vix_close = self.data_dict[self.vix_proxy]["adj_close"]
            # Align indices
            vix_close = vix_close.reindex(spy_close.index).ffill()
            f_df["vix_level"] = vix_close
            f_df["vix_percentile_1y"] = vix_close.rolling(252).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1])
        else:
            f_df["vix_level"] = 20.0
            f_df["vix_percentile_1y"] = 0.5
            
        # Regime labeling heuristic
        def label_regime(row):
            if row["spy_drawdown"] < -0.15:
                return 2  # CRASH
            elif row["realized_market_vol_63d"] > 0.25:
                return 1  # HIGH_VOL
            elif row["spy_ret_6m"] > 0.10:
                return 4  # TRENDING
            else:
                return 0  # SIDEWAYS / LOW_VOL
                
        f_df["market_regime"] = f_df.apply(label_regime, axis=1)
        
        f_df = f_df.shift(1)
        return f_df
