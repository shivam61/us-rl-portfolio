import yfinance as yf
import pandas as pd
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class YFinanceProvider:
    def __init__(self):
        pass

    def download_ticker(self, ticker: str, start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Download historical OHLCV data for a single ticker.
        """
        logger.info(f"Downloading data for {ticker} from {start_date} to {end_date or 'today'}")
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, multi_level_index=False)
        
        if df.empty:
            logger.warning(f"No data retrieved for {ticker}")
            return pd.DataFrame()
            
        # Standardize column names
        df.index.name = "date"
        df.columns = [c.lower() for c in df.columns]
        
        if "adj close" in df.columns:
            df = df.rename(columns={"adj close": "adj_close"})
            
        # Ensure we have the minimum required columns
        required_cols = ["open", "high", "low", "close", "volume", "adj_close"]
        for col in required_cols:
            if col not in df.columns:
                if col == "adj_close" and "close" in df.columns:
                    df["adj_close"] = df["close"]
                else:
                    logger.warning(f"Missing required column {col} for {ticker}")
                    
        return df[required_cols]

    def download_bulk(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> dict[str, pd.DataFrame]:
        """
        Download historical data for multiple tickers.
        Returns a dict of DataFrames.
        """
        result = {}
        for ticker in tickers:
            try:
                df = self.download_ticker(ticker, start_date, end_date)
                if not df.empty:
                    result[ticker] = df
            except Exception as e:
                logger.error(f"Failed to download {ticker}: {e}")
        return result
