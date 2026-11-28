"""Point-in-time membership price coverage before and after the free-source ingest.

Uses the saved PIT mask (data/artifacts/sp500_pit_membership_mask.parquet, built by
scripts/build_sp500_pit_membership.py) and the same rule as its coverage_report: a member is
priced when <cache>/<TICKER>.parquet exists and the ticker has no -YYMMDD suffix. For each year
the last trading day in the mask is used, as in the builder's printout.

Columns: members, and priced share for (1) original cache = data/raw minus the verify2 Tier A
files, (2) current data/raw (adds Tier A), (3) data/raw + data/raw_tierB (adds Tier B).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
YEARS = list(range(2008, 2027))


def priced_set(cache: Path) -> set[str]:
    return {p.stem for p in cache.glob("*.parquet") if not re.search(r"-\d{6}$", p.stem)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mask", type=Path, default=REPO / "data" / "artifacts" / "sp500_pit_membership_mask.parquet")
    ap.add_argument("--raw", type=Path, default=REPO / "data" / "raw")
    ap.add_argument("--tierb", type=Path, default=REPO / "data" / "raw_tierB" / "raw")
    ap.add_argument("--tiera-tickers", type=str, default="BF.B,VEEV,FDXF,FLEX,HONA")
    ap.add_argument("--out", type=Path, default=REPO / "runs_ingest" / "coverage_before_after.csv")
    args = ap.parse_args()

    mask = pd.read_parquet(args.mask)
    mask.index = pd.DatetimeIndex(pd.to_datetime(mask.index))
    tier_a = {t for t in args.tiera_tickers.split(",") if t}
    now = priced_set(args.raw)
    original = now - tier_a
    tier_b = priced_set(args.tierb) if args.tierb.exists() else set()
    after = now | tier_b

    rows = []
    for year in YEARS:
        sub = mask[mask.index.year == year]
        if sub.empty:
            continue
        d = sub.index[-1]
        members = set(sub.columns[sub.loc[d].fillna(False).astype(bool).to_numpy()])
        n = len(members)
        rows.append({
            "year": year,
            "date": str(d.date()),
            "members": n,
            "priced_original_cache": len(members & original),
            "priced_current_data_raw": len(members & now),
            "priced_plus_tierB": len(members & after),
            "share_original_cache": round(len(members & original) / n, 4),
            "share_current_data_raw": round(len(members & now) / n, 4),
            "share_plus_tierB": round(len(members & after) / n, 4),
            "tierB_names_added_this_year": len((members & tier_b) - now),
        })
    out = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
