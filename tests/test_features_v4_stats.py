"""M8/M9 statistical controls: block permutation, embargo, noise-null calibration, screen configuration and
reachability of the BH threshold (FH task 11 and 12)."""
import json
import os

import numpy as np
import pandas as pd
import pytest
from scipy.stats import kstest

from features_v4_helpers import GRID14_PATH, ROOT, bh_q, loro_pred, require
from src.rl import features_v4_screen as S

SCREEN_DIR = os.path.join(ROOT, "runs_fh", "screen_v4_1")


@pytest.fixture(scope="module")
def y_t1():
    G = pd.read_parquet(require(GRID14_PATH))
    y = -G["T1_mdd"].dropna().to_numpy(float)
    return y


def test_block_permuted_feature_has_no_ic(y_t1):
    """M9: a feature identical to the target has IC 1; after a block permutation of its time order its IC with
    the target is ~0, and the block-permutation test rejects the unpermuted version and not the permuted one."""
    rng = np.random.default_rng(0)
    x = y_t1.copy()
    _ic, p_true = S.p_block(x, y_t1, B=2000, rng=np.random.default_rng(1))
    assert p_true < 0.001
    perm = S.block_perm_indices(len(x), 1, S.BLOCK_LEN, rng)[0]
    xp = x[perm]
    assert abs(S.spearman(xp, y_t1)) < 0.25
    _ic2, p_perm = S.p_block(xp, y_t1, B=2000, rng=np.random.default_rng(2))
    assert p_perm > 0.01


def test_stationary_perm_null_is_centred(y_t1):
    """The block-permutation null of an unrelated feature is centred at 0 with sd near 1/sqrt(n)."""
    rng = np.random.default_rng(3)
    x = rng.standard_normal(len(y_t1))
    null = S.ic_block_null(S.rank_cols(x), S.rank_cols(y_t1), B=4000, rng=np.random.default_rng(4))
    assert abs(null.mean()) < 0.01
    assert 0.5 / np.sqrt(len(y_t1)) < null.std() < 2.0 / np.sqrt(len(y_t1))


def test_embargo_removes_two_decisions_each_side():
    """M8: with embargo=2 the training set excludes two rows on each side of every held-out block. Checked
    against a manual implementation on data where a leak through the neighbours would change the forecast."""
    n = 200
    blk = np.repeat(np.arange(10), 20)  # ten regime blocks of 20 decisions
    blocks = list(range(10))
    rng = np.random.default_rng(5)
    F = rng.standard_normal((n, 2))
    y = F[:, 0] + 0.1 * rng.standard_normal(n)
    for b in blocks[1:]:  # the two rows just before each block are outliers the embargo must remove
        start = b * 20
        y[start - 2:start] += 5.0
    got = loro_pred(F, y, blk, blocks, embargo=2)
    man = np.full(n, np.nan)
    for b in blocks:
        te = np.where(blk == b)[0]
        tr = np.ones(n, bool)
        tr[te] = False
        lo, hi = max(0, te[0] - 2), min(n, te[-1] + 3)
        tr[lo:hi] = False
        mu, sd = F[tr].mean(0), F[tr].std(0)
        Z = (F[tr] - mu) / sd
        ym = y[tr].mean()
        w = np.linalg.solve(Z.T @ Z + 10.0 * np.eye(2), Z.T @ (y[tr] - ym))
        man[te] = ((F[te] - mu) / sd) @ w + ym
    assert np.allclose(got, man, equal_nan=True, atol=1e-10)
    assert not np.allclose(got, loro_pred(F, y, blk, blocks, embargo=0), equal_nan=True)


def test_bh_threshold_reachable_with_B20000():
    """FH task 12: with B=20000 the smallest attainable p (1/(B+1)) is below the BH threshold 0.10/m for the
    pre-registered family (m = 48 features) and for the intended maximum (m = 60)."""
    B = S.B_SCREEN
    assert B >= 20000
    assert 1.0 / (B + 1) < 0.10 / 60 < 0.10 / 48 + 1e-12


def test_bh_q_matches_reference():
    """BH q-values on a hand-computed example."""
    p = np.array([0.01, 0.04, 0.03, 0.005])
    q = bh_q(p)
    assert np.allclose(q, [0.02, 0.04, 0.04, 0.02])
    rej = S.bh_reject(p, alpha=0.10)
    assert rej.sum() == 4 and S.bh_reject(np.array([0.5, 0.6]), 0.1).sum() == 0


@pytest.mark.slow
def test_noise_feature_null_calibration(y_t1):
    """M9: 200 independent standard-normal features tested against the real target give block-permutation p
    values that are uniform (KS p > 0.01) and IC ~ 0."""
    rng = np.random.default_rng(20260101)
    n = len(y_t1)
    X = rng.standard_normal((n, 200))
    Xr, yr = S.rank_cols(X), S.rank_cols(y_t1)
    obs = S.obs_ic_vector(Xr, yr)
    null = S.null_matrix(Xr, yr, B=20000, rng=np.random.default_rng(9))
    p = (np.sum(np.abs(null) >= np.abs(obs)[None, :], axis=0) + 1) / 20001
    stat, pv = kstest(p, "uniform")
    assert pv > 0.01, f"block-permutation p-values not uniform (KS p={pv:.3f})"
    assert abs(obs.mean()) < 3 / np.sqrt(n)


@pytest.mark.slow
def test_power_curve_reported_and_consistent():
    """FH task 12: the power curve and the minimum detectable IC exist and match the stored summary. The v4.1
    design (B=20000) is the one reported; the claim 'delta IC 0.05 at 80% power' is checked, not assumed."""
    summ_path = os.path.join(SCREEN_DIR, "screen_summary.json")
    curve_path = os.path.join(SCREEN_DIR, "power_curve.csv")
    summ = json.load(open(require(summ_path)))
    curve = pd.read_csv(require(curve_path))
    assert summ["B_screen"] >= 20000
    p05 = float(curve.query("delta_IC == 0.05 and design.str.startswith('v4.1 analytic')")["power"].iloc[0])
    assert abs(p05 - 0.0767) < 0.2  # sanity band; the stored value is the reference
    mde = summ["min_detectable_delta_IC_power80_analytic_m60"]
    assert mde is not None and mde > 0.05, "the screen would detect IC 0.05 at 80%: re-check the design"
