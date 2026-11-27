"""C1 regression: B.5 snapshots that hold SPY (the benchmark) must not break the equity-only mapping.

SPY is never bought in equity-only mode. Before the fix it entered the equity-sleeve scaling, and
finalize_equity_only raised an invariant AssertionError. The fix is in src/rl/exposure_mix.py
(apply_two_sleeve_mix excludes NON_TRADABLE_ASSETS). Snapshots without SPY are unchanged.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.rl.exposure_mix import (  # noqa: E402
    NON_TRADABLE_ASSETS,
    apply_exposure_mix,
    finalize_equity_only,
    project_two_sleeve,
)

TREND = ["TLT", "GLD", "UUP"]


def _snapshot(with_nontradable: bool) -> pd.Series:
    idx = ["AAA", "BBB", "CCC"]
    vals = [0.4, 0.3, 0.3]
    if with_nontradable:
        idx += ["SPY", "TLT", "GLD", "UUP"]
        vals += [0.05, 0.02, 0.01, 0.01]
    return pd.Series(vals, index=idx, dtype=float)


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
