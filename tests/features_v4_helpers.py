"""Shared helpers for the v4.1 feature certification tests (not a test module).

Inputs are read from runs_fh/ in this worktree (built locally, not committed). A missing input SKIPS
by default so a clean checkout stays green. Set V4_REQUIRE_ARTIFACTS=1 to make a missing input a
FAILURE, so a green run in certification means the checks actually ran.
"""
import os
import pickle

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(ROOT, "runs_fh", "features_v4_1")
HIST_PATH = os.path.join(OUT_DIR, "history_v41.pkl")
DAILY_PATH = os.path.join(OUT_DIR, "daily_v4.parquet")
GRID14_PATH = os.path.join(OUT_DIR, "grid_14d_v4.parquet")
GRID8W_PATH = os.path.join(OUT_DIR, "grid_8w_v4.parquet")
META_PATH = os.path.join(OUT_DIR, "feature_meta.csv")
MANIFEST_PATH = os.path.join(OUT_DIR, "manifest.json")
H1_CACHE_DIR = os.path.join(ROOT, "runs_fh", "inputs", "h1")  # copied from H1 cache (reference only, not used by the build)
H1_8W = os.path.join(H1_CACHE_DIR, "8w_base.pkl")
H1_14D = os.path.join(H1_CACHE_DIR, "14d_base.pkl")

EVAL_START = pd.Timestamp("2008-01-01")
EVAL_END = pd.Timestamp("2026-04-24")  # end of the certified window; the sealed holdout starts 2026-05-01
FORCED_DATES = ["2008-10-10", "2020-03-16", "2022-06-15"]
MIN_COMPARED = 30  # a truncation comparison must compare at least this many non-NaN features


def require(path: str):
    if not os.path.exists(path):
        msg = (f"required input missing: {path} (run scripts/features_v4_history_build.py and "
               f"scripts/features_v4_materialize.py)")
        if os.environ.get("V4_REQUIRE_ARTIFACTS") == "1":
            pytest.fail(msg)
        pytest.skip(msg + " [set V4_REQUIRE_ARTIFACTS=1 to fail instead]")
    return path


def load_history() -> dict:
    with open(require(HIST_PATH), "rb") as f:
        h = pickle.load(f)
    h.pop("_meta", None)
    h.pop("universe_mask_absent", None)
    return h


def load_meta() -> dict:
    """The history _meta block (end date, origin, B.5 control dates)."""
    with open(require(HIST_PATH), "rb") as f:
        return pickle.load(f)["_meta"]


def load_daily() -> pd.DataFrame:
    return pd.read_parquet(require(DAILY_PATH))


def truncate(H: dict, d) -> dict:
    d = pd.Timestamp(d)
    return {k: (v.loc[:d] if hasattr(v, "loc") else v) for k, v in H.items()}


def corrupt_after(H: dict, d, mode: str, rng=None) -> dict:
    """Same index; every value dated after d is replaced.

    mode='nan'   : NaN after d.
    mode='noise' : bootstrap draws (with replacement) from the pre-d values of the same column.
    """
    d = pd.Timestamp(d)
    out = {}
    for k, v in H.items():
        if not hasattr(v, "loc"):
            out[k] = v
            continue
        v2 = v.copy()
        post = v2.index > d
        if post.any():
            n_post = int(post.sum())
            if mode == "nan":
                if isinstance(v, pd.DataFrame):
                    for c in v2.columns:
                        v2.loc[post, c] = False if v2[c].dtype == bool else np.nan
                else:
                    v2.loc[post] = False if v2.dtype == bool else np.nan
            elif mode == "noise":
                pre = v.loc[:d]
                if isinstance(v, pd.DataFrame):
                    for c in v2.columns:
                        if v2[c].dtype == bool:
                            v2.loc[post, c] = rng.random(n_post) < 0.5
                        else:
                            vals = pre[c].values[np.isfinite(pre[c].values)]
                            # a name with no history before d (listed later) stays NaN after d
                            v2.loc[post, c] = rng.choice(vals, size=n_post) if len(vals) else np.nan
                else:
                    vals = pre.values[np.isfinite(pre.values)]
                    v2.loc[post] = rng.choice(vals, size=n_post)
            else:
                raise ValueError(mode)
        out[k] = v2
    return out


def rows_match(a: pd.Series, b: pd.Series, names, rtol=1e-9, atol=1e-12):
    """Return (bad_names, n_compared). NaN equals NaN; a NaN on one side only is a mismatch."""
    bad, n = [], 0
    for k in names:
        x, y = a[k], b[k]
        if pd.isna(x) and pd.isna(y):
            continue
        n += 1
        if pd.isna(x) or pd.isna(y) or not np.isclose(float(x), float(y), rtol=rtol, atol=atol):
            bad.append(k)
    return bad, n


def probe_dates(index, n_random=100, seed=20261127):
    """n_random dates uniform over the certified window plus the forced crisis dates."""
    idx = index[(index >= EVAL_START) & (index <= EVAL_END)]
    forced = [min(idx, key=lambda t: abs((t - pd.Timestamp(f)).days)) for f in FORCED_DATES]
    rng = np.random.default_rng(seed)
    pool = [t for t in idx if t not in forced]
    pick = rng.choice(len(pool), size=max(0, n_random - len(forced)), replace=False)
    return sorted(set(forced + [pool[i] for i in sorted(pick)]))


def ic(x, y):
    from scipy.stats import spearmanr
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 20:
        return np.nan
    return spearmanr(x[m], y[m]).correlation


def circ_block_perm(y, rng, L=10):
    """Circular block permutation (block length L) of a series, as in the screen."""
    y = np.asarray(y, float)
    n = len(y)
    shift = rng.integers(0, n)
    z = np.roll(y, shift)
    nb = int(np.ceil(n / L))
    pad = np.resize(z, nb * L)
    blocks = pad.reshape(nb, L)
    order = rng.permutation(nb)
    return blocks[order].ravel()[:n]


def bh_q(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    q = np.empty(m)
    prev = 1.0
    for rank, i in enumerate(order[::-1]):
        k = m - rank
        prev = min(prev, p[i] * m / k)
        q[i] = prev
    return q


def loro_pred(F, y, blk, blocks, alpha=10.0, embargo=2):
    """Leave-one-regime-out ridge. embargo>0 removes that many rows on each side of the held-out block
    from the training set (purge/embargo, M8)."""
    pred = np.full(len(y), np.nan)
    n = len(y)
    for b in blocks:
        te = blk == b
        tr = ~te
        if embargo > 0 and te.any():
            pos = np.where(te)[0]
            lo, hi = max(0, pos[0] - embargo), min(n, pos[-1] + 1 + embargo)
            tr = tr.copy()
            tr[lo:hi] = False
        if tr.sum() < 50 or te.sum() == 0:
            continue
        mu, sd = F[tr].mean(0), F[tr].std(0)
        sd = np.where(sd < 1e-9, 1.0, sd)
        Z = (F[tr] - mu) / sd
        Zt = (F[te] - mu) / sd
        ym = y[tr].mean()
        k = Z.shape[1]
        w = np.linalg.solve(Z.T @ Z + alpha * np.eye(k), Z.T @ (y[tr] - ym))
        pred[te] = Zt @ w + ym
    return pred
