"""Candidate causal risk feature library v4.1 (experiment FH; certification gate in
docs/phases/rl_feature_certification.md).

Single entry point: ``features_at(date, history)`` returns one row of features for ``date`` using ONLY
history rows dated <= ``date``. ``build_panel(history)`` computes the whole panel in one pass; every raw
column is a trailing or expanding operation, so row t depends only on data <= t (tests/test_features_v4_*).

History (dict of pandas objects, see src/rl/features_v4_history.py for the canonical construction):
  spy, iwm, tlt, gld, uup, vix         : Series of closes (vix = ^VIX close, index points)
  spy_high, spy_low                    : Series (range vol)
  stocks                               : DataFrame of closes, dates x tickers (502 current constituents)
  universe_mask                        : DataFrame bool, dates x tickers. Point-in-time ADV eligibility
                                         (data/artifacts/universe_mask_sp500.parquet). NOT index membership.
  unit_w                               : DataFrame dates x tickers, unit-book weights in force at each date
                                         (gross 1, known at that date)
  unit_ret                             : Series, daily return of the unit book (canonical, daily-rebalanced
                                         to the B.5 weights in force; NaN, never zero, when undefined)
  base_ret                             : Series, daily return of the B.5+B.4 baseline book (NaN before inception)
  base_gross                           : Series, baseline gross exposure in force at each date
  stress                               : Series, B.5 stress score in force at each date

Timing (M2, documented in docs/phases/rl_feature_certification.md section 0):
  A decision at the close of t uses data up to and including the close of t. The env fills at the close
  of t and earns returns from t+1 (PortfolioEnvV2._compute_daily_returns). VIX is the close of t (same
  day, so it is available only at or after the close of t; a decision at t is therefore taken at the close).
  Calendar flags are known in advance and are not look-ahead.

Normalisation (M4): expanding mean and std with a minimum of Z_MIN observations, z clipped at +-3.
Pre-inception NAV-derived inputs are NaN (not zero), so they never enter a baseline.
Survivorship (M-item 7): breadth and cross-sectional features use only names with universe_mask(t)=True.
The raw stock set is 502 current constituents, so 2008-2014 breadth is flagged survivor-biased.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ORIGIN = pd.Timestamp("2006-01-03")
Z_MIN = 126  # expanding z-score minimum (v4.1; v4 used 252, see FH coverage table)
ANN = np.sqrt(252.0)
GARCH_ALPHA, GARCH_GAMMA, GARCH_BETA = 0.05, 0.08, 0.90  # fixed, NOT fitted (documented hand-set values)
KM_N_INIT, KM_SEED = 10, 0
BOOK_FEATURES_NAV = ("dd_b", "dsp_b", "rec_b", "spd_b_5", "spd_b_21", "base_gross", "worst_dec_share",
                     "corr_held_21", "corr_held_63", "disp_held_21", "base_vol_21", "base_vol_63",
                     "base_beta_63", "stress_b5")

# name -> (group, transform). transform: "log" applies log before the expanding z-score.
# v4.1 removals (FH task 2): hhi_u and n_names (constant), invvar_u_21 and invvar_s_21 (exact monotone
# copies of rv_*_21 after log-z), base_ret_21 (identical to spd_b_21).
FEATURES = {
    # (a) volatility dynamics
    "rv_u_5": ("a_vol", "log"), "rv_u_21": ("a_vol", "log"), "rv_u_63": ("a_vol", "log"),
    "rv_s_5": ("a_vol", "log"), "rv_s_21": ("a_vol", "log"), "rv_s_63": ("a_vol", "log"),
    "vr_u_5_63": ("a_vol", "raw"), "vr_s_5_63": ("a_vol", "raw"),
    "vov_u_63": ("a_vol", "log"),
    "semidn_u_21": ("a_vol", "log"), "downup_u_63": ("a_vol", "log"), "downup_s_63": ("a_vol", "log"),
    "vix_level": ("a_vol", "log"), "vix_chg_5": ("a_vol", "raw"), "vrp_vs_rv21": ("a_vol", "raw"),
    "har_s_fc": ("a_vol", "log"), "vrp_har_s": ("a_vol", "raw"),
    "ewdn_u_126": ("a_regime", "log"),
    "regime_km_bear": ("a_regime", "raw"), "regime_simple_bear": ("a_regime", "raw"),
    # (b) drawdown state
    "dd_s": ("b_dd", "raw"), "dsp_s": ("b_dd", "raw"), "rec_s": ("b_dd", "raw"),
    "spd_s_5": ("b_dd", "raw"), "spd_s_21": ("b_dd", "raw"),
    "dd_b": ("b_dd", "raw"), "dsp_b": ("b_dd", "raw"), "rec_b": ("b_dd", "raw"),
    "spd_b_5": ("b_dd", "raw"), "spd_b_21": ("b_dd", "raw"),
    # (c) cross-sectional risk of the traded book
    "corr_held_21": ("c_xs", "raw"), "corr_held_63": ("c_xs", "raw"), "disp_held_21": ("c_xs", "log"),
    "worst_dec_share": ("c_xs", "raw"), "beta_u_63": ("c_xs", "raw"),
    # (d) breadth (point-in-time universe mask; survivor-biased before 2015, see meta)
    "pct_gt50": ("d_breadth", "raw"), "pct_gt200": ("d_breadth", "raw"),
    "netnewhl": ("d_breadth", "raw"), "ew_vs_spy_63": ("d_breadth", "raw"),
    # (e) cross-asset stress
    "tlt_mom_63": ("e_xasset", "raw"), "gld_mom_63": ("e_xasset", "raw"), "uup_mom_63": ("e_xasset", "raw"),
    "tlt_vol_21": ("e_xasset", "log"), "corr_sb_21": ("e_xasset", "raw"), "corr_sb_63": ("e_xasset", "raw"),
    # (g) baseline-book state
    "base_gross": ("g_base", "raw"), "base_beta_63": ("g_base", "raw"), "stress_b5": ("g_base", "raw"),
}
FEATURE_NAMES = list(FEATURES)
# v4 -> v4.1 removals, with the reason (full table in feature_meta / docs):
#   dead or constant: hhi_u, n_names; exact duplicates: invvar_u_21, invvar_s_21, base_ret_21 (= spd_b_21);
#   calendar flags (not risk information, binary z-scores ill-defined): month_end, quarter_end;
#   |corr|>0.95 cluster members (representative in brackets): har_u_fc, garch_u_fc, base_vol_21 [rv_u_21];
#   base_vol_63 [rv_u_63]; park_s_21 [rv_s_21].
REMOVED_V41 = {
    "hhi_u": "dead: constant (EW top-20 book)", "n_names": "dead: constant (20 names)",
    "invvar_u_21": "duplicate of rv_u_21 (monotone copy after log-z)",
    "invvar_s_21": "duplicate of rv_s_21 (monotone copy after log-z)",
    "base_ret_21": "duplicate of spd_b_21 (identical formula)",
    "month_end": "calendar flag, not risk information", "quarter_end": "calendar flag, not risk information",
    "har_u_fc": "cluster |corr|>0.95 with rv_u_21 (0.959)", "garch_u_fc": "cluster |corr|>0.95 with rv_u_21 (0.955)",
    "base_vol_21": "cluster |corr|>0.95 with rv_u_21 (0.959)", "base_vol_63": "cluster |corr|>0.95 with rv_u_63 (0.963)",
    "park_s_21": "cluster |corr|>0.95 with rv_s_21 (0.958)",
    "ewdn_u_21": "cluster |corr|>0.95 with rv_u_63 (0.953 on the 14d grid)",
}
# survivor-biased before 2015: computed on the 502 current constituents (delisted names absent)
SURVIVOR_BIASED_PRE2015 = ("pct_gt50", "pct_gt200", "netnewhl", "ew_vs_spy_63", "worst_dec_share")


def _ew_down_dev(r: pd.Series, halflife: int) -> pd.Series:
    return np.sqrt((np.minimum(r, 0.0) ** 2).ewm(halflife=halflife, adjust=False).mean()) * ANN


def _har_forecast(rv_d: pd.Series, rv_w: pd.Series, rv_m: pd.Series, target: pd.Series,
                  horizon: int = 21, min_rows: int = 126) -> pd.Series:
    """Expanding OLS HAR-RV: y_s = target_s (mean of next `horizon` daily variances, known at s+horizon).
    Fit at t uses only rows s <= t - horizon, so the coefficient is causal. Returns annualised vol."""
    X = np.column_stack([np.ones(len(rv_d)), rv_d.values, rv_w.values, rv_m.values])
    y = target.values
    n = len(y)
    out = np.full(n, np.nan)
    XtX = np.zeros((4, 4))
    Xty = np.zeros(4)
    cnt = 0
    for t in range(n):
        s = t - horizon  # row s becomes usable once its target is known (at s + horizon = t)
        if s >= 0 and np.all(np.isfinite(X[s])) and np.isfinite(y[s]):
            XtX += np.outer(X[s], X[s])
            Xty += X[s] * y[s]
            cnt += 1
        if cnt >= min_rows and np.all(np.isfinite(X[t])):
            try:
                beta = np.linalg.solve(XtX + 1e-10 * np.eye(4), Xty)
                out[t] = float(X[t] @ beta)
            except np.linalg.LinAlgError:
                pass
    return pd.Series(np.sqrt(np.maximum(out, 0.0) * 252), index=rv_d.index)


def _garch_fc(r: pd.Series, min_rows: int = 126) -> pd.Series:
    """GJR-GARCH(1,1) one-step-ahead conditional volatility with FIXED parameters.

    Value at t = sqrt(252 * h_{t+1|t}): the variance forecast for day t+1 given returns up to and
    including t (the recursion is updated with r_t before it is stored). Unconditional variance is the
    expanding mean of r^2 (causal). Parameters are hand-set, not fitted (see GARCH_* constants)."""
    r2 = (r ** 2).values
    uncond = pd.Series(r2, index=r.index).expanding(min_periods=min_rows).mean().values
    h = np.full(len(r), np.nan)
    persist = GARCH_ALPHA + GARCH_GAMMA / 2 + GARCH_BETA
    prev = np.nan  # h_{t|t-1}: forecast of day t made with data to t-1
    for t in range(len(r)):
        if np.isnan(uncond[t]):
            continue
        if np.isnan(prev):
            prev = uncond[t]
        rt = r.values[t]
        rt = 0.0 if np.isnan(rt) else rt
        # update with day t's return: h_{t+1|t}
        nxt = (1 - persist) * uncond[t] + (GARCH_ALPHA + GARCH_GAMMA * (rt < 0)) * rt * rt + GARCH_BETA * prev
        h[t] = nxt
        prev = nxt
    return pd.Series(np.sqrt(np.maximum(h, 0) * 252), index=r.index)


def _regime_km(ewdn21: pd.Series, ewdn126: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Two-state k-means on log downside deviations, refit once a year on data strictly before that year.
    Output: the logit of P(bear), logit = 4 * (d_bull - d_bear) with d the distances to the fit-date
    centroids. The logit is the unsaturated form of the softmax P(bear) = sigmoid(logit): P itself rounds
    to exactly 1.0 for whole crisis years (2008), which zeroes the expanding variance (v4.1 fix, FH task 3).
    Also returns the hard state (logit > 0). Before the first refit the output is NaN. KMeans is pinned."""
    from sklearn.cluster import KMeans

    X = np.column_stack([np.log(ewdn21.clip(lower=1e-4)), np.log(ewdn126.clip(lower=1e-4))])
    idx = ewdn21.index
    prob = pd.Series(np.nan, index=idx)  # holds the logit
    years = idx.year
    centers = None
    bear_c = None
    for y in sorted(set(years)):
        first = np.where(years == y)[0][0]
        fit_rows = np.arange(first)
        ok = fit_rows[np.all(np.isfinite(X[fit_rows]), axis=1)]
        if len(ok) >= 252:  # refit needs one trading year of fit rows
            km = KMeans(n_clusters=2, n_init=KM_N_INIT, random_state=KM_SEED).fit(X[ok])
            c = km.cluster_centers_
            bear_c = int(np.argmax(c[:, 0]))
            centers = c
        if centers is None:
            continue
        seg = np.where(years == y)[0]
        d = np.linalg.norm(X[seg][:, None, :] - centers[None, :, :], axis=2)
        dbear, dbull = d[:, bear_c], d[:, 1 - bear_c]
        logit = (dbull - dbear) * 4.0
        prob.iloc[seg] = np.where(np.all(np.isfinite(X[seg]), axis=1), logit, np.nan)
    hard = (prob > 0).astype(float).where(prob.notna())
    return prob, hard


def _expz(x: pd.Series, transform: str) -> pd.Series:
    x = np.log(x.clip(lower=1e-6)) if transform == "log" else x
    m = x.expanding(min_periods=Z_MIN).mean()
    sd = x.expanding(min_periods=Z_MIN).std()
    z = (x - m) / sd.where(sd > 1e-12)
    return z.clip(-3, 3)


def _drawdown_block(nav: pd.Series, prefix: str) -> dict[str, pd.Series]:
    peak = nav.cummax()
    dd = nav / peak - 1.0
    is_peak = (nav >= peak).astype(int)
    grp = is_peak.cumsum()
    days = nav.groupby(grp).cumcount().astype(float)
    trough = nav.groupby(grp).cummin()
    span = (peak - trough).where(peak > trough)
    rec = ((nav - trough) / span).clip(0, 1).fillna(1.0)
    return {f"dd_{prefix}": dd, f"dsp_{prefix}": days + 1.0, f"rec_{prefix}": rec}


def _held_book_stats(unit_w: pd.DataFrame, R: pd.DataFrame):
    """Average pairwise correlation (21/63d) and dispersion of the names held in force at t.
    The holding set changes only at rebalances; each constant-set segment is evaluated with its
    trailing window, so each value uses only returns <= t."""
    idx = unit_w.index
    held = unit_w.values > 0
    corr21 = pd.Series(np.nan, index=idx)
    corr63 = pd.Series(np.nan, index=idx)
    disp21 = pd.Series(np.nan, index=idx)
    change = np.r_[True, np.any(held[1:] != held[:-1], axis=1)]
    starts = np.where(change)[0]
    ends = np.r_[starts[1:], len(idx)]
    for s, e in zip(starts, ends):
        names = unit_w.columns[held[s]]
        if len(names) < 3:
            continue
        rH = R[names]
        ew = rH.mean(axis=1)
        var_i = rH.rolling(63, min_periods=63).var().mean(axis=1)
        var_ew = ew.rolling(63, min_periods=63).var()
        n = len(names)
        avgcov = (var_ew - var_i / n) / (1 - 1 / n)
        avgc = (avgcov / var_i).clip(-1, 1)
        var_i21 = rH.rolling(21, min_periods=21).var().mean(axis=1)
        var_ew21 = ew.rolling(21, min_periods=21).var()
        avgc21 = (((var_ew21 - var_i21 / n) / (1 - 1 / n)) / var_i21).clip(-1, 1)
        sl = idx[s:e]
        corr63.loc[sl] = avgc.reindex(sl).values
        corr21.loc[sl] = avgc21.reindex(sl).values
        disp21.loc[sl] = rH.std(axis=1).rolling(21, min_periods=21).mean().reindex(sl).values
    return corr21, corr63, disp21


def build_panel(history: dict) -> pd.DataFrame:
    """Causal raw + expanding-z feature panel. Row t uses only history rows dated <= t."""
    spy = history["spy"].astype(float)
    idx = spy.index
    r_s = spy.pct_change(fill_method=None)
    W = history["unit_w"].reindex(idx).fillna(0.0)
    W = W.div(W.abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    # book returns are NaN before the book exists, so rolling and expanding stats ignore pre-inception rows
    live = W.abs().sum(axis=1) > 0
    live_start = live.idxmax() if live.any() else idx[-1]
    pre_live = idx < live_start
    r_u = history["unit_ret"].reindex(idx).where(~pre_live)
    r_b = history["base_ret"].reindex(idx).where(~pre_live)
    S = history["stocks"].reindex(idx).ffill()
    R = S.pct_change(fill_method=None)
    M = history["universe_mask"].reindex(index=idx, columns=S.columns).fillna(False).astype(bool)
    vix = history["vix"].reindex(idx).ffill() / 100.0
    tlt = history["tlt"].reindex(idx).ffill()
    gld = history["gld"].reindex(idx).ffill()
    uup = history["uup"].reindex(idx).ffill()
    hi = history["spy_high"].reindex(idx).ffill()
    lo = history["spy_low"].reindex(idx).ffill()
    raw = {}

    # (a) volatility
    for h in (5, 21, 63):
        raw[f"rv_u_{h}"] = r_u.rolling(h, min_periods=h).std() * ANN
        raw[f"rv_s_{h}"] = r_s.rolling(h, min_periods=h).std() * ANN
    raw["vr_u_5_63"] = raw["rv_u_5"] / raw["rv_u_63"]
    raw["vr_s_5_63"] = raw["rv_s_5"] / raw["rv_s_63"]
    raw["vov_u_63"] = raw["rv_u_21"].rolling(63, min_periods=63).std()
    dn = np.minimum(r_u, 0.0)
    up = np.maximum(r_u, 0.0)
    raw["semidn_u_21"] = np.sqrt((dn ** 2).rolling(21, min_periods=21).mean()) * ANN
    raw["downup_u_63"] = np.sqrt((dn ** 2).rolling(63, min_periods=63).mean()) / \
        np.sqrt((up ** 2).rolling(63, min_periods=63).mean())
    dns = np.minimum(r_s, 0.0)
    ups = np.maximum(r_s, 0.0)
    raw["downup_s_63"] = np.sqrt((dns ** 2).rolling(63, min_periods=63).mean()) / \
        np.sqrt((ups ** 2).rolling(63, min_periods=63).mean())
    lr = np.log(hi / lo)
    raw["park_s_21"] = np.sqrt((lr ** 2).rolling(21, min_periods=21).mean() / (4 * np.log(2))) * ANN
    raw["vix_level"] = vix
    raw["vix_chg_5"] = vix - vix.shift(5)
    raw["vrp_vs_rv21"] = vix - raw["rv_s_21"]
    raw["har_u_fc"] = _har_forecast(r_u.pow(2).rolling(1).mean(), r_u.pow(2).rolling(5).mean(),
                                    r_u.pow(2).rolling(21).mean(), r_u.pow(2).rolling(21).mean().shift(-21))
    raw["har_s_fc"] = _har_forecast(r_s.pow(2).rolling(1).mean(), r_s.pow(2).rolling(5).mean(),
                                    r_s.pow(2).rolling(21).mean(), r_s.pow(2).rolling(21).mean().shift(-21))
    raw["vrp_har_s"] = vix - raw["har_s_fc"]
    raw["garch_u_fc"] = _garch_fc(r_u)
    raw["ewdn_u_21"] = _ew_down_dev(r_u, 21).where(~pre_live)
    raw["ewdn_u_126"] = _ew_down_dev(r_u, 126).where(~pre_live)
    # regime inputs use SPY downside deviation (SPY history from ORIGIN)
    ewdn_s21 = _ew_down_dev(r_s.fillna(0.0), 21)
    ewdn_s126 = _ew_down_dev(r_s.fillna(0.0), 126)
    km_prob, km_hard = _regime_km(ewdn_s21, ewdn_s126)
    raw["regime_km_bear"] = km_prob
    simple_thr = ewdn_s21.expanding(min_periods=Z_MIN).quantile(0.75)
    raw["regime_simple_bear"] = (ewdn_s21 > simple_thr).astype(float).where(simple_thr.notna())

    # (b) drawdown state of SPY (continuous from ORIGIN) and of the baseline book (from its inception)
    nav_s = (1 + r_s.fillna(0)).cumprod()
    nav_b = (1 + r_b).cumprod()  # NaN before inception (pandas keeps NaN, no zero fill)
    raw.update(_drawdown_block(nav_s, "s"))
    db = _drawdown_block(nav_b.ffill().where(~pre_live), "b")
    for k, v in db.items():
        raw[k] = v.where(~pre_live)
    raw["dsp_s"] = np.log(raw["dsp_s"])  # already log-scale; transform "raw" in FEATURES
    raw["dsp_b"] = np.log(raw["dsp_b"])
    raw["spd_s_5"] = nav_s / nav_s.shift(5) - 1
    raw["spd_s_21"] = nav_s / nav_s.shift(21) - 1
    raw["spd_b_5"] = (nav_b / nav_b.shift(5) - 1).where(~pre_live)
    raw["spd_b_21"] = (nav_b / nav_b.shift(21) - 1).where(~pre_live)

    # (c) cross-sectional structure of the traded book
    c21, c63, d21 = _held_book_stats(W, R)
    raw["corr_held_21"] = c21.where(~pre_live)
    raw["corr_held_63"] = c63.where(~pre_live)
    raw["disp_held_21"] = d21.where(~pre_live)
    dd63 = (S / S.rolling(63, min_periods=63).max() - 1).where(M)  # universe = PIT-eligible names only
    cut = dd63.quantile(0.10, axis=1)
    worst = dd63.le(cut, axis=0).astype(float).where(M)
    raw["worst_dec_share"] = (W * worst.reindex(columns=W.columns).fillna(0.0)).sum(axis=1).where(~pre_live)
    raw["beta_u_63"] = r_u.rolling(63, min_periods=63).cov(r_s) / r_s.rolling(63, min_periods=63).var()

    # (d) breadth on the point-in-time universe (M)
    ma50 = S.rolling(50, min_periods=50).mean()
    ma200 = S.rolling(200, min_periods=200).mean()
    valid50 = (ma50.notna() & M)
    valid200 = (ma200.notna() & M)
    raw["pct_gt50"] = ((S > ma50) & valid50).sum(axis=1) / valid50.sum(axis=1).replace(0, np.nan)
    raw["pct_gt200"] = ((S > ma200) & valid200).sum(axis=1) / valid200.sum(axis=1).replace(0, np.nan)
    hi52 = ((S >= S.rolling(252, min_periods=252).max()) & M).sum(axis=1)
    lo52 = ((S <= S.rolling(252, min_periods=252).min()) & M).sum(axis=1)
    n_u = (S.notna() & M).sum(axis=1).replace(0, np.nan)
    raw["netnewhl"] = (hi52 - lo52) / n_u
    ew63 = R.where(M).mean(axis=1).rolling(63, min_periods=63).sum()
    raw["ew_vs_spy_63"] = ew63 - spy.pct_change(63, fill_method=None)

    # (e) cross-asset stress
    raw["tlt_mom_63"] = tlt / tlt.shift(63) - 1
    raw["gld_mom_63"] = gld / gld.shift(63) - 1
    raw["uup_mom_63"] = uup / uup.shift(63) - 1
    rt = np.log(tlt).diff()
    raw["tlt_vol_21"] = rt.rolling(21, min_periods=21).std() * ANN
    raw["corr_sb_21"] = r_s.rolling(21, min_periods=21).corr(rt)
    raw["corr_sb_63"] = r_s.rolling(63, min_periods=63).corr(rt)

    # (f) calendar (known in advance)
    raw["month_end"] = pd.Series(idx.is_month_end.astype(float), index=idx)
    raw["quarter_end"] = pd.Series(idx.is_quarter_end.astype(float), index=idx)

    # (g) baseline-book state
    raw["base_vol_21"] = (r_b.rolling(21, min_periods=21).std() * ANN)
    raw["base_vol_63"] = (r_b.rolling(63, min_periods=63).std() * ANN)
    raw["base_gross"] = history["base_gross"].reindex(idx).ffill().where(~pre_live)
    raw["base_beta_63"] = r_b.rolling(63, min_periods=63).cov(r_s) / r_s.rolling(63, min_periods=63).var()
    raw["stress_b5"] = history["stress"].reindex(idx).ffill()

    raw_df = pd.DataFrame({k: raw[k] for k in FEATURE_NAMES}, index=idx)
    out = pd.DataFrame(index=idx)
    for k in FEATURE_NAMES:
        out[k] = _expz(raw_df[k].astype(float), FEATURES[k][1])
    out.attrs["raw"] = raw_df
    out.attrs["regime_hard"] = km_hard
    out.attrs["live_start"] = live_start
    return out


def features_at(date, history: dict) -> pd.Series:
    """One causal observation vector at `date`. `history` must start at ORIGIN (never an episode start)
    and may extend beyond `date`; only rows <= date are used."""
    d = pd.Timestamp(date)
    first = history["spy"].index.min()
    if first > ORIGIN:
        raise ValueError(f"history must start at ORIGIN {ORIGIN.date()}, got {first.date()} (NAV-reset guard)")
    h = {k: (v.loc[:d] if hasattr(v, "loc") else v) for k, v in history.items()}
    panel = build_panel(h)
    return panel.loc[d].reindex(FEATURE_NAMES)
