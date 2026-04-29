from pathlib import Path
from typing import List, Optional
import logging

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_CANONICAL_COLUMNS = [
    "filing_date",
    "ticker",
    "eps",
    "book_value",
    "net_income",
    "shares_outstanding",
    "revenue",
    "gross_profit",
    "total_assets",
    "total_debt",
    "operating_income",
    "interest_expense",
    "operating_cash_flow",
]

OPTIONAL_CANONICAL_COLUMNS = [
    "cash_and_equivalents",
    "total_equity",
    "capex",
    "free_cash_flow",
    "ebitda",
    "analyst_eps_revision_1m",
    "analyst_eps_revision_3m",
    "earnings_surprise",
]

COLUMN_ALIASES = {
    "date": "filing_date",
    "filed_date": "filing_date",
    "accepted_date": "filing_date",
    "symbol": "ticker",
    "total_stockholder_equity": "book_value",
    "shareholders_equity": "book_value",
    "weighted_average_shares": "shares_outstanding",
    "shares": "shares_outstanding",
    "debt": "total_debt",
    "gross_profit_loss": "gross_profit",
    "operating_cashflow": "operating_cash_flow",
    "cash_flow_from_operations": "operating_cash_flow",
}


class CanonicalFundamentalProvider:
    def __init__(self, path: str):
        self.path = Path(path)

    def fetch_fundamentals(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        df = self._read()
        df = self._normalize(df)
        self.validate_schema(df)

        requested = set(tickers)
        df = df[df["ticker"].isin(requested)].copy()
        start = pd.Timestamp(start_date)
        df = df[df["filing_date"] >= start]
        if end_date is not None:
            df = df[df["filing_date"] <= pd.Timestamp(end_date)]
        return df.sort_values(["ticker", "filing_date"]).reset_index(drop=True)

    def _read(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Canonical fundamentals file not found: {self.path}")
        suffix = self.path.suffix.lower()
        if suffix == ".parquet":
            return pd.read_parquet(self.path)
        if suffix == ".csv":
            return pd.read_csv(self.path)
        raise ValueError(f"Unsupported canonical fundamentals file type: {self.path}")

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        normalized_cols = {
            col: COLUMN_ALIASES.get(col.strip().lower(), col.strip().lower())
            for col in result.columns
        }
        result = result.rename(columns=normalized_cols)
        if "ticker" in result.columns:
            result["ticker"] = result["ticker"].astype(str).str.upper().str.strip()
        if "filing_date" in result.columns:
            result["filing_date"] = pd.to_datetime(result["filing_date"], errors="coerce")
        if {"ticker", "filing_date"}.issubset(result.columns):
            result = (
                result.dropna(subset=["ticker", "filing_date"])
                .sort_values(["ticker", "filing_date"])
                .drop_duplicates(["ticker", "filing_date"], keep="last")
            )
        return result

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> None:
        missing = [col for col in REQUIRED_CANONICAL_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Canonical fundamentals missing required columns: {missing}")
        if df["filing_date"].isna().any():
            raise ValueError("Canonical fundamentals contain unparseable filing_date values")
        duplicate_count = int(df.duplicated(["ticker", "filing_date"]).sum())
        if duplicate_count:
            raise ValueError(f"Canonical fundamentals contain {duplicate_count} duplicate ticker/filing_date rows")
