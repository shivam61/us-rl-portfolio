"""Build a point-in-time S&P 500 membership mask from a historical components file.

Source: fja05680/sp500, "S&P 500 Historical Components & Changes (Updated).csv"
(MIT License, Copyright 2019-2020 Farrell J. Aultman). Download the file yourself and pass its path;
this script does not fetch anything.

Output: a daily (trading-date x ticker) boolean frame. A ticker is True on a date when it was
in the index on that date, using the latest snapshot on or before that date.

Coverage caveat: tickers without price history in data/raw (delisted or renamed names) are members in
the mask but cannot be priced. The mask therefore does not remove survivorship bias on its own; use
the coverage report printed by this script to size it.
"""
import argparse
import re
from pathlib import Path

import pandas as pd


def load_snapshots(components_csv: Path) -> dict:
    comp = pd.read_csv(components_csv, parse_dates=["date"]).sort_values("date")
    snaps = {}
    for _, row in comp.iterrows():
        tickers = {t.strip() for t in str(row["tickers"]).split(",") if t.strip()}
        snaps[pd.Timestamp(row["date"])] = tickers
    return snaps


def build_mask(snaps: dict, trading_dates: pd.DatetimeIndex, columns: pd.Index) -> pd.DataFrame:
    mask = pd.DataFrame(False, index=trading_dates, columns=columns)
    snap_dates = sorted(snaps)
    j, current = 0, set()
    for d in trading_dates:
        while j < len(snap_dates) and snap_dates[j] <= d:
            current = snaps[snap_dates[j]]
            j += 1
        mask.loc[d, [c for c in columns if c in current]] = True
    return mask


def coverage_report(snaps: dict, cached: set, start: str, end: str) -> pd.DataFrame:
    rows = []
    for d in sorted(snaps):
        if d < pd.Timestamp(start) or d > pd.Timestamp(end):
            continue
        members = snaps[d]
        priced = {t for t in members if t in cached and not re.search(r"-\d{6}$", t)}
        rows.append(dict(date=d, members=len(members), priced=len(priced)))
    df = pd.DataFrame(rows)
    df["coverage"] = df["priced"] / df["members"]
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--components", required=True, type=Path)
    ap.add_argument("--prices-dir", default="data/raw", type=Path)
    ap.add_argument("--output", default="data/artifacts/sp500_pit_membership_mask.parquet", type=Path)
    ap.add_argument("--start", default="2008-01-01")
    ap.add_argument("--end", default="2026-04-24")
    args = ap.parse_args()

    cached = {p.stem for p in args.prices_dir.glob("*.parquet")}
    snaps = load_snapshots(args.components)
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(pd.read_parquet(args.prices_dir / "SPY.parquet").index)))
    dates = dates[(dates >= pd.Timestamp(args.start)) & (dates <= pd.Timestamp(args.end))]
    columns = pd.Index(sorted(set().union(*snaps.values())))
    mask = build_mask(snaps, dates, columns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    mask.to_parquet(args.output)

    cov = coverage_report(snaps, cached, args.start, args.end)
    print(f"mask {mask.shape} -> {args.output}")
    for year in (2008, 2012, 2016, 2020, 2024, 2026):
        sub = cov[cov["date"].dt.year == year]
        if not sub.empty:
            r = sub.iloc[-1]
            print(f"{year}: members {r.members}, priced {r.priced}, coverage {r.coverage:.0%}")
    print(f"mean coverage {args.start}..{args.end}: {cov['coverage'].mean():.0%}")


if __name__ == "__main__":
    main()
