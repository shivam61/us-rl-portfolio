import argparse
import json
from pathlib import Path

import pandas as pd

from src.data.providers.canonical_fundamental_provider import (
    COLUMN_ALIASES,
    REQUIRED_CANONICAL_COLUMNS,
    OPTIONAL_CANONICAL_COLUMNS,
    CanonicalFundamentalProvider,
)


def read_frame(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input type: {path}")


def write_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df.to_parquet(path, index=False)
        return
    if suffix == ".csv":
        df.to_csv(path, index=False)
        return
    raise ValueError(f"Unsupported output type: {path}")


def load_mapping(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    with open(path, "r") as f:
        return json.load(f)


def normalize(df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    aliases = {**COLUMN_ALIASES, **{k.strip().lower(): v.strip().lower() for k, v in column_map.items()}}
    result = df.copy()
    result = result.rename(columns={col: aliases.get(col.strip().lower(), col.strip().lower()) for col in result.columns})
    if "ticker" in result.columns:
        result["ticker"] = result["ticker"].astype(str).str.upper().str.strip()
    if "filing_date" in result.columns:
        result["filing_date"] = pd.to_datetime(result["filing_date"], errors="coerce")
    keep = [col for col in REQUIRED_CANONICAL_COLUMNS + OPTIONAL_CANONICAL_COLUMNS if col in result.columns]
    result = result[keep]
    result = result.dropna(subset=["ticker", "filing_date"])
    result = result.sort_values(["ticker", "filing_date"]).drop_duplicates(["ticker", "filing_date"], keep="last")
    return result.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Normalize local fundamentals into the canonical research schema")
    parser.add_argument("--input", required=True, help="Source CSV/parquet")
    parser.add_argument("--output", required=True, help="Canonical output CSV/parquet")
    parser.add_argument("--column-map", help="Optional JSON mapping from source column names to canonical names")
    parser.add_argument("--min-ticker-coverage", type=float, default=0.80)
    parser.add_argument("--tickers", nargs="*", help="Optional expected ticker universe for coverage validation")
    args = parser.parse_args()

    source = read_frame(Path(args.input))
    canonical = normalize(source, load_mapping(args.column_map))
    CanonicalFundamentalProvider.validate_schema(canonical)

    if args.tickers:
        expected = {ticker.upper() for ticker in args.tickers}
        covered = set(canonical["ticker"].unique()) & expected
        coverage = len(covered) / max(len(expected), 1)
        if coverage < args.min_ticker_coverage:
            raise ValueError(
                f"Canonical ticker coverage {coverage:.2%} below threshold {args.min_ticker_coverage:.2%}"
            )

    write_frame(canonical, Path(args.output))
    print(f"Wrote {len(canonical):,} canonical rows to {args.output}")
    print(f"Tickers: {canonical['ticker'].nunique():,}")
    print(f"Date range: {canonical['filing_date'].min()} to {canonical['filing_date'].max()}")


if __name__ == "__main__":
    main()
