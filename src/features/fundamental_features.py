import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from src.features.base import BaseFeatureGenerator
import logging

logger = logging.getLogger(__name__)

class FundamentalFeatureGenerator(BaseFeatureGenerator):
    def __init__(self, data_dict: Dict[str, pd.DataFrame], fundamentals_df: Optional[pd.DataFrame] = None, **kwargs: Any):
        super().__init__(data_dict, **kwargs)
        self.fundamentals_df = fundamentals_df
        
    def generate(self) -> pd.DataFrame:
        if self.fundamentals_df is None or self.fundamentals_df.empty:
            logger.warning("No fundamental data provided. Returning empty DataFrame.")
            return pd.DataFrame()
            
        features_list = []
        
        # Sort fundamentals for merge_asof
        fund_df = self.fundamentals_df.sort_values('filing_date').copy()
        
        for ticker, df in self.data_dict.items():
            ticker_fund = fund_df[fund_df['ticker'] == ticker].copy()
            if ticker_fund.empty:
                continue
                
            close = df["adj_close"].copy()
            
            # Create a dataframe for the prices
            price_df = pd.DataFrame({'date': close.index, 'adj_close': close.values})
            price_df = price_df.sort_values('date')
            
            # merge_asof requires sorted keys
            merged = pd.merge_asof(
                price_df, 
                ticker_fund,
                left_on='date',
                right_on='filing_date',
                direction='backward'
            )
            
            # Set index back to date
            merged.set_index('date', inplace=True)
            
            f_df = pd.DataFrame(index=merged.index)
            
            # Replace 0 with NaN for division
            eps_safe = merged['eps'].replace(0, np.nan)
            shares_safe = merged['shares_outstanding'].replace(0, np.nan)
            bv_safe = merged['book_value'].replace(0, np.nan)
            
            # Compute PE Ratio (Price / EPS)
            f_df['pe_ratio'] = merged['adj_close'] / eps_safe
            
            # Compute PB Ratio (Price / Book Value Per Share)
            bvps = merged['book_value'] / shares_safe
            f_df['pb_ratio'] = merged['adj_close'] / bvps.replace(0, np.nan)
            
            # Compute ROE (Net Income / Book Value)
            f_df['roe'] = merged['net_income'] / bv_safe
            
            # Compute EPS Growth YoY
            # Use 252 trading days to approximate 1 year ago, since merge_asof forward-fills
            f_df['eps_growth_yoy'] = merged['eps'] / merged['eps'].shift(252).replace(0, np.nan) - 1.0
            
            # Shift everything by 1 day to prevent leakage
            f_df = f_df.shift(1)
            
            f_df['ticker'] = ticker
            features_list.append(f_df)
            
        if not features_list:
            return pd.DataFrame()
            
        result = pd.concat(features_list)
        result.set_index(["ticker"], append=True, inplace=True)
        result = result.reorder_levels(["date", "ticker"]).sort_index()
        
        return result
