"""Tests for the free-source price ingest (schema cast, overwrite refusal, failed-check refusal,
reused-ticker rejection, manifest content). Synthetic data only; no network."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.data.free_price_checks import SchemaError, cast_cache_schema, check_series  # noqa: E402

_spec = importlib.util.spec_from_file_location("ingest_free_price_data", REPO / "scripts" / "ingest_free_price_data.py")
ingest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ingest)

CALENDAR = pd.DatetimeIndex(pd.bdate_range("2005-01-03", "2012-12-31"))
GOOD_CHECKS = {k: True for k in
               ["a_start_or_ipo", "b_continuity", "c_no_unexplained_jump", "d_identity", "e_scale_anchor"]}


def _yf_frame(start: str, end: str = "2012-12-31", seed: int = 0) -> pd.DataFrame:
    dates = CALENDAR[(CALENDAR >= pd.Timestamp(start)) & (CALENDAR <= pd.Timestamp(end))]
    rng = np.random.default_rng(seed)
    close = 50 * np.exp(np.cumsum(rng.normal(0, 0.01, len(dates))))
    return pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d 04:00:00"),
        "Open": close * 0.99, "High": close * 1.01, "Low": close * 0.98, "Close": close,
        "Adj Close": close * 0.97, "Volume": rng.integers(1_000, 90_000, len(dates)).astype(float),
        "Dividends": 0.0, "Stock Splits": 0.0,
    })


def _evidence(tmp: Path, ticker: str, tier: str = "B", **overrides) -> Path:
    ev = {"ticker": ticker, "tier": tier, "cik": "0000001234", "vendor_name": "Example Corp",
          "sec_name_matched": "EXAMPLE CORP", "sec_first_filing": "1995-01-01", "checks": dict(GOOD_CHECKS)}
    ev.update(overrides)
    path = tmp / "evidence" / f"{ticker}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ev))
    return path


def _setup(tmp: Path, ticker: str, frame: pd.DataFrame, member_first="2006-01-01", member_last="2012-12-31",
           tier="B", evidence_overrides=None):
    raw_dir = tmp / "raw_yf"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{ticker}.csv"
    frame.to_csv(raw_path, index=False)
    ev = _evidence(tmp, ticker, tier=tier, **(evidence_overrides or {}))
    tiers = pd.DataFrame([{
        "ticker": ticker, "source_ticker": ticker, "tier": tier, "cik": "0000001234",
        "member_first": member_first, "member_last": member_last, "raw_path": str(raw_path),
        "evidence_ref": str(ev),
    }])
    verdicts = tmp / "tiers.csv"
    tiers.to_csv(verdicts, index=False)
    return verdicts, tiers.iloc[0]


def _args(verdicts, dest, **kw):
    base = dict(verdicts=verdicts, raw_src=None, dest=dest, tier="B", calendar=None,
                dry_run=False, skip_existing=False, tickers=None)
    base.update(kw)
    return argparse.Namespace(**base)


def test_schema_cast_produces_cache_schema():
    raw = _yf_frame("2006-01-03", "2006-03-31")
    out = cast_cache_schema(raw)
    assert isinstance(out.index, pd.DatetimeIndex)
    assert out.index.dtype == "datetime64[ns]"
    assert out.index.name == "date"
    assert out["volume"].dtype == "int64"
    assert list(out.columns) == ["open", "high", "low", "close", "volume", "adj_close"]
    assert out.index.is_monotonic_increasing and out.index.is_unique
    assert out.index[0] == pd.Timestamp("2006-01-03")  # 04:00 timestamps normalized to midnight


def test_schema_cast_sorts_dedupes_and_rejects_missing_columns():
    raw = _yf_frame("2006-01-03", "2006-02-28").iloc[::-1]
    dup = pd.concat([raw, raw.iloc[:1]])
    out = cast_cache_schema(dup)
    assert out.index.is_monotonic_increasing and out.index.is_unique
    with pytest.raises(SchemaError):
        cast_cache_schema(raw.drop(columns=["Volume"]))


def test_overwrite_refused_then_skipped_with_flag(tmp_path):
    verdicts, row = _setup(tmp_path, "XYZ", _yf_frame("2006-01-03"))
    dest = tmp_path / "dest"
    existing = dest / "raw" / "XYZ.parquet"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"do not touch")
    manifest = []
    status, msgs = ingest.process_row(row, _args(verdicts, dest), CALENDAR, dest, manifest)
    assert status == "FAILED" and "refusing to overwrite" in msgs[0]
    assert existing.read_bytes() == b"do not touch"
    status, _ = ingest.process_row(row, _args(verdicts, dest, skip_existing=True), CALENDAR, dest, manifest)
    assert status == "SKIPPED" and existing.read_bytes() == b"do not touch"


def test_failed_check_refuses_write_and_exits_nonzero(tmp_path, monkeypatch):
    frame = _yf_frame("2006-01-03")
    frame.loc[frame.index[500:530], "Close"] = 0.0  # non-positive closes inside the window
    verdicts, _ = _setup(tmp_path, "BAD", frame)
    dest = tmp_path / "dest"
    monkeypatch.setattr(sys, "argv", ["ingest", "--verdicts", str(verdicts), "--dest", str(dest), "--tier", "B",
                                      "--calendar", "unused"])
    monkeypatch.setattr(ingest.pd, "read_parquet", lambda p: pd.DataFrame(index=CALENDAR))
    assert ingest.main() == 1
    assert not (dest / "raw" / "BAD.parquet").exists()
    assert not (dest / ingest.MANIFEST_NAME).exists()


def test_missing_identity_evidence_refused(tmp_path):
    verdicts, row = _setup(tmp_path, "NOEV", _yf_frame("2006-01-03"), evidence_overrides={"checks": {"d_identity": False}})
    dest = tmp_path / "dest"
    status, msgs = ingest.process_row(row, _args(verdicts, dest), CALENDAR, dest, [])
    assert status == "FAILED"
    assert any("evidence check" in m for m in msgs)


def test_reused_ticker_series_starting_after_member_first_is_rejected(tmp_path):
    # Series only starts in 2010 while the name was a member from 2006: the ticker was reused.
    frame = _yf_frame("2010-03-01")
    verdicts, row = _setup(tmp_path, "REUSED", frame, member_first="2006-01-01")
    dest = tmp_path / "dest"
    manifest = []
    status, msgs = ingest.process_row(row, _args(verdicts, dest), CALENDAR, dest, manifest)
    assert status == "FAILED"
    assert any("after member_first" in m for m in msgs)
    assert manifest == [] and not (dest / "raw" / "REUSED.parquet").exists()


def test_series_check_flags_unexplained_jump_and_accepts_split_explained_one():
    frame = cast_cache_schema(_yf_frame("2006-01-03"))
    jump_at = frame.index[300]
    frame.loc[jump_at:, ["open", "high", "low", "close", "adj_close"]] *= 0.4  # -60% day, no split
    bad = check_series(frame, pd.Timestamp("2006-01-01"), pd.Timestamp("2012-12-31"), CALENDAR)
    assert any(f.startswith("unexplained") for f in bad.failures)
    splits = pd.Series([2.5], index=pd.DatetimeIndex([jump_at]))  # 2.5:1 split explains -60%
    good = check_series(frame, pd.Timestamp("2006-01-01"), pd.Timestamp("2012-12-31"), CALENDAR, splits=splits)
    assert not any(f.startswith("unexplained") for f in good.failures)


def test_gap_longer_than_ten_trading_days_fails():
    frame = cast_cache_schema(_yf_frame("2006-01-03"))
    keep = frame.index.difference(CALENDAR[(CALENDAR >= "2008-01-01") & (CALENDAR < "2008-03-01")])
    rep = check_series(frame.loc[keep], pd.Timestamp("2006-01-01"), pd.Timestamp("2012-12-31"), CALENDAR)
    assert any(f.startswith("gap of") for f in rep.failures)


def test_manifest_row_written_with_sha_and_ranges(tmp_path):
    verdicts, row = _setup(tmp_path, "GOOD", _yf_frame("2006-01-03"))
    dest = tmp_path / "dest"
    manifest = []
    status, _ = ingest.process_row(row, _args(verdicts, dest), CALENDAR, dest, manifest)
    assert status == "WRITTEN"
    ingest.write_manifest(dest, manifest)
    rows = json.loads((dest / ingest.MANIFEST_NAME).read_text())
    assert len(rows) == 1
    m = rows[0]
    target = dest / "raw" / "GOOD.parquet"
    assert m["ticker"] == "GOOD" and m["tier"] == "B" and m["source"] == "yfinance"
    assert m["sha256"] == hashlib.sha256(target.read_bytes()).hexdigest()
    stored = pd.read_parquet(target)
    assert m["rows"] == len(stored) and m["first"] == str(stored.index[0].date())
    assert m["last"] == str(stored.index[-1].date())
    assert m["cache_file"] == "raw/GOOD.parquet"
    assert "identity_evidence" in m["checks_passed"] and m["evidence_ref"].endswith("GOOD.json")
    assert stored.index.dtype == "datetime64[ns]" and stored["volume"].dtype == "int64"


def test_dry_run_writes_nothing(tmp_path):
    verdicts, row = _setup(tmp_path, "DRY", _yf_frame("2006-01-03"))
    dest = tmp_path / "dest"
    status, _ = ingest.process_row(row, _args(verdicts, dest, dry_run=True), CALENDAR, dest, [])
    assert status == "DRY_OK"
    assert not dest.exists()
