import pandas as pd
from typing import Dict, Any, List
from src.features.base import BaseFeatureGenerator

class SectorFeatureGenerator(BaseFeatureGenerator):
    def __init__(self, data_dict: Dict[str, pd.DataFrame], sector_etfs: List[str], **kwargs: Any):
        super().__init__(data_dict, **kwargs)
        self.sector_etfs = sector_etfs
        
    def generate(self) -> pd.DataFrame:
        features_list = []
        for ticker in self.sector_etfs:
            if ticker not in self.data_dict:
                continue
            
            close = self.data_dict[ticker]["adj_close"]
            f_df = pd.DataFrame(index=close.index)
            
            f_df["sector_ret_1m"] = close.pct_change(21)
            f_df["sector_ret_3m"] = close.pct_change(63)
            f_df["sector_ret_6m"] = close.pct_change(126)
            f_df["sector_ret_12m"] = close.pct_change(252)
            
            f_df["sector_volatility_63d"] = close.pct_change().rolling(63).std()
            
            f_df = f_df.shift(1)
            f_df["ticker"] = ticker
            features_list.append(f_df)
            
        if not features_list:
            return pd.DataFrame()
            
        result = pd.concat(features_list)
        result.set_index(["ticker"], append=True, inplace=True)
        result = result.reorder_levels(["date", "ticker"]).sort_index()
        return result
