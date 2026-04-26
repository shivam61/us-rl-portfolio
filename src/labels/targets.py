import pandas as pd
from typing import Dict, Any

class TargetGenerator:
    def __init__(self, data_dict: Dict[str, pd.DataFrame], forward_horizon: int = 21):
        self.data_dict = data_dict
        self.forward_horizon = forward_horizon
        
    def generate(self) -> pd.DataFrame:
        """
        Generates forward returns for all assets.
        For date T, the target is Return(T -> T + horizon).
        """
        targets_list = []
        for ticker, df in self.data_dict.items():
            close = df["adj_close"]
            
            # Future return: (Close(t+horizon) / Close(t)) - 1
            # We use shift(-horizon) to align future return with current date T
            fwd_ret = close.shift(-self.forward_horizon) / close - 1.0
            
            t_df = pd.DataFrame(index=close.index)
            t_df["target_fwd_ret"] = fwd_ret
            t_df["ticker"] = ticker
            
            targets_list.append(t_df)
            
        result = pd.concat(targets_list)
        result.set_index(["ticker"], append=True, inplace=True)
        result = result.reorder_levels(["date", "ticker"]).sort_index()
        return result
