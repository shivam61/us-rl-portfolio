import pandas as pd
from typing import Dict, Any, Optional

class TargetGenerator:
    def __init__(
        self,
        data_dict: Dict[str, pd.DataFrame],
        forward_horizon: int = 21,
        sector_mapping: Optional[Dict[str, str]] = None,
    ):
        self.data_dict = data_dict
        self.forward_horizon = forward_horizon
        self.sector_mapping = sector_mapping or {}

    def generate(self) -> pd.DataFrame:
        targets_list = []
        for ticker, df in self.data_dict.items():
            close = df["adj_close"]
            fwd_ret = close.shift(-self.forward_horizon) / close - 1.0
            t_df = pd.DataFrame(index=close.index)
            t_df["target_fwd_ret"] = fwd_ret
            t_df["ticker"] = ticker
            targets_list.append(t_df)

        result = pd.concat(targets_list)
        result.set_index(["ticker"], append=True, inplace=True)
        result = result.reorder_levels(["date", "ticker"]).sort_index()

        # Cross-sectional rank [0, 1] within each date
        result["target_rank_cs"] = (
            result.groupby(level="date")["target_fwd_ret"].rank(pct=True)
        )

        # Sector-relative forward return (fwd_ret - sector mean fwd_ret on same date)
        if self.sector_mapping:
            tickers = result.index.get_level_values("ticker")
            result["_sector"] = tickers.map(self.sector_mapping)
            sector_mean = result.groupby(["date", "_sector"])["target_fwd_ret"].transform("mean")
            result["target_fwd_ret_sector_rel"] = result["target_fwd_ret"] - sector_mean
            result.drop(columns=["_sector"], inplace=True)
        else:
            result["target_fwd_ret_sector_rel"] = float("nan")

        return result
