"""Write validated free-source price series into a cache folder (data/raw or data/raw_tierB).

Reads the tiers.csv written by scripts/tier_free_price_candidates.py. For each row of the
requested tier it:
  1. refuses to overwrite an existing <dest>/raw/<TICKER>.parquet (use --skip-existing to skip),
  2. checks the identity evidence file (Tier B needs every evidence check passed),
  3. casts the raw yfinance csv to the cache schema,
  4. re-runs the series checks (start, end, gaps, zero prices/volume, unexplained jumps)
     on the membership window,
  5. writes the parquet and appends a row to <dest>/_manifest.json.
Any failed check is reported and the process exits 1. Nothing is written for a failed name.

Tier B goes to data/raw_tierB (DataIngestion(cache_dir=data/raw_tierB) reads data/raw_tierB/raw).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.data.free_price_checks import (  # noqa: E402
    SchemaError,
    cast_cache_schema,
    check_series,
    evidence_failures,
    splits_from_raw,
)

MANIFEST_NAME = "_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(dest: Path) -> list:
    path = dest / MANIFEST_NAME
    return json.loads(path.read_text()) if path.exists() else []


def write_manifest(dest: Path, rows: list) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    tmp = dest / (MANIFEST_NAME + ".tmp")
    tmp.write_text(json.dumps(rows, indent=1))
    tmp.replace(dest / MANIFEST_NAME)


def process_row(row: pd.Series, args, calendar: pd.DatetimeIndex, dest: Path, manifest: list) -> tuple[str, list]:
    """Return (status, messages). status is WRITTEN, DRY_OK, SKIPPED or FAILED."""
    ticker, tier = row["ticker"], row["tier"]
    target = dest / "raw" / f"{ticker}.parquet"
    if target.exists():
        if args.skip_existing:
            return "SKIPPED", [f"{target} exists"]
        return "FAILED", [f"refusing to overwrite existing {target}"]
    if any(r.get("ticker") == ticker for r in manifest):
        return "FAILED", [f"{ticker} already listed in {dest / MANIFEST_NAME}"]

    failures: list[str] = []
    evidence_path = Path(str(row["evidence_ref"]))
    if not evidence_path.exists():
        failures.append(f"identity evidence file missing: {evidence_path}")
        evidence = {}
    else:
        evidence = json.loads(evidence_path.read_text())
        if tier == "B":
            failures += evidence_failures(evidence)

    raw_path = Path(args.raw_src) / Path(str(row["raw_path"])).name if args.raw_src else Path(str(row["raw_path"]))
    if not raw_path.exists():
        return "FAILED", failures + [f"raw file missing: {raw_path}"]
    raw = pd.read_csv(raw_path, parse_dates=[0])
    try:
        series = cast_cache_schema(raw)
    except SchemaError as exc:
        return "FAILED", failures + [f"schema: {exc}"]

    mf, ml = pd.Timestamp(row["member_first"]), pd.Timestamp(row["member_last"])
    rep = check_series(series, mf, ml, calendar, splits=splits_from_raw(raw))
    failures += rep.failures
    if failures:
        return "FAILED", failures

    if args.dry_run:
        return "DRY_OK", [f"{ticker}: {len(series)} rows {series.index[0].date()}..{series.index[-1].date()}"]

    dest.joinpath("raw").mkdir(parents=True, exist_ok=True)
    series.to_parquet(target)
    manifest.append({
        "ticker": ticker,
        "tier": tier,
        "source": "yfinance",
        "source_ticker": str(row.get("source_ticker")),
        "pull_date": datetime.fromtimestamp(raw_path.stat().st_mtime, tz=timezone.utc).date().isoformat(),
        "sha256": _sha256(target),
        "first": str(series.index[0].date()),
        "last": str(series.index[-1].date()),
        "rows": int(len(series)),
        "checks_passed": ["schema", "start", "end", "gaps", "nonpositive", "zero_volume", "jumps", "identity_evidence"],
        "evidence_ref": str(evidence_path),
        "cik": evidence.get("cik"),
        "cache_file": str(target.relative_to(dest)),
        "written_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    return "WRITTEN", [f"{ticker}: {len(series)} rows"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verdicts", required=True, type=Path, help="tiers.csv from tier_free_price_candidates.py")
    ap.add_argument("--raw-src", type=Path, default=None,
                    help="directory holding the yfinance raw csvs (default: raw_path column of --verdicts)")
    ap.add_argument("--dest", required=True, type=Path, help="cache folder, e.g. data/raw or data/raw_tierB")
    ap.add_argument("--tier", required=True, choices=["A", "B"])
    ap.add_argument("--calendar", type=Path, default=REPO / "data" / "raw" / "AAPL.parquet")
    ap.add_argument("--dry-run", action="store_true", help="run every check, write nothing")
    ap.add_argument("--skip-existing", action="store_true", help="skip tickers whose parquet already exists")
    ap.add_argument("--tickers", nargs="*", default=None, help="restrict to these tickers")
    args = ap.parse_args()
    if args.dest.name == "raw":
        ap.error("--dest is the cache root (the folder holding raw/); use --dest data for Tier A "
                 "and --dest data/raw_tierB for Tier B")

    tiers = pd.read_csv(args.verdicts)
    tiers = tiers[tiers["tier"] == args.tier]
    if args.tickers:
        tiers = tiers[tiers["ticker"].isin(args.tickers)]
    calendar = pd.DatetimeIndex(pd.read_parquet(args.calendar).index).sort_values()
    manifest = load_manifest(args.dest)

    counts: dict[str, int] = {}
    failed = []
    for _, row in tiers.iterrows():
        status, msgs = process_row(row, args, calendar, args.dest, manifest)
        counts[status] = counts.get(status, 0) + 1
        for m in msgs:
            print(f"[{status}] {m}")
        if status == "FAILED":
            failed.append(row["ticker"])
        if status == "WRITTEN":
            write_manifest(args.dest, manifest)
    print(f"tier {args.tier}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
