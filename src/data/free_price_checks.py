"""Schema and validation checks for free-source price series (survivorship ingest).

Used by scripts/tier_free_price_candidates.py (tiering) and scripts/ingest_free_price_data.py
(writing). A series is only written when every check here passes and the identity evidence
file records a Tier B pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

REQUIRED_COLUMNS = ["open", "high", "low", "close", "volume", "adj_close"]
PRICE_COLUMNS = ["open", "high", "low", "close", "adj_close"]
START_TOLERANCE_DAYS = 30
MAX_GAP_TRADING_DAYS = 10
MAX_ZERO_VOLUME_FRAC = 0.05
JUMP_THRESHOLD = 0.40
SPLIT_TOLERANCE = 0.05
END_TOLERANCE_DAYS = 14


class SchemaError(ValueError):
    """Raised when a raw frame cannot be cast to the cache schema."""


def cast_cache_schema(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a frame in the data/raw cache schema.

    Accepts yfinance-style column names ("Adj Close", "Date" column) or cache names.
    Index: datetime64[ns] named 'date', normalized to midnight, sorted, unique.
    Columns: open, high, low, close, volume (int64), adj_close (float64).
    """
    df = raw.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    if "date" in df.columns:
        df = df.set_index("date")
    idx = pd.DatetimeIndex(pd.to_datetime(df.index))
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    df.index = idx.normalize().astype("datetime64[ns]")
    df.index.name = "date"
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"missing required columns: {missing}")
    out = df[REQUIRED_COLUMNS].astype("float64")
    out["volume"] = out["volume"].fillna(0).round().astype("int64")
    out = out[~out.index.duplicated(keep="last")].sort_index()
    if out.empty:
        raise SchemaError("empty frame after cast")
    return out


@dataclass
class CheckReport:
    values: dict = field(default_factory=dict)
    failures: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures


def splits_from_raw(raw: pd.DataFrame) -> pd.Series:
    """Split ratios from a raw yfinance frame ('Stock Splits' column), indexed by date."""
    date_col = raw.columns[0]
    col = next((c for c in raw.columns if str(c).lower().replace(" ", "_") == "stock_splits"), None)
    if col is None:
        return pd.Series(dtype=float)
    vals = pd.to_numeric(raw[col], errors="coerce").fillna(0.0)
    vals = vals[vals != 0]
    if vals.empty:
        return pd.Series(dtype=float)
    dates = pd.DatetimeIndex(pd.to_datetime(raw.loc[vals.index, date_col])).tz_localize(None).normalize()
    return pd.Series(vals.values, index=dates)


def _max_gap_trading_days(window_index: pd.DatetimeIndex, calendar: pd.DatetimeIndex) -> int:
    cal = calendar[(calendar >= window_index[0]) & (calendar <= window_index[-1])]
    pos = cal.get_indexer(window_index)
    pos = pos[pos >= 0]
    if len(pos) < 2:
        return 0
    return int((pd.Series(pos).diff().dropna() - 1).max())


def check_series(
    df: pd.DataFrame,
    window_start: pd.Timestamp,
    window_end: pd.Timestamp,
    calendar: pd.DatetimeIndex,
    splits: Optional[pd.Series] = None,
) -> CheckReport:
    """Run the Tier B series checks (a), (b), (c) on the member window.

    splits: optional Series indexed by date with split ratios (e.g. 2.0 for 2:1, 0.5 for 1:2).
    A large move is explained only if a split on that date (+-1 day) implies the same return.
    """
    rep = CheckReport()
    ws, we = pd.Timestamp(window_start), pd.Timestamp(window_end)
    win = df.loc[(df.index <= we)]
    win = win.loc[win.index >= ws]
    rep.values["series_first"] = str(df.index[0].date())
    rep.values["series_last"] = str(df.index[-1].date())
    rep.values["window_rows"] = int(len(win))
    if win.empty:
        rep.failures.append("no_rows_in_member_window")
        return rep

    start_ok = df.index[0] <= ws + pd.Timedelta(days=START_TOLERANCE_DAYS)
    rep.values["start_ok"] = bool(start_ok)
    if not start_ok:
        rep.failures.append(f"starts {(df.index[0] - ws).days}d after member_first")

    end_ok = df.index[-1] >= we - pd.Timedelta(days=END_TOLERANCE_DAYS)
    rep.values["end_ok"] = bool(end_ok)
    if not end_ok:
        rep.failures.append(f"series ends {df.index[-1].date()} before member_last {we.date()}")

    gap = _max_gap_trading_days(win.index, calendar)
    rep.values["max_gap_trading_days"] = gap
    if gap > MAX_GAP_TRADING_DAYS:
        rep.failures.append(f"gap of {gap} trading days inside window")

    nonpos = bool((win[PRICE_COLUMNS] <= 0).any().any())
    rep.values["nonpositive_price"] = nonpos
    if nonpos:
        rep.failures.append("non-positive price in window")

    zero_frac = float((win["volume"] == 0).mean())
    rep.values["zero_volume_frac"] = round(zero_frac, 4)
    if zero_frac > MAX_ZERO_VOLUME_FRAC:
        rep.failures.append(f"zero-volume fraction {zero_frac:.2%} > {MAX_ZERO_VOLUME_FRAC:.0%}")

    rets = win["close"].pct_change().dropna()
    big = rets[rets.abs() > JUMP_THRESHOLD]
    unexplained = []
    for dt, r in big.items():
        explained = False
        if splits is not None and len(splits):
            near = splits[(splits.index >= dt - pd.Timedelta(days=1)) & (splits.index <= dt + pd.Timedelta(days=1))]
            for ratio in near.values:
                if ratio > 0 and abs(r - (1.0 / ratio - 1.0)) <= SPLIT_TOLERANCE:
                    explained = True
        if not explained:
            unexplained.append(f"{dt.date()}:{r:+.2f}")
    rep.values["unexplained_jumps"] = unexplained
    if unexplained:
        rep.failures.append(f"unexplained |ret|>{JUMP_THRESHOLD:.0%}: {';'.join(unexplained[:5])}")
    return rep


REQUIRED_EVIDENCE_FLAGS = ["a_start_or_ipo", "b_continuity", "c_no_unexplained_jump", "d_identity", "e_scale_anchor"]


def evidence_failures(evidence: dict) -> list:
    """Return failures for an identity evidence record; empty list means Tier B evidence is complete."""
    out = []
    if evidence.get("tier") != "B":
        out.append(f"evidence tier is {evidence.get('tier')!r}, not 'B'")
    checks = evidence.get("checks", {})
    for flag in REQUIRED_EVIDENCE_FLAGS:
        if checks.get(flag) is not True:
            out.append(f"evidence check {flag} not passed")
    for key in ("cik", "vendor_name", "sec_name_matched", "sec_first_filing"):
        if not evidence.get(key):
            out.append(f"evidence missing {key}")
    return out
