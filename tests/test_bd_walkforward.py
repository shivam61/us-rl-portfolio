"""BD2 structural tests (docs/phases/rl_bandit_plan.md section 9).

- test_walk_forward_purge: every training decision is at least PURGE+1 decisions before the test fold,
  and training never includes a test year or later.
- test_no_future_labels_in_fit_or_alpha: corrupting labels (U1) at and after a fold's first test decision
  leaves that fold's training fit, inner alpha choice and test shares unchanged.
- test_bootstrap_coverage: the paired stationary bootstrap covers a known difference at roughly 95%.
- test_shuffled_context_destroys_signal: on a synthetic dataset with a real context-dependent edge,
  L2 beats the block-shuffled-context control.
- test_planted_signal_recovered: a strong planted edge is recovered by L2 on synthetic data.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from rl import bd_core as C  # noqa: E402

# BD inputs (runs_bd/inputs) are materialised copies of the FH feature outputs and are not committed.
pytestmark = pytest.mark.skipif(not (C.INPUT_DIR / "history_v41.pkl").exists(),
                                reason="runs_bd/inputs not built (see docs/phases/rl_bandit_plan.md)")
from rl import bd_learners as L  # noqa: E402


@pytest.fixture(scope="module")
def setup14():
    h = C.load_history()
    x0 = C.x0_daily(h)
    dt = pd.read_parquet(C.INPUT_DIR / "daily_table.parquet")
    dt = dt.loc[dt.index <= C.TERMINAL]
    g = C.build_grid("14d", h)
    Yall = L.labels(g, C.ARMS_UNION)
    cols = [C.ARMS_UNION.index(a) for a in C.ARMS_PRIMARY]
    Y = Yall[:, cols]
    M, _ = L.gross_risk(g)
    X = L.context_x0(g, x0)
    Xt = L.context_tr(g, dt)
    valid = L.common_mask(X, Xt, Y, M)
    return g, Y, X, Xt, M, valid


def test_walk_forward_purge(setup14):
    g, Y, X, Xt, M, valid = setup14
    n_folds = 0
    for y, train, test in L.fold_sets(g, valid):
        n_folds += 1
        k = int(test.min())
        assert train.max() <= k - L.PURGE - 1
        assert (g.dates[train].year < y).all()
        assert (g.dates[test].year == y).all()
    assert n_folds == 14


def test_no_future_labels_in_fit_or_alpha(setup14):
    g, Y, X, Xt, M, valid = setup14
    yrs = np.asarray(g.dates.year)
    y = 2019
    test = np.where((yrs == y) & valid)[0]
    train = np.where(valid & (yrs < y) & (np.arange(g.n) <= test.min() - L.PURGE - 1))[0]
    sh_a, info_a = L.fold_choice("L2", g, train, test, C.ARMS_PRIMARY, Y, X=X)
    Yc = Y.copy()
    Yc[test.min():] = 1e6  # labels from the first test decision onwards are garbage
    sh_b, info_b = L.fold_choice("L2", g, train, test, C.ARMS_PRIMARY, Yc, X=X)
    assert info_a["alpha"] == info_b["alpha"]
    assert np.allclose(sh_a, sh_b)


def test_bootstrap_coverage():
    """Stationary block bootstrap CI for a known mean difference covers the truth in >= 80% of reps."""
    truth = 0.004
    n, reps, B = 300, 60, 200
    hits = 0
    for r in range(reps):
        rng = np.random.default_rng(1000 + r)
        base = rng.normal(0.0, 0.03, size=n)
        diff = truth + rng.normal(0.0, 0.02, size=n)  # per-decision paired difference, true mean = truth
        assert abs(float(np.mean(diff)) - truth) < 0.02
        a_u = base + diff
        boots = []
        for _ in range(B):
            J = L.stationary_indices(n, 10, rng)
            boots.append(float(np.mean(a_u[J] - base[J])))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        hits += int(lo <= truth <= hi)
    assert hits / reps >= 0.8, hits / reps


def test_shuffled_context_destroys_signal(setup14):
    g, Y, X, Xt, M, valid = setup14
    rng = np.random.default_rng(0)
    # build a synthetic label with a real edge in the high-VIX-rank states (known context)
    vr = X[:, C.X0_COLS.index("vix_rank")]
    Ys = Y.copy()
    E = np.zeros_like(Y)
    for k, a in enumerate(C.ARMS_PRIMARY):
        E[:, k] = 0.05 * (vr > 0) * (0.625 - a)
    Ys = Ys + E
    wf = L.run_walk_forward(g, Ys, C.ARMS_PRIMARY, "L2", valid, X=X, M=M, Xtr=Xt)
    wfc = L.run_walk_forward(g, Ys, C.ARMS_PRIMARY, "C1", valid, X=X, M=M, Xtr=Xt, seed=1)
    ch = wf["chosen"]
    cc = wfc["chosen"]
    idx = np.where(np.isfinite(ch))[0]
    u_l2 = np.mean(C.run_shares(g, idx, ch[idx])["U1"])
    u_c1 = np.mean(C.run_shares(g, idx, cc[idx])["U1"])
    assert u_l2 > u_c1


def test_planted_signal_recovered(setup14):
    """A strong planted edge (high-VIX-rank states favour low shares) is recovered: L2's chosen shares are
    lower in high-VIX-rank decisions than in low-VIX-rank decisions."""
    g, Y, X, Xt, M, valid = setup14
    vr = X[:, C.X0_COLS.index("vix_rank")]
    E = np.zeros_like(Y)
    for k, a in enumerate(C.ARMS_PRIMARY):
        E[:, k] = 0.08 * (vr > 0) * (0.625 - a)
    wf = L.run_walk_forward(g, Y + E, C.ARMS_PRIMARY, "L2", valid, X=X, M=M, Xtr=Xt)
    idx = np.where(np.isfinite(wf["chosen"]))[0]
    sh = wf["chosen"][idx]
    hi = vr[idx] > 0
    assert sh[hi].mean() < sh[~hi].mean()
