"""BD2 pipeline: walk-forward folds, learners L0/L0b/L1/L2, controls C1/C2, metrics and bootstrap.

Labels: U1(d,a) = log(1 + R_gross(d,a)) (churn excluded from labels, spec section 2).
Decoding (L2): argmax_a [ yhat_a(x) - (COST_BPS/1e4) * |a - p| ], p = previous share.
Evaluation: every path charges 10 bps per unit turnover via bd_core.period_returns.

Folds (spec section 5): test year Y+1 for Y = 2012..2025; training = valid decisions dated <= Y whose
index is <= (first test index - 3), i.e. a 2-decision purge before each test fold. The L2 ridge alpha
is chosen by an inner walk-forward over the last three training years only.
One valid mask is shared by all learners (identical samples), see `common_mask`.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from rl import bd_core as C

ALPHA_GRID = (1.0, 10.0, 100.0)  # L2 ridge, pre-registered small grid
TR_ALPHA = 10.0  # L1 (FM TR sizer) ridge alpha, fixed in FM
TR_COLS = ["rv_u_21", "rv_u_63", "rv_s_21", "rv_s_63", "vix_level", "stress_b5", "prev_dd14"]
PURGE = 2
INNER_YEARS = 3
MIN_TRAIN = 20  # decisions; 40 would drop the 8w folds 2013-2015 (deviation recorded in REPORT.md)
MIN_INNER_TRAIN = 15
ALPHA_DEFAULT = 10.0
EXP_YEARS = list(range(2013, 2027))
COST_UNIT = C.COST_BPS / 1e4


# ----------------------------------------------------------------------------- labels / contexts
def labels(g: C.Grid, arms) -> np.ndarray:
    """N x K matrix of U1(d,a) on gross (no-cost) period returns."""
    Y = np.full((g.n, len(arms)), np.nan)
    for i in range(g.n):
        for k, a in enumerate(arms):
            r, _ = C.period_returns(g, i, a, 0.0, 0.0)
            Y[i, k] = np.log1p(C.wealth_stats(r)["R"])
    return Y


def gross_risk(g: C.Grid):
    """M = -MaxDD (drawdown magnitude) and realised vol of the 100% book over each period, gross."""
    M = np.empty(g.n)
    V = np.empty(g.n)
    for i in range(g.n):
        r, _ = C.period_returns(g, i, 1.0, 1.0, 0.0)
        ws = C.wealth_stats(r)
        M[i] = -ws["MaxDD"]
        V[i] = ws["vol"]
    return M, V


def context_x0(g: C.Grid, x0daily: pd.DataFrame) -> np.ndarray:
    return x0daily.reindex(g.dates)[C.X0_COLS].values


def context_tr(g: C.Grid, daily_table: pd.DataFrame) -> np.ndarray:
    return daily_table.reindex(g.dates)[TR_COLS].values


def shuffle_blocks(X: np.ndarray, rng: np.random.Generator, block: int = 4) -> np.ndarray:
    """Block-shuffle rows of X (consecutive blocks, block order permuted)."""
    n = len(X)
    nb = int(np.ceil(n / block))
    order = rng.permutation(nb)
    idx = np.concatenate([np.arange(b * block, min((b + 1) * block, n)) for b in order])
    return X[idx]


def common_mask(*arrays) -> np.ndarray:
    m = None
    for a in arrays:
        a = np.asarray(a, dtype=float)
        f = np.all(np.isfinite(a.reshape(len(a), -1)), axis=1)
        m = f if m is None else (m & f)
    return m


# ----------------------------------------------------------------------------- folds
def fold_sets(g: C.Grid, valid: np.ndarray, years=EXP_YEARS):
    """Yield (year, train_idx, test_idx). Train: valid decisions dated <= year-1 (i.e. Y = year-1) and
    index <= first test index - (PURGE + 1)."""
    yrs = np.asarray(g.dates.year)
    for y in years:
        test = np.where((yrs == y) & valid)[0]
        if len(test) == 0:
            continue
        k = int(test.min())
        train = np.where(valid & (yrs < y) & (np.arange(g.n) <= k - PURGE - 1))[0]
        if len(train) < MIN_TRAIN:
            continue
        yield y, train, test


# ----------------------------------------------------------------------------- ridge / decode
def _standardise(Xtr, Xte):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def ridge_fit_predict(Xtr, Ytr, Xte, alpha):
    """Ridge with unpenalised intercept, standardisation on the training block. Ytr: n or n x K."""
    A, B = _standardise(Xtr, Xte)
    A1 = np.hstack([A, np.ones((len(A), 1))])
    B1 = np.hstack([B, np.ones((len(B), 1))])
    P = alpha * np.eye(A1.shape[1])
    P[-1, -1] = 0.0
    beta = np.linalg.solve(A1.T @ A1 + P, A1.T @ Ytr)
    return B1 @ beta


def decode(yhat: np.ndarray, arms, p0: float = 0.0) -> np.ndarray:
    """Sequential cost-aware argmax over arms. yhat: m x K predicted U1 per arm per decision."""
    arms = np.asarray(arms, dtype=float)
    out = np.empty(len(yhat))
    p = p0
    for t in range(len(yhat)):
        score = yhat[t] - COST_UNIT * np.abs(arms - p)
        k = int(np.argmax(score))
        out[t] = arms[k]
        p = arms[k]
    return out


def choose_alpha(g: C.Grid, X, Y, arms, train, last_train_year: int) -> float:
    """Inner walk-forward over the last INNER_YEARS training years. Score = mean realised net U1 of the
    cost-aware policy on each inner test year (policy restarted at p = 0 each inner year)."""
    yrs = np.asarray(g.dates.year)
    best, best_s = ALPHA_DEFAULT, -np.inf
    scores = {a: [] for a in ALPHA_GRID}
    for y in range(last_train_year - INNER_YEARS + 1, last_train_year + 1):
        test = train[yrs[train] == y]
        if len(test) < 5:
            continue
        k = int(test.min())
        itr = train[(yrs[train] < y) & (train <= k - PURGE - 1)]
        if len(itr) < MIN_INNER_TRAIN:
            continue
        for a in ALPHA_GRID:
            yhat = ridge_fit_predict(X[itr], Y[itr], X[test], a)
            shares = decode(yhat, arms, 0.0)
            scores[a].append(float(np.mean(C.run_shares(g, test, shares, p0=0.0)["U1"])))
    for a in ALPHA_GRID:
        if scores[a]:
            s = float(np.mean(scores[a]))
            if s > best_s:
                best, best_s = a, s
    return best


# ----------------------------------------------------------------------------- L1 map
def fit_map(pred_tr: np.ndarray, train_idx: np.ndarray, g: C.Grid, arms):
    """FM monotone map: 4 in-fold quartile bins on predicted drawdown magnitude; nonincreasing levels
    from `arms` (bin 0 = lowest risk gets the highest level), chosen by in-fold Calmar of the net path."""
    cuts = np.quantile(pred_tr, [0.25, 0.5, 0.75])
    bins = np.digitize(pred_tr, cuts)
    lv = sorted(arms, reverse=True)
    best, best_c = None, -np.inf
    for L in itertools.combinations_with_replacement(lv, 4):
        shares = np.array(L)[bins]
        res = C.run_shares(g, train_idx, shares, p0=0.0)
        c = C.path_stats(C.flat(res["daily"]))["Calmar"]
        c = -np.inf if not np.isfinite(c) else c
        if c > best_c:
            best, best_c = L, c
    assert best is not None
    return cuts, np.array(best)


# ----------------------------------------------------------------------------- walk-forward
def fold_choice(learner: str, g: C.Grid, train, test, arms, Y, X=None, M=None, Xtr=None,
                rng=None, p0: float = 0.0, alpha: float | None = None):
    """Shares chosen on the test decisions by one learner, fitted on the train decisions only.

    learner: 'L2' (per-arm ridge on U1, X0, cost-aware decode), 'C1' (same on block-shuffled X0 in
    train and test), 'L1' (FM TR sizer: ridge on drawdown magnitude M over TR features Xtr, in-fold
    monotone map), 'L0b' (best constant arm by mean training U1), 'C2' (uniform random arm).
    alpha: fixed ridge alpha for L2/C1 (legacy split); None = inner walk-forward selection.
    Returns (shares for test, info dict).
    """
    arms = tuple(float(a) for a in arms)
    info = {}
    if learner == "L0b":
        k = int(np.argmax(np.mean(Y[train], axis=0)))
        return np.full(len(test), arms[k]), {"best_const": arms[k]}
    if learner == "C2":
        return rng.choice(np.asarray(arms), size=len(test)), info
    if learner == "L1":
        pred_tr = ridge_fit_predict(Xtr[train], M[train], Xtr[train], TR_ALPHA)
        pred_te = ridge_fit_predict(Xtr[train], M[train], Xtr[test], TR_ALPHA)
        cuts, L = fit_map(pred_tr, train, g, arms)
        info["levels"] = [float(v) for v in L]
        return L[np.digitize(pred_te, cuts)], info
    if learner in ("L2", "C1"):
        Xuse = X
        if learner == "C1":
            Xuse = X.copy()
            Xuse[train] = shuffle_blocks(X[train], rng)
            Xuse[test] = shuffle_blocks(X[test], rng)
        if alpha is None:
            alpha = choose_alpha(g, Xuse, Y, arms, train, int(g.dates[train].year.max()))
        yhat = ridge_fit_predict(Xuse[train], Y[train], Xuse[test], alpha)
        info["alpha"] = float(alpha)
        return decode(yhat, arms, p0), info
    raise ValueError(learner)


def run_walk_forward(g: C.Grid, Y: np.ndarray, arms, learner: str, valid: np.ndarray,
                     X: np.ndarray | None = None, M: np.ndarray | None = None,
                     Xtr: np.ndarray | None = None, seed: int = 0, years=EXP_YEARS):
    """Expanding walk-forward for one learner over test years `years`. The previous-share chain is
    continuous across folds (the last decision of a fold is the previous decision of the next)."""
    chosen = np.full(g.n, np.nan)
    info = []
    rng = np.random.default_rng(seed)
    for y, train, test in fold_sets(g, valid, years):
        prev = int(test[0]) - 1
        p0 = float(chosen[prev]) if prev >= 0 and np.isfinite(chosen[prev]) else 0.0
        sh, inf = fold_choice(learner, g, train, test, arms, Y, X=X, M=M, Xtr=Xtr, rng=rng, p0=p0)
        chosen[test] = sh
        info.append({"year": y, "n_train": int(len(train)), "n_test": int(len(test)), **inf})
    return {"chosen": chosen, "info": info}


def pooled_eval(g: C.Grid, chosen: np.ndarray, label: str) -> dict:
    """Evaluate chosen shares on the pooled test decisions; the previous-share chain starts at 0."""
    idx = np.where(np.isfinite(chosen))[0]
    res = C.run_shares(g, idx, chosen[idx], p0=0.0)
    res["label"] = label
    res["years"] = np.asarray(g.dates[idx].year)
    return res


def matched_static(g: C.Grid, res_learner: dict, label: str) -> dict:
    """Constant share equal to the learner's time-weighted average equity on the same pooled days.
    The time-weighted average of a constant share is the share itself, so the numerical inverse is
    exact; the target is still computed from the realised path."""
    _, _, share = C.flatten(res_learner)
    s_star = float(np.mean(share))
    res = C.run_shares(g, res_learner["idx"], np.full(len(res_learner["idx"]), s_star), p0=0.0)
    res["label"] = label
    res["years"] = res_learner["years"]
    res["share_star"] = s_star
    return res


# ----------------------------------------------------------------------------- metrics
def summarise(res: dict, label: str | None = None) -> dict:
    """Metrics on the pooled daily path of a (possibly subset) result, net of 10 bps."""
    daily, dates, share = C.flatten(res)
    st = C.path_stats(daily)
    yrs = (dates[-1] - dates[0]).days / 365.25 if len(dates) > 1 else np.nan
    return {
        "label": label or res.get("label", ""),
        "CAGR": st["CAGR"], "MaxDD": st["MaxDD"], "vol": st["vol"], "Sharpe": st["Sharpe"],
        "Sortino": st["Sortino"], "Calmar": st["Calmar"], "n_days": st["n_days"],
        "n_decisions": int(len(res["idx"])),
        "turnover_per_year": float(np.sum(res["turn"]) / yrs) if yrs > 0 else np.nan,
        "avg_equity": float(np.mean(share)) if len(share) else np.nan,
        "equity_std_daily": float(np.std(share, ddof=1)) if len(share) > 1 else np.nan,
        "equity_std_decision": float(np.std(res["shares"], ddof=1)) if len(res["shares"]) > 1 else np.nan,
        "mean_U1": float(np.mean(res["U1"])) if len(res["U1"]) else np.nan,
        "mdd_2020": C.window_mdd(daily, dates, *C.WINDOW_2020),
        "mdd_2022": C.window_mdd(daily, dates, *C.WINDOW_2022),
    }


def dec_window(res: dict, start: str, end: str) -> dict:
    d = res["dec_dates"]
    m = (d >= pd.Timestamp(start)) & (d <= pd.Timestamp(end))
    return C.subset(res, m)


def per_fold(res: dict) -> pd.DataFrame:
    rows = []
    for y in sorted(set(res["years"].tolist())):
        sub = C.subset(res, res["years"] == y)
        daily, _, _ = C.flatten(sub)
        st = C.path_stats(daily)
        rows.append({"year": int(y), "CAGR": st["CAGR"], "MaxDD": st["MaxDD"], "Sharpe": st["Sharpe"],
                     "Calmar": st["Calmar"], "mean_U1": float(np.mean(sub["U1"]))})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- bootstrap
def stationary_indices(n: int, mean_block: int, rng: np.random.Generator) -> np.ndarray:
    """Politis-Romano stationary bootstrap indices, geometric block lengths with mean mean_block."""
    p = 1.0 / max(mean_block, 1)
    idx = np.empty(n, dtype=int)
    cur = int(rng.integers(n))
    for t in range(n):
        if t == 0 or rng.random() < p:
            cur = int(rng.integers(n))
        else:
            cur = (cur + 1) % n
        idx[t] = cur
    return idx


def paired_bootstrap(res_a: dict, res_b: dict, B: int = 1000, block: int = 10, seed: int = 1) -> dict:
    """Paired stationary block bootstrap over decisions (same draw for both paths).
    Returns point, SE (bootstrap sd), 95% percentile CI, z = point/SE and one-sided p for (a - b)."""
    n = len(res_a["daily"])
    assert n == len(res_b["daily"])
    rng = np.random.default_rng(seed)
    pa = C.path_stats(C.flatten(res_a)[0])
    pb = C.path_stats(C.flatten(res_b)[0])
    point = {"dU1": float(np.mean(res_a["U1"]) - np.mean(res_b["U1"])),
             "dSharpe": pa["Sharpe"] - pb["Sharpe"], "dCalmar": pa["Calmar"] - pb["Calmar"]}
    dU, dS, dC = [], [], []
    for _ in range(B):
        J = stationary_indices(n, block, rng)
        dU.append(float(np.mean(res_a["U1"][J]) - np.mean(res_b["U1"][J])))
        sa = C.path_stats(C.flat([res_a["daily"][j] for j in J]))
        sb = C.path_stats(C.flat([res_b["daily"][j] for j in J]))
        dS.append(sa["Sharpe"] - sb["Sharpe"])
        dC.append(sa["Calmar"] - sb["Calmar"])
    out = {}
    for key, arr in [("dU1", dU), ("dSharpe", dS), ("dCalmar", dC)]:
        arr = np.asarray(arr, dtype=float)
        arr = arr[np.isfinite(arr)]
        pt = point[key]
        se = float(np.std(arr, ddof=1))
        out[key] = {"point": pt, "se": se, "lo95": float(np.percentile(arr, 2.5)),
                    "hi95": float(np.percentile(arr, 97.5)), "z": pt / se if se > 0 else np.nan,
                    "p_one_sided": float(np.mean(arr <= 0))}
    return out
