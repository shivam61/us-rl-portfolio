"""Re-evaluate free-source price candidates and assign Tier A / Tier B / REJECT.

Inputs (all read-only):
  --verdicts   verify2 verdicts.csv (VERIFIED -> Tier A; PARTIAL -> re-tiered here)
  --membership artifacts/reports/members_missing_price_data_2006plus.csv (member_first/last)
  --yf-dir     verify2 raw/yf/<SOURCE_TICKER>.csv (yfinance, auto_adjust=False)
  --sec-dir    verify2 raw/sec/<CIK10>.json (SEC submissions)
  --calendar   a cache parquet whose index is the trading calendar (default data/raw/AAPL.parquet)

Network (cached under --out-dir, so reruns are offline):
  vendor name via yfinance Ticker.info; SEC companyfacts dei facts (EntityPublicFloat,
  EntityCommonStockSharesOutstanding), reduced to a small json per CIK.

Outputs under --out-dir:
  tiers.csv                 one row per candidate: ticker, tier, failures, check flags, refs
  evidence/<TICKER>.json    per-name evidence record consumed by scripts/ingest_free_price_data.py

Tier B needs ALL of: (a) start or IPO/spin inside window, (b) continuity, (c) no unexplained
>40% move, (d) SEC identity (CIK alive at member start, no predecessor series, vendor name
matches a SEC name valid in the member window, CIK alive at member end), (e) price-scale
anchor from SEC dei facts. Anything else is REJECT with reasons.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from src.data.free_price_checks import (  # noqa: E402
    cast_cache_schema,
    check_series,
    evidence_failures,
    splits_from_raw,
)

SEC_UA = "us-rl-portfolio-research ingest-tiering (research@example.com)"
# float / total shares understates price by the affiliate share; 0.5 allows up to 50% affiliates.
# Tighter than 0.25-4.0: a wider band let a spin-restated series (ITT, ratio 0.34) through.
ANCHOR_BAND = (0.5, 2.0)
IPO_LOOKBACK_DAYS = 365
IPO_LOOKAHEAD_DAYS = 120
EDGAR_PHASE_IN_END = pd.Timestamp("1997-12-31")
NAME_STOPWORDS = {"inc", "corp", "corporation", "co", "company", "ltd", "plc", "group", "holdings",
                  "holding", "the", "incorporated", "cl", "class", "llc", "lp", "trust", "de", "new"}


def _ts(value) -> pd.Timestamp | None:
    if value in (None, "", "nan") or pd.isna(value):
        return None
    return pd.Timestamp(str(value)[:10])


def _sig_tokens(name: str) -> list[str]:
    toks = re.findall(r"[a-z0-9]+", str(name).lower().replace("&", " and "))
    return [t for t in toks if t not in NAME_STOPWORDS]


def names_match(a: str, b: str) -> bool:
    ta, tb = _sig_tokens(a), _sig_tokens(b)
    if not ta or not tb:
        return False
    if ta[0] == tb[0] and (set(ta) & set(tb)):
        return True
    na, nb = " ".join(ta), " ".join(tb)
    return difflib.SequenceMatcher(None, na, nb).ratio() >= 0.85


def fetch_vendor_name(source_ticker: str, cache_dir: Path) -> str | None:
    path = cache_dir / "vendor" / f"{source_ticker.replace('/', '_')}.json"
    if not path.exists():
        import yfinance as yf

        info = {}
        for attempt in range(3):
            try:
                info = yf.Ticker(source_ticker).info or {}
                break
            except Exception:  # network / throttling
                time.sleep(1.0 + attempt)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"longName": info.get("longName"), "shortName": info.get("shortName")}))
        time.sleep(0.3)
    rec = json.loads(path.read_text())
    return rec.get("longName") or rec.get("shortName")


def load_companyfacts_dei(cik10: str, cache_dir: Path) -> dict:
    path = cache_dir / "cf_dei" / f"{cik10}.json"
    if not path.exists():
        req = urllib.request.Request(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json", headers={"User-Agent": SEC_UA}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            facts = json.loads(resp.read()).get("facts", {}).get("dei", {})
        keep = {}
        for key, unit in (("EntityPublicFloat", "USD"), ("EntityCommonStockSharesOutstanding", "shares")):
            vals = facts.get(key, {}).get("units", {}).get(unit, [])
            keep[key] = [{"end": v["end"], "val": v["val"]} for v in vals if "end" in v and "val" in v]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(keep))
        time.sleep(0.2)
    return json.loads(path.read_text())


def scale_anchor(series: pd.DataFrame, member_first: pd.Timestamp, member_last: pd.Timestamp, dei: dict) -> dict:
    """Price-scale anchor: SEC public float / shares outstanding implies a price near a float date.

    The float fact is the value of non-affiliate shares at the last business day of Q2, so
    float / total shares is a rough price level (affiliates push it below the true price). The
    fact must fall inside the membership window (XBRL facts start about 2009, so 2006-2008-only
    members have no anchor). The check compares the median close within +-45 days of the fact
    with the implied price and requires a ratio inside ANCHOR_BAND.
    """
    out = {"anchor": "sec_dei_public_float_over_shares", "passed": False, "band": list(ANCHOR_BAND)}
    floats = dei.get("EntityPublicFloat", [])
    shares = dei.get("EntityCommonStockSharesOutstanding", [])
    if not floats or not shares:
        out["reason"] = "no PublicFloat or shares facts in SEC dei"
        return out
    mid = member_first + (member_last - member_first) / 2
    inside = [v for v in floats if member_first <= pd.Timestamp(v["end"]) <= member_last and v["val"] > 0]
    if not inside:
        out["reason"] = "no PublicFloat fact dated inside membership window"
        return out
    fl = min(inside, key=lambda v: abs((pd.Timestamp(v["end"]) - mid).days))
    fl_end = pd.Timestamp(fl["end"])
    sh_ok = [v for v in shares if abs((pd.Timestamp(v["end"]) - fl_end).days) <= 365 and v["val"] > 0]
    if not sh_ok:
        out["reason"] = "no share count within 365d of float fact"
        return out
    sh = min(sh_ok, key=lambda v: abs((pd.Timestamp(v["end"]) - fl_end).days))
    implied = fl["val"] / sh["val"]
    near = series.loc[(series.index >= fl_end - pd.Timedelta(days=45)) & (series.index <= fl_end + pd.Timedelta(days=45))]
    if near.empty:
        out["reason"] = "no series rows within 45d of float fact"
        return out
    med = float(near["close"].median())
    ratio = med / implied
    out.update(
        float_date=str(fl_end.date()), float_usd=fl["val"], shares=sh["val"], shares_date=sh["end"],
        implied_price=round(implied, 4), median_close_near_fact=round(med, 4), ratio=round(ratio, 4),
        passed=bool(ANCHOR_BAND[0] <= ratio <= ANCHOR_BAND[1]),
    )
    return out


def sec_identity(sec: dict, member_first, member_last, series_first) -> dict:
    filing_dates = [_ts(d) for d in sec.get("filings", {}).get("recent", {}).get("filingDate", [])]
    filing_dates += [_ts(f.get("filingFrom")) for f in sec.get("filings", {}).get("files", [])]
    filing_dates = [d for d in filing_dates if d is not None]
    first_filing = min(filing_dates) if filing_dates else None
    last_filing = max(_ts(d) for d in sec.get("filings", {}).get("recent", {}).get("filingDate", [])) \
        if sec.get("filings", {}).get("recent", {}).get("filingDate") else None
    former = sec.get("formerNames", []) or []
    valid = []
    for fn in former:
        f, t = _ts(fn.get("from")), _ts(fn.get("to"))
        if f is None or t is None:
            continue
        if f <= member_last and t >= member_first:
            valid.append(fn["name"])
    tos = [_ts(fn.get("to")) for fn in former if _ts(fn.get("to")) is not None]
    current_from = max(tos) if tos else None
    if current_from is None or current_from <= member_last:
        valid.append(sec.get("name"))
    return {
        "cik": sec.get("cik"),
        "sec_name": sec.get("name"),
        "sec_former_names": former,
        "sec_names_valid_in_window": valid,
        "sec_first_filing": str(first_filing.date()) if first_filing is not None else None,
        "sec_last_filing": str(last_filing.date()) if last_filing is not None else None,
        "d1_cik_alive_at_member_start": bool(first_filing is not None and first_filing <= member_first + pd.Timedelta(days=30)),
        # EDGAR phase-in (about 1993-1996) makes earliest-filing dates before 1998 uninformative.
        "d3_no_predecessor_series": bool(first_filing is None or first_filing <= EDGAR_PHASE_IN_END
                                         or series_first >= first_filing - pd.Timedelta(days=IPO_LOOKBACK_DAYS)),
        "d4_cik_alive_at_member_end": bool(last_filing is not None and last_filing >= member_last - pd.Timedelta(days=IPO_LOOKBACK_DAYS)),
    }


def evaluate(row: pd.Series, args, calendar: pd.DatetimeIndex, cache: Path) -> dict:
    ticker, src = row["ticker"], row["source_ticker"]
    mf, ml = _ts(row["member_first"]), _ts(row["member_last"])
    raw_path = Path(args.yf_dir) / f"{src.replace('.', '-')}.csv"
    rec = {"ticker": ticker, "source_ticker": src, "cik": None, "member_first": str(mf.date()),
           "member_last": str(ml.date()), "raw_path": str(raw_path), "checks": {}, "failures": []}
    if not raw_path.exists():
        rec["failures"].append("no yfinance raw file")
        return rec
    raw = pd.read_csv(raw_path, parse_dates=[0])
    series = cast_cache_schema(raw.rename(columns={raw.columns[0]: "date"}).set_index("date"))
    splits = splits_from_raw(raw)
    rep = check_series(series, mf, ml, calendar, splits=splits)
    rec["series_first"], rec["series_last"] = rep.values.get("series_first"), rep.values.get("series_last")
    rec["series_checks"] = rep.values
    series_first = series.index[0]
    ipo_inside = bool(mf <= series_first <= ml)
    rec["checks"]["a_start_or_ipo"] = bool(rep.values.get("start_ok"))
    rec["checks"]["b_continuity"] = not any(
        f.startswith(("gap", "non-positive", "zero-volume", "no_rows")) for f in rep.failures)
    rec["checks"]["c_no_unexplained_jump"] = not any(f.startswith("unexplained") for f in rep.failures)
    rec["failures"] += rep.failures

    cik_raw = row.get("cik")
    if pd.isna(cik_raw):
        rec["failures"].append("no CIK in verify2 verdicts")
        return rec
    cik10 = f"{int(cik_raw):010d}"
    rec["cik"] = cik10
    sec = json.loads((Path(args.sec_dir) / f"{cik10}.json").read_text())
    ident = sec_identity(sec, mf, ml, series_first)
    rec.update(ident)
    vendor = fetch_vendor_name(src, cache)
    rec["vendor_name"] = vendor
    matched = next((n for n in ident["sec_names_valid_in_window"] if vendor and names_match(vendor, n)), None)
    rec["sec_name_matched"] = matched
    if not ident["sec_first_filing"]:
        rec["failures"].append("no SEC filing dates")
    if not ident["d1_cik_alive_at_member_start"]:
        rec["failures"].append(f"CIK first filing {ident['sec_first_filing']} after member_first (ticker reuse)")
    if not ident["d3_no_predecessor_series"]:
        rec["failures"].append("series predates CIK first filing by >1y (predecessor history)")
    if not ident["d4_cik_alive_at_member_end"]:
        rec["failures"].append("CIK stopped filing before member window ended")
    if matched is None:
        rec["failures"].append(f"vendor name {vendor!r} matches no SEC name valid in member window")
    rec["checks"]["d_identity"] = bool(
        ident["d1_cik_alive_at_member_start"] and ident["d3_no_predecessor_series"]
        and ident["d4_cik_alive_at_member_end"] and matched is not None)

    if ident["sec_first_filing"]:
        ipo_ok = ipo_inside and (pd.Timestamp(ident["sec_first_filing"]) >= series_first - pd.Timedelta(days=IPO_LOOKBACK_DAYS)) \
            and (pd.Timestamp(ident["sec_first_filing"]) <= series_first + pd.Timedelta(days=IPO_LOOKAHEAD_DAYS))
        rec["ipo_or_spin_inside_window"] = bool(ipo_ok)
        if ipo_ok and not rec["checks"]["a_start_or_ipo"]:
            rec["checks"]["a_start_or_ipo"] = True
            rec["failures"] = [f for f in rec["failures"] if not f.startswith("starts ")]
    dei = load_companyfacts_dei(cik10, cache / "cf")
    anchor = scale_anchor(series, mf, ml, dei)
    rec["anchor"] = anchor
    rec["checks"]["e_scale_anchor"] = bool(anchor.get("passed"))
    if not anchor.get("passed"):
        rec["failures"].append("scale anchor: " + str(anchor.get("reason") or f"ratio {anchor.get('ratio')} outside band"))
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verdicts", required=True, type=Path)
    ap.add_argument("--membership", required=True, type=Path)
    ap.add_argument("--yf-dir", required=True, type=Path)
    ap.add_argument("--sec-dir", required=True, type=Path)
    ap.add_argument("--calendar", type=Path, default=REPO / "data" / "raw" / "AAPL.parquet")
    ap.add_argument("--out-dir", type=Path, default=REPO / "runs_ingest")
    ap.add_argument("--limit", type=int, default=None, help="evaluate only the first N PARTIAL rows (debug)")
    args = ap.parse_args()

    out = args.out_dir
    (out / "evidence").mkdir(parents=True, exist_ok=True)
    cache = out / "net_cache"
    cache.mkdir(parents=True, exist_ok=True)
    calendar = pd.DatetimeIndex(pd.read_parquet(args.calendar).index).sort_values()
    verdicts = pd.read_csv(args.verdicts)
    members = pd.read_csv(args.membership).set_index("ticker")
    rows = []

    for _, v in verdicts[verdicts.verdict == "VERIFIED"].iterrows():
        rec = {"ticker": v.ticker, "source_ticker": v.source_ticker, "tier": "A", "cik": v.cik,
               "member_first": v.member_first, "member_last": v.member_last,
               "raw_path": str(args.yf_dir / f"{v.source_ticker.replace('.', '-')}.csv"),
               "failures": [], "checks": {"note": "verify2 VERIFIED; cache file already in data/raw"}}
        rec["evidence_ref"] = str(out / "evidence" / f"{v.ticker}.json")
        (out / "evidence" / f"{v.ticker}.json").write_text(json.dumps(
            {"ticker": v.ticker, "tier": "A", "source": "verify2 VERIFIED (runs_verify2/verdicts.csv)"}, indent=1))
        rows.append(rec)

    partial = verdicts[verdicts.verdict == "PARTIAL"]
    if args.limit:
        partial = partial.head(args.limit)
    for _, v in partial.iterrows():
        row = v.copy()
        row["member_first"] = members.loc[v.ticker, "member_first"]
        row["member_last"] = members.loc[v.ticker, "member_last"]
        rec = evaluate(row, args, calendar, cache)
        ok = not rec["failures"] and all(rec["checks"].get(k) for k in
                                          ["a_start_or_ipo", "b_continuity", "c_no_unexplained_jump",
                                           "d_identity", "e_scale_anchor"])
        rec["tier"] = "B" if ok else "REJECT"
        rec["evidence_ref"] = str(out / "evidence" / f"{v.ticker}.json")
        ev = {k: rec.get(k) for k in rec if k not in ("series_checks",)}
        ev["checks"] = {k: bool(x) for k, x in rec["checks"].items()}
        ev["evidence_failures"] = evidence_failures(ev) if rec["tier"] == "B" else []
        (out / "evidence" / f"{v.ticker}.json").write_text(json.dumps(ev, indent=1, default=str))
        rows.append(rec)

    flat = []
    for r in rows:
        flat.append({
            "ticker": r["ticker"], "source_ticker": r["source_ticker"], "tier": r["tier"], "cik": r.get("cik"),
            "member_first": r["member_first"], "member_last": r["member_last"],
            "series_first": r.get("series_first"), "series_last": r.get("series_last"),
            "raw_path": r["raw_path"], "evidence_ref": r["evidence_ref"],
            "vendor_name": r.get("vendor_name"), "sec_name_matched": r.get("sec_name_matched"),
            "checks": json.dumps(r["checks"], sort_keys=True), "failures": "; ".join(r["failures"]),
        })
    df = pd.DataFrame(flat)
    df.to_csv(out / "tiers.csv", index=False)
    print(df.tier.value_counts().to_string())


if __name__ == "__main__":
    main()
