"""A0 tests: action -> exposure map, corrected inverse, SPY-in-snapshot regression (C1 bug)."""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from a0_action_map import equity_floor, raw_for_equity  # noqa: E402
from src.rl.exposure_mix import (  # noqa: E402
    NON_TRADABLE_ASSETS,
    apply_exposure_mix,
    finalize_equity_only,
    project_two_sleeve,
)

TREND = ["TLT", "GLD", "UUP"]
CACHE = REPO_ROOT / "runs_a0" / "cache" / "a0_cache.pkl"


def _snapshot(with_nontradable: bool) -> pd.Series:
    idx = ["AAA", "BBB", "CCC"]
    vals = [0.4, 0.3, 0.3]
    if with_nontradable:
        idx += ["SPY", "TLT", "GLD", "UUP"]
        vals += [0.05, 0.02, 0.01, 0.01]
    return pd.Series(vals, index=idx, dtype=float)


def test_projection_invariants_on_grid():
    grid = np.linspace(-1, 1, 41)
    for a in grid:
        for b in grid:
            eq, ca = project_two_sleeve(float(a), float(b))
            assert 0.5 - 1e-12 <= eq <= 1.0 + 1e-12
            assert -1e-12 <= ca <= 0.5 + 1e-12
            assert abs(eq + ca - 1.0) < 1e-12


@pytest.mark.parametrize("raw,expected", [
    ((-1, -1), (1.0, 0.0)),
    ((-1, 1), (0.5, 0.5)),
    ((1, -1), (1.0, 0.0)),
    ((1, 1), (2 / 3, 1 / 3)),
])
def test_corner_cases(raw, expected):
    eq, ca = project_two_sleeve(*map(float, raw))
    assert eq == pytest.approx(expected[0], abs=1e-12)
    assert ca == pytest.approx(expected[1], abs=1e-12)


def test_floor_is_half_and_cash_cap_binds_there():
    assert equity_floor() == pytest.approx(0.5)
    eq, ca = project_two_sleeve(-1.0, 1.0)
    assert eq == pytest.approx(0.5) and ca == pytest.approx(0.5)


@pytest.mark.parametrize("target", [0.5, 0.55, 0.6, 0.612, 2 / 3, 0.75, 0.9, 1.0])
def test_corrected_inverse_realises_target(target):
    re_, rc = raw_for_equity(target)
    eq, _ = project_two_sleeve(re_, rc)
    assert eq == pytest.approx(target, abs=1e-9)


def test_inverse_rejects_unreachable_targets():
    with pytest.raises(ValueError):
        raw_for_equity(0.3)


def test_regression_c1_spy_in_snapshot_passes_with_fix():
    """C1 bug: SPY in a B.5 snapshot entered equity scaling and finalize_equity_only raised."""
    w, info = apply_exposure_mix(_snapshot(True), TREND, np.array([0.2, -0.3]))
    out = finalize_equity_only(w, info["equity_frac"])
    assert "SPY" not in out.index and "TLT" not in out.index
    assert float(out.abs().sum()) == pytest.approx(info["equity_frac"], abs=1e-6)


def test_regression_c1_spy_in_snapshot_would_have_raised_before_fix():
    """Reproduce the pre-fix scaling (SPY included in stock_slice) and show the invariant breaks."""
    snap = _snapshot(True)
    eq, _ca = project_two_sleeve(0.2, -0.3)
    stock = snap[[t for t in snap.index if t not in set(TREND)]]  # old: NON_TRADABLE not excluded
    res = pd.Series(0.0, index=snap.index)
    res[stock.index] = stock * (eq / float(stock.abs().sum()))
    with pytest.raises(AssertionError):
        finalize_equity_only(res, eq)
    assert set(NON_TRADABLE_ASSETS) == {"GLD", "SPY", "TLT", "UUP"}


@pytest.mark.parametrize("nontrade", [False, True])
def test_stock_sum_equals_equity_share(nontrade):
    for raw in ([-1, -1], [0.0, 0.0], [1.0, -1.0], [0.3, 0.9]):
        w, info = apply_exposure_mix(_snapshot(nontrade), TREND, np.array(raw, dtype=float))
        out = finalize_equity_only(w, info["equity_frac"])
        assert abs(float(out.abs().sum()) - info["equity_frac"]) < 1e-6


@pytest.mark.xfail(strict=True, reason="A0 defect D4: snapshot with no stock (only SPY/TLT/GLD/UUP) "
                                       "gives zero holdings while equity_frac > 0; finalize does not raise")
def test_zero_stock_snapshot_should_not_report_equity():
    snap = pd.Series([0.9, 0.1], index=["SPY", "TLT"], dtype=float)
    w, info = apply_exposure_mix(snap, TREND, np.array([0.0, 0.0]))
    out = finalize_equity_only(w, info["equity_frac"])
    assert float(out.abs().sum()) == pytest.approx(info["equity_frac"], abs=1e-6)


@pytest.mark.skipif(not CACHE.exists(), reason="runs_a0/cache not built (scripts/a0_build_cache.py)")
def test_real_snapshots_identity_on_control_dates():
    """Real B.5 snapshots (committed equity-only build): identity holds on every 8w control date.

    Note: the committed build has no SPY/TLT/GLD/UUP columns at all, so the C1 SPY case is not
    reached on real data; it is covered by the synthetic regression tests above.
    """
    with open(CACHE, "rb") as fh:
        c = pickle.load(fh)
    b5 = c["b5"]
    assert not (set(NON_TRADABLE_ASSETS) & set(b5.columns)), "unexpected non-tradable columns in B.5"
    for d in c["ctrl"][1:]:  # first control date 2008-01-07 is the first with a book
        snap = b5.loc[b5.index <= d].iloc[-1].fillna(0.0)
        for raw in ([0.5, -0.2], [-1.0, 1.0], [1.0, -1.0]):
            w, info = apply_exposure_mix(snap, TREND, np.array(raw))
            out = finalize_equity_only(w, info["equity_frac"])
            assert abs(float(out.abs().sum()) - info["equity_frac"]) < 1e-6


@pytest.mark.skipif(not CACHE.exists(), reason="runs_a0/cache not built")
@pytest.mark.xfail(strict=True, reason="A0 defect D4 on real data: 14d grid starts 2008-01-02, before the "
                                       "first B.5 snapshot (2008-01-07); holdings are zero while equity_frac>0")
def test_real_14d_first_decision_has_a_book():
    with open(CACHE, "rb") as fh:
        c = pickle.load(fh)
    b5 = c["b5"]
    d = pd.Timestamp("2008-01-02")
    snap = b5.loc[b5.index <= d]
    assert not snap.empty
    w, info = apply_exposure_mix(snap.iloc[-1].fillna(0.0), TREND, np.array([0.0, 0.0]))
    out = finalize_equity_only(w, info["equity_frac"])
    assert float(out.abs().sum()) == pytest.approx(info["equity_frac"], abs=1e-6)
