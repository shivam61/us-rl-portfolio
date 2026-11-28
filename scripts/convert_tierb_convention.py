"""Convert Tier B price files to the main cache convention (close == adj_close).

Main cache (data/raw) stores already-adjusted prices: close == adj_close. Tier B files keep the raw
close and a separate adj_close. Per row, open/high/low/close are scaled by adj_close / close, so
close becomes adj_close exactly. Volume, index and dtypes are unchanged. Inputs are never modified.

Usage (from repo root):
    .venv/bin/python -I scripts/convert_tierb_convention.py \
        --src data/raw_tierB/raw --dst runs_final/raw_tierB_adj/raw --summary runs_final/tierb_convention.csv
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

PRICE_COLS = ["open", "high", "low", "close"]


def convert_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with OHLC scaled per row so that close equals adj_close."""
    close = df["close"].astype(float)
    adj = df["adj_close"].astype(float)
    if close.isna().any() or adj.isna().any():
        raise ValueError("close or adj_close has nulls")
    if (close <= 0).any() or (adj <= 0).any():
        raise ValueError("non-positive close or adj_close")
    factor = (adj / close).to_numpy()
    out = df.copy()
    for col in ["open", "high", "low"]:
        out[col] = (df[col].astype(float).to_numpy() * factor).astype(df[col].dtype)
    out["close"] = adj.to_numpy().astype(df["close"].dtype)
    return out


def convert_file(src: Path, dst: Path) -> dict:
    df = pd.read_parquet(src)
    out = convert_frame(df)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dst)
    factor = (df["adj_close"] / df["close"]).astype(float)
    return dict(
        ticker=src.stem,
        rows=len(df),
        first=str(df.index.min().date()),
        last=str(df.index.max().date()),
        rows_adjusted=int((np.abs(factor - 1) > 1e-12).sum()),
        min_factor=float(factor.min()),
        max_factor=float(factor.max()),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--dst", required=True, type=Path)
    ap.add_argument("--summary", type=Path, default=None)
    args = ap.parse_args()
    if str(args.dst.resolve()).startswith(str(Path("data").resolve())):
        raise SystemExit("refusing to write under data/")
    rows = [convert_file(p, args.dst / p.name) for p in sorted(args.src.glob("*.parquet"))]
    summary = pd.DataFrame(rows)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(args.summary, index=False)
    print(f"converted {len(summary)} files -> {args.dst}; rows with adjustment: {int((summary.rows_adjusted > 0).sum())} files")


if __name__ == "__main__":
    main()
