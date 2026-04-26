import os
import pandas as pd
from typing import List, Dict, Optional
import logging
from pathlib import Path
from src.data.providers.yfinance_provider import YFinanceProvider

logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, cache_dir: str, force_download: bool = False):
        self.cache_dir = Path(cache_dir)
        self.raw_dir = self.cache_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.force_download = force_download
        self.provider = YFinanceProvider()

    def fetch_universe_data(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        data_dict = {}
        for ticker in tickers:
            file_path = self.raw_dir / f"{ticker}.parquet"
            if file_path.exists() and not self.force_download:
                logger.debug(f"Loading {ticker} from cache.")
                df = pd.read_parquet(file_path)
                data_dict[ticker] = df
            else:
                df = self.provider.download_ticker(ticker, start_date, end_date)
                if not df.empty:
                    df.to_parquet(file_path)
                    data_dict[ticker] = df
        return data_dict

    def build_matrices(self, data_dict: Dict[str, pd.DataFrame], column: str = "adj_close") -> pd.DataFrame:
        """
        Build a 2D matrix (dates x tickers) for a specific column.
        """
        series_list = []
        for ticker, df in data_dict.items():
            if column in df.columns:
                s = df[column].rename(ticker)
                series_list.append(s)
                
        if not series_list:
            return pd.DataFrame()
            
        matrix = pd.concat(series_list, axis=1)
        matrix.index = pd.to_datetime(matrix.index)
        matrix.sort_index(inplace=True)
        return matrix
        
    def build_all_matrices(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        return {
            "open": self.build_matrices(data_dict, "open"),
            "close": self.build_matrices(data_dict, "close"),
            "adj_close": self.build_matrices(data_dict, "adj_close"),
            "volume": self.build_matrices(data_dict, "volume")
        }
