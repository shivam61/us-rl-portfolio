"""Build a point-in-time S&P 500 membership mask from a historical components file.

Source: fja05680/sp500, "S&P 500 Historical Components & Changes (Updated).csv"
(MIT License, Copyright 2019-2020 Farrell J. Aultman). Download the file yourself and pass its path;
this script does not fetch anything.

Output: a daily (trading-date x ticker) boolean frame. A ticker is True on a date when it was
in the index on that date, using the latest snapshot on or before that date.

Corrected mask (--windows, --price-dir): on top of the snapshot mask,
  1. LAST_MEMBER_OVERRIDES: snapshot last-member dates that a press release corrects.
  2. Tier B names (every ticker in the usable-windows CSV) are True only inside their usable window,
     i.e. [usable_start, usable_end] intersected with the corrected stint. Their snapshot membership
     is ignored. Multiple rows per ticker give multiple windows.
  3. Price gate (--price-dir): a ticker is False on any date with no adj_close in its price file.
     Price-missing days are dropped from the mask, not filled.
The override table (one row per overridden ticker) is written to --overrides-out.

Coverage caveat: tickers without price history (delisted or renamed names) are members in
the mask but cannot be priced. The mask therefore does not remove survivorship bias on its own; use
the coverage report printed by this script to size it.
"""
import argparse
import re
from pathlib import Path

import pandas as pd

# Snapshot last-member corrections: ticker -> (last member date, reason). Applied before Tier B windows.
LAST_MEMBER_OVERRIDES = {
    "FMC": (
        "2025-03-21",
        "snapshot has no row between 2024-12-23 and 2025-03-24; S&P release 2025-03-07, removal effective 2025-03-24",
    ),
}

# Names whose press-confirmed stint is longer than the snapshot. Their Tier B windows set the dates.
PRESS_LONGER_THAN_SNAPSHOT = ["AAP", "ETSY", "TFX", "VNO", "FLS", "BHF", "OGN"]


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


def parse_leading_date(text) -> pd.Timestamp | None:
    """Return the ISO date at the start of a notes-style cell, or None (e.g. 'ongoing ...')."""
    m = re.match(r"\s*(\d{4}-\d{2}-\d{2})", str(text))
    return pd.Timestamp(m.group(1)) if m else None


def load_tierb_windows(windows_csv: Path) -> pd.DataFrame:
    """One row per usable window: ticker, window_start, window_end, verdict, batch.

    window = [usable_start, usable_end]. The usable columns are the reviewed answer and already sit
    inside the press-corrected stint. Intersecting with the stint text would be wrong: for PVH, PENN,
    SEDG and SLG the stint_end text is the stale snapshot date (e.g. PENN 2022-06-28) while usable_end
    is the corrected 2022-09-16. The stint text is only checked: a usable_start before stint_start raises.
    Rows with no usable dates (FMC 1996 row, outside the batch) are dropped.
    """
    w = pd.read_csv(windows_csv, dtype=str)
    rows = []
    for _, r in w.iterrows():
        if pd.isna(r["usable_start"]) or pd.isna(r["usable_end"]):
            continue
        start = pd.Timestamp(r["usable_start"])
        end = pd.Timestamp(r["usable_end"])
        s_stint = parse_leading_date(r["stint_start"])
        if s_stint is not None and start < s_stint:
            raise ValueError(f"{r['ticker']}: usable_start {start.date()} before stint start {s_stint.date()}")
        if end < start:
            raise ValueError(f"{r['ticker']}: usable_end before usable_start")
        rows.append(
            dict(
                ticker=r["ticker"].strip(),
                window_start=start,
                window_end=end,
                verdict=r["verdict"],
                batch=r["batch"],
            )
        )
    return pd.DataFrame(rows)


def load_price_presence(prices_dir: Path, tickers, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """True where the ticker file has a non-null adj_close on that date (no forward fill)."""
    out = pd.DataFrame(False, index=dates, columns=pd.Index(list(tickers)))
    for t in out.columns:
        path = prices_dir / f"{t}.parquet"
        if not path.exists():
            continue
        s = pd.read_parquet(path, columns=["adj_close"])["adj_close"]
        s.index = pd.to_datetime(s.index)
        out[t] = s.notna().reindex(dates).fillna(False).astype(bool).to_numpy()
    return out


def build_corrected_mask(
    snaps: dict,
    dates: pd.DatetimeIndex,
    columns: pd.Index,
    windows: pd.DataFrame,
    last_member: dict | None = None,
) -> pd.DataFrame:
    """Snapshot mask, then last-member overrides, then Tier B windows (no price gate)."""
    last_member = LAST_MEMBER_OVERRIDES if last_member is None else last_member
    mask = build_mask(snaps, dates, columns)
    for ticker, (last, _reason) in last_member.items():
        if ticker in mask.columns:
            mask.loc[mask.index > pd.Timestamp(last), ticker] = False
    for ticker, grp in windows.groupby("ticker"):
        if ticker not in mask.columns:
            continue
        mask[ticker] = False
        for _, w in grp.iterrows():
            inside = (dates >= w["window_start"]) & (dates <= w["window_end"])
            mask.loc[inside, ticker] = True
    return mask


def override_table(
    snaps: dict,
    dates: pd.DatetimeIndex,
    columns: pd.Index,
    windows: pd.DataFrame,
    corrected: pd.DataFrame,
    last_member: dict | None = None,
) -> pd.DataFrame:
    """One row per overridden ticker: snapshot vs corrected first/last member date and the rule used."""
    last_member = LAST_MEMBER_OVERRIDES if last_member is None else last_member
    snap = build_mask(snaps, dates, columns)
    rows = []
    for ticker in sorted(set(windows["ticker"]) | set(last_member)):
        if ticker not in corrected.columns:
            continue
        if ticker in set(windows["ticker"]):
            rule = "tierB_window"
            if ticker in PRESS_LONGER_THAN_SNAPSHOT:
                rule = "tierB_window (press stint longer than snapshot)"
            if ticker in last_member:
                rule += " + snapshot last-member override"
            grp = windows[windows["ticker"] == ticker]
            win = "; ".join(f"{a.date()}..{b.date()}" for a, b in zip(grp.window_start, grp.window_end))
        else:
            rule = f"snapshot last member {last_member[ticker][0]}"
            win = ""
        s_on = snap[ticker][snap[ticker]].index
        c_on = corrected[ticker][corrected[ticker]].index
        rows.append(
            dict(
                ticker=ticker,
                rule=rule,
                windows=win,
                snapshot_first=str(s_on.min().date()) if len(s_on) else "",
                snapshot_last=str(s_on.max().date()) if len(s_on) else "",
                corrected_first=str(c_on.min().date()) if len(c_on) else "",
                corrected_last=str(c_on.max().date()) if len(c_on) else "",
                reason=last_member[ticker][1] if ticker in last_member else "",
            )
        )
    return pd.DataFrame(rows)


def coverage_report(snaps: dict, cached: set, start: str, end: str) -> pd.DataFrame:
    """Snapshot-only coverage (legacy): members per snapshot vs cached files."""
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


def corrected_coverage(ungated: pd.DataFrame, presence: pd.DataFrame) -> pd.DataFrame:
    """Per trading day: members (ungated mask count) and priced members (mask and price present)."""
    members = ungated.sum(axis=1)
    priced = (ungated & presence.reindex(columns=ungated.columns, fill_value=False)).sum(axis=1)
    return pd.DataFrame({"members": members, "priced": priced, "coverage": priced / members.where(members > 0)})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--components", required=True, type=Path)
    ap.add_argument("--prices-dir", default="data/raw", type=Path)
    ap.add_argument("--windows", type=Path, default=None, help="tierb_usable_windows.csv; enables corrected mask")
    ap.add_argument("--output", default="data/artifacts/sp500_pit_membership_mask.parquet", type=Path)
    ap.add_argument("--ungated-output", type=Path, default=None, help="corrected mask before price gate")
    ap.add_argument("--presence-output", type=Path, default=None, help="price presence frame")
    ap.add_argument("--overrides-out", type=Path, default=None, help="override table CSV")
    ap.add_argument("--start", default="2008-01-01")
    ap.add_argument("--end", default="2026-04-24")
    args = ap.parse_args()

    cached = {p.stem for p in args.prices_dir.glob("*.parquet")}
    snaps = load_snapshots(args.components)
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(pd.read_parquet(args.prices_dir / "SPY.parquet").index)))
    dates = dates[(dates >= pd.Timestamp(args.start)) & (dates <= pd.Timestamp(args.end))]
    columns = pd.Index(sorted(set().union(*snaps.values())))

    if args.windows is None:
        mask = build_mask(snaps, dates, columns)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        mask.to_parquet(args.output)
        print(f"snapshot mask {mask.shape} -> {args.output}")
    else:
        windows = load_tierb_windows(args.windows)
        columns = pd.Index(sorted(set(columns) | set(windows["ticker"])))
        ungated = build_corrected_mask(snaps, dates, columns, windows)
        presence = load_price_presence(args.prices_dir, columns, dates)
        mask = ungated & presence
        print(f"price gate removed {int(ungated.values.sum() - mask.values.sum())} True cells")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        mask.to_parquet(args.output)
        if args.ungated_output:
            ungated.to_parquet(args.ungated_output)
        if args.presence_output:
            presence.to_parquet(args.presence_output)
        if args.overrides_out:
            override_table(snaps, dates, columns, windows, ungated).to_csv(args.overrides_out, index=False)
        print(f"corrected mask {mask.shape} -> {args.output}")
        cov = corrected_coverage(ungated, presence)
        for year in (2008, 2012, 2016, 2020, 2024):
            sub = cov[cov.index.year == year]
            if not sub.empty:
                r = sub.iloc[-1]
                print(f"{year}: members {int(r.members)}, priced {int(r.priced)}, coverage {r.coverage:.0%}")
        print(f"mean corrected coverage {args.start}..{args.end}: {cov['coverage'].mean():.0%}")

    cov_legacy = coverage_report(snaps, cached, args.start, args.end)
    print("snapshot-only legacy coverage (file exists, ignores dates):")
    for year in (2008, 2012, 2016, 2020, 2024, 2026):
        sub = cov_legacy[cov_legacy["date"].dt.year == year]
        if not sub.empty:
            r = sub.iloc[-1]
            print(f"  {year}: members {r.members}, priced {r.priced}, coverage {r.coverage:.0%}")


if __name__ == "__main__":
    main()
