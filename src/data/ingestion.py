import hashlib
import re
import pandas as pd
from typing import List, Dict, Optional
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.data.providers.yfinance_provider import YFinanceProvider
from src.data.providers.fundamental_provider import FundamentalProvider

logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, cache_dir: str, force_download: bool = False):
        self.cache_dir = Path(cache_dir)
        self.raw_dir = self.cache_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.force_download = force_download
        self.provider = YFinanceProvider()
        self.fundamental_provider = FundamentalProvider()

    def _fundamentals_cache_path(self, tickers: List[str], cache_key: Optional[str] = None) -> Path:
        if cache_key:
            safe_key = re.sub(r"[^A-Za-z0-9_.-]+", "_", cache_key).strip("_").lower()
        else:
            digest = hashlib.sha1(",".join(sorted(set(tickers))).encode("utf-8")).hexdigest()[:12]
            safe_key = f"tickers_{digest}"
        return self.raw_dir / f"fundamentals_{safe_key}.parquet"

    def fetch_universe_fundamentals(
        self,
        tickers: List[str],
        start_date: str,
        end_date: Optional[str] = None,
        cache_key: Optional[str] = None,
    ) -> pd.DataFrame:
        requested = sorted(set(tickers))
        file_path = self._fundamentals_cache_path(requested, cache_key=cache_key)
        if file_path.exists() and not self.force_download:
            logger.debug("Loading fundamentals from cache: %s", file_path)
            df = pd.read_parquet(file_path)
            if "ticker" in df.columns:
                cached = set(df["ticker"].dropna().astype(str).unique())
                missing = sorted(set(requested) - cached)
                if missing:
                    logger.warning(
                        "Fundamental cache %s covers %d/%d requested tickers; missing sample=%s",
                        file_path,
                        len(cached & set(requested)),
                        len(requested),
                        missing[:10],
                    )
            return df
            
        df = self.fundamental_provider.fetch_fundamentals(requested, start_date, end_date)
        if not df.empty:
            df.to_parquet(file_path)
        return df

    def fetch_universe_data(self, tickers: List[str], start_date: str,
                           end_date: Optional[str] = None,
                           n_workers: int = 8) -> Dict[str, pd.DataFrame]:
        data_dict = {}
        to_download = []

        for ticker in tickers:
            file_path = self.raw_dir / f"{ticker}.parquet"
            if file_path.exists() and not self.force_download:
                logger.debug(f"Loading {ticker} from cache.")
                data_dict[ticker] = pd.read_parquet(file_path)
            else:
                to_download.append(ticker)

        if to_download:
            logger.info(f"Downloading {len(to_download)} tickers with {n_workers} workers...")

            def _fetch_one(ticker: str):
                try:
                    df = self.provider.download_ticker(ticker, start_date, end_date)
                    if not df.empty:
                        df.to_parquet(self.raw_dir / f"{ticker}.parquet")
                    return ticker, df
                except Exception as e:
                    logger.error(f"Failed to download {ticker}: {e}")
                    return ticker, pd.DataFrame()

            with ThreadPoolExecutor(max_workers=n_workers) as executor:
                futures = {executor.submit(_fetch_one, t): t for t in to_download}
                for future in as_completed(futures):
                    try:
                        ticker, df = future.result()
                        if not df.empty:
                            data_dict[ticker] = df
                    except Exception as e:
                        logger.error(f"Unexpected error for {futures[future]}: {e}")

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
