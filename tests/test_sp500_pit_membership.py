import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_sp500_pit_membership import build_mask, coverage_report  # noqa: E402


def _snaps():
    return {
        pd.Timestamp("2008-01-02"): {"AAA", "BBB"},
        pd.Timestamp("2008-06-01"): {"AAA", "CCC"},  # BBB removed, CCC added
    }


def test_mask_uses_latest_snapshot_on_or_before_date():
    dates = pd.DatetimeIndex(["2008-01-02", "2008-05-30", "2008-06-02"])
    mask = build_mask(_snaps(), dates, pd.Index(["AAA", "BBB", "CCC"]))
    assert mask.loc["2008-01-02", ["AAA", "BBB"]].all()
    assert not mask.loc["2008-01-02", "CCC"]
    assert mask.loc["2008-05-30", "BBB"] and not mask.loc["2008-05-30", "CCC"]
    assert not mask.loc["2008-06-02", "BBB"] and mask.loc["2008-06-02", "CCC"]


def test_mask_is_causal_no_future_snapshot_used_early():
    dates = pd.DatetimeIndex(["2007-12-31"])
    mask = build_mask(_snaps(), dates, pd.Index(["AAA", "BBB", "CCC"]))
    assert not mask.values.any()


def test_coverage_excludes_tagged_delisted_and_unpriced():
    snaps = {pd.Timestamp("2008-01-02"): {"AAA", "OLDX-200101", "NOPRICE"}}
    cov = coverage_report(snaps, cached={"AAA", "OLDX-200101"}, start="2008-01-01", end="2008-12-31")
    row = cov.iloc[0]
    assert row.members == 3
    assert row.priced == 1
