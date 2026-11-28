"""Tests for the corrected point-in-time S&P 500 membership mask (scripts/build_sp500_pit_membership.py).

Synthetic tests run without any data. The last test checks the real mask artifact when it exists.
"""
import importlib.util
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
_spec = importlib.util.spec_from_file_location("build_sp500_pit_membership", REPO / "scripts" / "build_sp500_pit_membership.py")
pit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pit)

WINDOWS_HEADER = "ticker,cik,entity_name_in_window,stint_start,stint_end,usable_start,usable_end,verdict,batch"
WINDOWS_ROWS = [
    "JEF,96223,Jefferies,2018-05-23,2019-09-26 (removal eff.),2018-05-23,2019-09-25,CONFIRMED-WITH-LIMITS,3",
    "CZR,1590895,Caesars,2021-03-22,2025-09-19,2021-03-22,2025-09-19,CONFIRMED-WITH-LIMITS,4",
    "PENN,921738,Penn,2021-03-22 (S&P release),2022-06-28 (last IN snapshot; removal eff 2022-09-19),2021-03-22,2022-09-16,CONFIRMED-WITH-LIMITS,2",
    "ILMN,1110803,Illumina,2015-11-19,2024-06-21,2015-11-19,2024-06-21,CONFIRMED-WITH-LIMITS,4",
    "ILMN,1110803,Illumina,2026-09-21,ongoing (series end 2026-11-27),2026-09-21,2026-11-27,CONFIRMED-WITH-LIMITS,4",
    "FMC,37785,FMC,2009-08-19,2025-03-21,2009-08-19,2025-03-21,CONFIRMED-WITH-LIMITS,4",
    "FMC,37785,FMC,1996-01-02,2002-01-01 (outside batch window),,,NOT IN BATCH WINDOW,4",
]


def write_windows(tmp_path: Path) -> Path:
    path = tmp_path / "windows.csv"
    path.write_text("\n".join([WINDOWS_HEADER] + WINDOWS_ROWS) + "\n")
    return path


@pytest.fixture
def synthetic(tmp_path):
    """Dates 2008..2026 (weekdays), every synthetic name a member in every snapshot, prices present."""
    dates = pd.bdate_range("2008-01-01", "2026-04-24")
    names = ["JEF", "CZR", "PENN", "ILMN", "FMC", "AAPL"]
    snaps = {pd.Timestamp("2008-01-01"): set(names)}
    windows = pit.load_tierb_windows(write_windows(tmp_path))
    columns = pd.Index(sorted(set(names) | set(windows["ticker"])))
    mask = pit.build_corrected_mask(snaps, dates, columns, windows)
    presence = pd.DataFrame(True, index=dates, columns=columns)
    return dict(dates=dates, windows=windows, mask=mask, presence=presence, columns=columns, snaps=snaps)


def test_tierb_false_outside_window_true_inside(synthetic):
    mask, windows = synthetic["mask"], synthetic["windows"]
    for ticker, grp in windows.groupby("ticker"):
        allowed = pd.Series(False, index=mask.index)
        for _, w in grp.iterrows():
            inside = (mask.index >= w["window_start"]) & (mask.index <= w["window_end"])
            allowed |= inside
            assert mask.loc[inside, ticker].all(), f"{ticker} should be True inside {w['window_start'].date()}..{w['window_end'].date()}"
        assert not (mask[ticker] & ~allowed).any(), f"{ticker} True outside its usable window(s)"


def test_jef_false_before_2018_05_23_and_true_inside(synthetic):
    jef = synthetic["mask"]["JEF"]
    assert not jef.loc[:"2018-05-22"].any()
    assert jef.loc["2018-05-23"]
    assert jef.loc["2019-09-25"]
    assert not jef.loc["2019-09-26":].any()


def test_czr_false_before_2020_07_20(synthetic):
    czr = synthetic["mask"]["CZR"]
    assert not czr.loc[:"2020-07-19"].any()
    assert not czr.loc["2020-07-20":"2021-03-21"].any()
    assert czr.loc["2021-03-22"]


def test_multi_stint_ticker_uses_each_window(synthetic):
    ilmn = synthetic["mask"]["ILMN"]
    assert ilmn.loc["2015-11-19"] and ilmn.loc["2024-06-21"]
    assert not ilmn.loc["2024-06-24":"2026-04-24"].any()


def test_penn_uses_press_corrected_usable_end_not_stale_stint_end(synthetic):
    penn = synthetic["mask"]["PENN"]
    assert penn.loc["2022-09-16"], "usable_end is the corrected date; stint text 2022-06-28 is stale"
    assert not penn.loc["2022-09-19":].any()


def test_fmc_snapshot_last_member_override(tmp_path):
    dates = pd.bdate_range("2008-01-01", "2026-04-24")
    snaps = {pd.Timestamp("2008-01-01"): {"FMC", "AAPL"}, pd.Timestamp("2025-03-24"): {"AAPL"}}
    columns = pd.Index(["AAPL", "FMC"])
    # No Tier B windows here: this isolates the snapshot override.
    empty = pd.DataFrame(columns=["ticker", "window_start", "window_end"])
    mask = pit.build_corrected_mask(snaps, dates, columns, empty)
    assert mask.loc["2025-03-21", "FMC"]
    assert not mask.loc["2025-03-24":, "FMC"].any()


def test_mask_false_when_no_price_on_date(synthetic):
    dates, columns = synthetic["dates"], synthetic["columns"]
    presence = synthetic["presence"].copy()
    presence.loc["2010-01-01":"2010-12-31", "JEF"] = False
    gated = synthetic["mask"] & presence
    assert not gated.loc["2010-01-01":"2010-12-31", "JEF"].any()
    assert gated.loc["2009-06-01", "JEF"] == synthetic["mask"].loc["2009-06-01", "JEF"]
    assert not (gated & ~presence).values.any()


def test_load_tierb_windows_drops_rows_without_usable_dates(tmp_path):
    windows = pit.load_tierb_windows(write_windows(tmp_path))
    assert "FMC" in set(windows["ticker"])
    assert len(windows[windows["ticker"] == "FMC"]) == 1  # the out-of-batch row has no usable dates
    assert len(windows[windows["ticker"] == "ILMN"]) == 2


REAL_MASK = REPO / "runs_final" / "pit_mask_corrected.parquet"
REAL_PRESENCE = REPO / "runs_final" / "pit_price_presence.parquet"
REAL_WINDOWS = Path(os.environ.get("TIERB_WINDOWS_CSV", "/Users/shivamgupta/github/us-rl-portfolio/artifacts/reports/tierb_usable_windows.csv"))


@pytest.mark.skipif(not (REAL_MASK.exists() and REAL_PRESENCE.exists() and REAL_WINDOWS.exists()), reason="real mask artifacts not built")
def test_real_mask_respects_windows_and_price_presence():
    mask = pd.read_parquet(REAL_MASK)
    presence = pd.read_parquet(REAL_PRESENCE).reindex(index=mask.index, columns=mask.columns, fill_value=False)
    windows = pit.load_tierb_windows(REAL_WINDOWS)
    assert not (mask & ~presence).values.any(), "mask True on a date with no price"
    for t, grp in windows.groupby("ticker"):
        col = mask[t]
        allowed = pd.Series(False, index=mask.index)
        for _, w in grp.iterrows():
            allowed |= (mask.index >= w["window_start"]) & (mask.index <= w["window_end"])
        assert not (col & ~allowed).any(), f"{t} True outside its usable window"
    assert mask.loc["2019-01-02", "JEF"]
    assert not mask.loc[:"2018-05-22", "JEF"].any()
    assert not mask.loc[:"2020-07-19", "CZR"].any()
