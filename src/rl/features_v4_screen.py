"""Screening statistics for the v4.1 feature selection experiment (FH task 12).

Univariate test of a feature f against a target y on decision rows (Spearman IC):
  * p_block  : two-sided circular BLOCK-PERMUTATION p-value of the target (block length L), B draws
               (B >= 20000 for the screen). Vectorised. Null: IC of f with a block-permuted y, which keeps
               y's autocorrelation and breaks the link to f.
  * p_fisher : analytic p-value, Fisher z with an effective sample size n_eff that corrects for the lag-1
               autocorrelation of the ranks of f and y (Bartlett-type). Used for the power curve, and checked
               against p_block in the tests.
BH-FDR is applied across the PRE-REGISTERED primary family only (targets listed in PRIMARY_TARGETS).
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm, rankdata, spearmanr

PRIMARY_TARGETS = ("T1_mdd",)  # pre-registered: one target x the feature family (48 tests <= 60)
BLOCK_LEN = 10
B_SCREEN = 20000


def rank_cols(x: np.ndarray) -> np.ndarray:
    return rankdata(x, axis=0)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(spearmanr(x, y).correlation)


def _centre(r: np.ndarray) -> np.ndarray:
    r = r - r.mean(axis=-1, keepdims=True)
    return r / np.sqrt((r * r).sum(axis=-1, keepdims=True))


def block_perm_indices(n: int, B: int, L: int, rng: np.random.Generator) -> np.ndarray:
    """(B, n) index array of circular block permutations: cut at a random shift, shuffle the blocks."""
    nb = int(np.ceil(n / L))
    shift = rng.integers(0, n, size=B)
    order = np.argsort(rng.random((B, nb)), axis=1)
    base = (order[:, :, None] * L + np.arange(L)[None, None, :]).reshape(B, nb * L)
    return (base[:, :n] + shift[:, None]) % n


def ic_block_null(x_rank: np.ndarray, y_rank: np.ndarray, B: int = B_SCREEN, L: int = BLOCK_LEN,
                  rng: np.random.Generator | None = None) -> np.ndarray:
    """Null distribution of the Spearman IC between a fixed feature (ranks x_rank) and block-permuted y."""
    rng = rng or np.random.default_rng(0)
    n = len(y_rank)
    idx = block_perm_indices(n, B, L, rng)
    yb = y_rank[idx]  # (B, n)
    xc = _centre(x_rank)
    yc = _centre(yb)
    return yc @ xc


def p_block(x: np.ndarray, y: np.ndarray, B: int = B_SCREEN, L: int = BLOCK_LEN,
            rng: np.random.Generator | None = None) -> tuple[float, float]:
    """(IC, two-sided block-permutation p-value)."""
    m = np.isfinite(x) & np.isfinite(y)
    xr, yr = rank_cols(x[m]), rank_cols(y[m])
    obs = float(_centre(xr) @ _centre(yr))
    null = ic_block_null(xr, yr, B=B, L=L, rng=rng)
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (B + 1)
    return obs, float(p)


def lag1_autocorr(r: np.ndarray) -> float:
    r = r - r.mean()
    den = float(r @ r)
    return float(r[1:] @ r[:-1] / den) if den > 0 else 0.0


def n_eff(x: np.ndarray, y: np.ndarray) -> float:
    n = int(np.sum(np.isfinite(x) & np.isfinite(y)))
    rx, ry = lag1_autocorr(rank_cols(x[np.isfinite(x) & np.isfinite(y)])), \
        lag1_autocorr(rank_cols(y[np.isfinite(x) & np.isfinite(y)]))
    k = rx * ry
    return max(4.0, n * (1 - k) / (1 + k))


def p_fisher(rho: float, neff: float) -> float:
    if not np.isfinite(rho) or neff <= 3:
        return float("nan")
    z = np.arctanh(np.clip(rho, -0.999999, 0.999999)) * np.sqrt(neff - 3)
    return float(2 * norm.sf(abs(z)))


def bh_q(p) -> np.ndarray:
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


def bh_reject(p, alpha: float = 0.10) -> np.ndarray:
    """Benjamini-Hochberg decisions (step-up): reject the k smallest p-values with the largest k such that
    p_(k) <= k * alpha / m."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p)
    ok = p[order] <= (np.arange(1, m + 1) * alpha / m)
    rej = np.zeros(m, dtype=bool)
    if ok.any():
        kmax = np.max(np.where(ok)[0])
        rej[order[: kmax + 1]] = True
    return rej


def plant_feature(y: np.ndarray, delta_ic: float, rng: np.random.Generator) -> np.ndarray:
    """A feature whose population Spearman IC with y is delta_ic (Gaussian copula: rho = 2 sin(pi*delta/6)).
    y is ranked to normal scores first, so the planted IC is delta regardless of y's marginal."""
    n = len(y)
    ys = norm.ppf((rankdata(y) - 0.5) / n)
    ys = (ys - ys.mean()) / ys.std()
    rho = 2.0 * np.sin(np.pi * delta_ic / 6.0)
    e = rng.standard_normal(n)
    return rho * ys + np.sqrt(max(0.0, 1 - rho * rho)) * e


def null_matrix(X_rank: np.ndarray, y_rank: np.ndarray, B: int, L: int = BLOCK_LEN,
                rng: np.random.Generator | None = None) -> np.ndarray:
    """(B, m) matrix of Spearman ICs between each of the m columns of X_rank (ranks) and a block-permuted
    y. One set of B permutations is shared by all columns, so the cost is one (B x n) by (n x m) product."""
    rng = rng or np.random.default_rng(0)
    idx = block_perm_indices(len(y_rank), B, L, rng)
    Yc = _centre(y_rank[idx])
    Xc = _centre(X_rank.T).T  # centre each column
    return Yc @ Xc


def obs_ic_vector(X_rank: np.ndarray, y_rank: np.ndarray) -> np.ndarray:
    return _centre(X_rank.T) @ _centre(y_rank)


def loro_pred(F: np.ndarray, y: np.ndarray, blk: np.ndarray, blocks, alpha: float = 10.0,
              embargo: int = 2) -> np.ndarray:
    """Leave-one-regime-out ridge. embargo>0 removes that many rows on each side of the held-out block from
    the training set (purge/embargo, M8)."""
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


def ar1(n: int, phi: float, rng: np.random.Generator) -> np.ndarray:
    """Standard-normal AR(1) path with lag-1 correlation phi (stationary start). Used for the power analysis:
    real features are persistent (median lag-1 rank autocorrelation ~0.97), so planted and null columns must be
    persistent too, otherwise the effective sample size is overstated."""
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0] / np.sqrt(1 - phi * phi) if abs(phi) < 1 else e[0]
    s = np.sqrt(max(1e-12, 1 - phi * phi))
    for t in range(1, n):
        x[t] = phi * x[t - 1] + s * e[t]
    return x


def plant_feature_ar(y: np.ndarray, delta_ic: float, phi: float, rng: np.random.Generator) -> np.ndarray:
    """Planted feature x = rho*ys + sqrt(1-rho^2)*AR1(phi), rho = 2 sin(pi*delta/6): population Spearman ~ delta,
    with the persistence of a real feature. ys = normal scores of y."""
    n = len(y)
    ys = norm.ppf((rankdata(y) - 0.5) / n)
    ys = (ys - ys.mean()) / ys.std()
    rho = 2.0 * np.sin(np.pi * delta_ic / 6.0)
    return rho * ys + np.sqrt(max(0.0, 1 - rho * rho)) * ar1(n, phi, rng)


def ar1_matrix(n: int, m: int, phi: float, rng: np.random.Generator) -> np.ndarray:
    """(n, m) matrix of independent stationary AR(1) columns (vectorised over columns)."""
    e = rng.standard_normal((n, m))
    x = np.empty((n, m))
    x[0] = e[0] / np.sqrt(1 - phi * phi)
    s = np.sqrt(1 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + s * e[t]
    return x
