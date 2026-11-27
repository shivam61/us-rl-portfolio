"""M1 causality and M9 negative controls for the v4.1 feature library.

Fast: 3 forced crisis dates (2008-10-10, 2020-03-16, 2022-06-15) and 2 random dates.
Slow (@pytest.mark.slow): 100 random dates + the forced dates, three corruption modes each.
"""
import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import (FORCED_DATES, MIN_COMPARED, corrupt_after, load_history, probe_dates, rows_match,
                                 truncate)
from src.rl.features_risk_v4 import FEATURE_NAMES, _expz, build_panel


@pytest.fixture(scope="module")
def H():
    return load_history()


@pytest.fixture(scope="module")
def full(H):
    return build_panel(H)


def _forced(full):
    return [min(full.index, key=lambda t: abs((t - pd.Timestamp(f)).days)) for f in FORCED_DATES]


def _assert_equal_at(full, Hx, d):
    bad, n = rows_match(full.loc[d], build_panel(Hx).loc[d], FEATURE_NAMES)
    assert n >= MIN_COMPARED, f"only {n} non-NaN features compared at {d.date()}: vacuous"
    assert not bad, f"look-ahead at {d.date()}: {bad}"


def test_no_lookahead_truncation(H, full):
    """M1: every feature at 2008-10, 2020-03, 2022-06 and two random dates equals the value computed
    from history truncated at that date (non-vacuous: a floor of non-NaN comparisons is enforced)."""
    dates = _forced(full) + probe_dates(full.index, n_random=5)[:2]
    for d in dates:
        _assert_equal_at(full, truncate(H, d), d)


def test_future_corruption_invariance(H, full):
    """M1: replacing everything after d by NaN, or by bootstrap noise, leaves row d unchanged."""
    rng = np.random.default_rng(11)
    for d in _forced(full):
        _assert_equal_at(full, corrupt_after(H, d, "nan"), d)
        _assert_equal_at(full, corrupt_after(H, d, "noise", rng), d)


@pytest.mark.slow
def test_causality_full_sweep_100_dates(H, full):
    """M1 full sweep: 100 random dates + forced dates, truncation / NaN / noise corruption."""
    rng = np.random.default_rng(7)
    failures = {}
    for d in probe_dates(full.index, n_random=100):
        for mode, Hx in (("trunc", truncate(H, d)), ("nan", corrupt_after(H, d, "nan")),
                         ("noise", corrupt_after(H, d, "noise", rng))):
            bad, n = rows_match(full.loc[d], build_panel(Hx).loc[d], FEATURE_NAMES)
            assert n >= MIN_COMPARED, f"vacuous comparison at {d.date()} ({mode})"
            if bad:
                failures[(str(d.date()), mode)] = bad
    assert not failures, list(failures.items())[:5]


def test_leak_detector_catches_injected_leak(H):
    """M9: a column carrying next-day SPY return must be flagged by the truncation check, while the
    real features are not."""
    def with_leak(Hx):
        P = build_panel(Hx).copy()
        P["LEAK_next_ret"] = _expz(Hx["spy"].pct_change(fill_method=None).shift(-1).reindex(P.index), "raw")
        return P
    d = pd.Timestamp("2012-06-01")
    names = FEATURE_NAMES + ["LEAK_next_ret"]
    bad_trunc, _ = rows_match(with_leak(H).loc[d], with_leak(truncate(H, d)).loc[d], names)
    bad_nan, _ = rows_match(with_leak(H).loc[d], with_leak(corrupt_after(H, d, "nan")).loc[d], names)
    assert "LEAK_next_ret" in bad_trunc and "LEAK_next_ret" in bad_nan, "detector failed to flag the leak"
    assert not [b for b in bad_trunc if b != "LEAK_next_ret"], "real features flagged: check is too loose"


def test_retained_features_are_non_constant(full):
    """The v4.1 set has no dead columns: every retained feature is non-constant over the certified window."""
    for c in FEATURE_NAMES:
        s = full[c].dropna()
        assert len(s) > 0 and s.std() > 1e-9, f"{c} is constant or empty"
