"""Per-feature documentation for the v4.1 set (certification item S4): definition, exact inputs, timing lag,
warm-up, first valid date, group, rationale and literature reference. Used by scripts/features_v4_materialize.py.

Lag convention (M2): every feature at decision date t uses closes up to and including t. VIX is the t close
(same day). The env fills at the close of t and earns returns from t+1 (PortfolioEnvV2._compute_daily_returns).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.rl import features_risk_v4 as L

# name -> (definition, exact inputs, rationale, literature reference or "")
DOC = {
    "rv_u_5": ("unit-book realised vol, 5 daily returns, x sqrt(252), log-z", "unit_ret",
               "short-horizon risk of the traded book", "Andersen et al. 2001 (realised vol)"),
    "rv_u_21": ("unit-book realised vol, 21 days, annualised, log-z (cluster representative: har_u_fc, garch_u_fc, base_vol_21)",
                "unit_ret", "cleanest causal monthly risk estimate; no fitted or hand-set parameters",
                "Andersen et al. 2001"),
    "rv_u_63": ("unit-book realised vol, 63 days, log-z (cluster representative: base_vol_63)", "unit_ret",
                "quarterly risk level; the book-level analogue of the SPY 63d vol", "Andersen et al. 2001"),
    "rv_s_5": ("SPY realised vol, 5 days, log-z", "spy", "market-level short-horizon risk", "Andersen et al. 2001"),
    "rv_s_21": ("SPY realised vol, 21 days, log-z (cluster representative: park_s_21)", "spy",
                "market-level monthly risk; close-to-close, no intraday data", "Andersen et al. 2001"),
    "rv_s_63": ("SPY realised vol, 63 days, log-z", "spy", "market-level quarterly risk", "Andersen et al. 2001"),
    "vr_u_5_63": ("unit-book vol ratio rv5/rv63 (raw, z)", "unit_ret", "vol-term-structure slope; spikes flag shocks",
                  "Andersen et al. 2001"),
    "vr_s_5_63": ("SPY vol ratio rv5/rv63 (raw, z)", "spy", "market vol-term-structure slope", "Andersen et al. 2001"),
    "vov_u_63": ("std over 63d of 21d unit-book vol, log-z", "unit_ret", "vol-of-vol; instability of risk",
                 "Corsi 2009 (HAR family; vol persistence)"),
    "semidn_u_21": ("unit-book downside semideviation, 21d, annualised, log-z", "unit_ret",
                    "asymmetric risk: only down-moves", "Ang, Chen & Xing 2006 (downside risk)"),
    "downup_u_63": ("unit-book downside / upside semivariance ratio, 63d, log-z", "unit_ret",
                    "skew of recent returns", "Ang, Chen & Xing 2006"),
    "downup_s_63": ("SPY downside / upside semivariance ratio, 63d, log-z", "spy", "market skew of recent returns",
                    "Ang, Chen & Xing 2006"),
    "vix_level": ("VIX close / 100, log-z", "vix (close of t)", "option-implied market risk, forward-looking",
                  "Whaley 2000 (VIX)"),
    "vix_chg_5": ("VIX(t) - VIX(t-5), raw z", "vix", "change in implied risk", "Whaley 2000"),
    "vrp_vs_rv21": ("VIX(t) - rv_s_21 (unscaled, raw z)", "vix, spy", "variance-risk-premium proxy",
                    "Bollerslev, Tauchen & Zhou 2009"),
    "har_s_fc": ("HAR-RV next-21d SPY vol forecast, expanding OLS fit with rows whose target is known, log-z",
                 "spy", "forecast of SPY vol from daily/weekly/monthly variance (SPY counterpart kept; the unit-book HAR is a cluster member)",
                 "Corsi 2009"),
    "vrp_har_s": ("VIX(t) - har_s_fc(t) (raw z)", "vix, spy", "implied minus model-based vol",
                  "Bollerslev, Tauchen & Zhou 2009"),
    "ewdn_u_21": ("EWMA downside deviation of unit book, half-life 21d, annualised, log-z", "unit_ret",
                  "recent downside pressure", "Ang, Chen & Xing 2006"),
    "ewdn_u_126": ("EWMA downside deviation of unit book, half-life 126d, log-z", "unit_ret",
                   "slower downside regime", "Ang, Chen & Xing 2006"),
    "regime_km_bear": ("logit P(bear) = 4*(d_bull - d_bear) from 2-means on log SPY EWMA downside dev (21d, 126d); "
                       "refit yearly on rows strictly before the year; raw z", "spy",
                       "unsaturated regime score (P itself saturates at 1.0 in 2008)",
                       "Hamilton 1989; Ang & Bekaert 2002 (regime switching)"),
    "regime_simple_bear": ("1 if SPY EWMA downside dev 21d > its expanding 75th percentile", "spy",
                           "non-parametric regime baseline", "Ang & Bekaert 2002"),
    "dd_s": ("SPY drawdown from running peak, raw z", "spy", "market drawdown state", "Magdon-Ismail et al. 2004"),
    "dsp_s": ("log(1 + trading days since SPY peak), raw z", "spy", "drawdown duration", "Magdon-Ismail et al. 2004"),
    "rec_s": ("SPY recovery fraction from current trough, raw z", "spy", "drawdown recovery state",
              "Magdon-Ismail et al. 2004"),
    "spd_s_5": ("SPY 5-day return, raw z", "spy", "short market momentum", ""),
    "spd_s_21": ("SPY 21-day return, raw z", "spy", "monthly market momentum", ""),
    "dd_b": ("baseline B.5+B.4 NAV drawdown from its peak; NaN before the book inception (2008-01-07), raw z",
             "unit_w, base_ret", "drawdown of the book the agent actually holds (pre-inception masked)",
             "Magdon-Ismail et al. 2004"),
    "dsp_b": ("log(1 + days since baseline peak); NaN pre-inception, raw z", "base_ret",
              "baseline drawdown duration", "Magdon-Ismail et al. 2004"),
    "rec_b": ("baseline recovery fraction from trough; NaN pre-inception, raw z", "base_ret",
              "baseline recovery state", "Magdon-Ismail et al. 2004"),
    "spd_b_5": ("baseline 5-day return; NaN pre-inception, raw z", "base_ret", "baseline short momentum", ""),
    "spd_b_21": ("baseline 21-day return; NaN pre-inception, raw z", "base_ret", "baseline monthly momentum", ""),
    "corr_held_21": ("average pairwise correlation of names held (EW identity), 21d, from the held set at t; "
                     "NaN pre-inception, raw z", "unit_w, stocks", "co-movement of the traded names",
                     "Pollet & Wilson 2010 (average correlation)"),
    "corr_held_63": ("average pairwise correlation of held names, 63d, raw z", "unit_w, stocks",
                     "longer co-movement window", "Pollet & Wilson 2010"),
    "disp_held_21": ("cross-sectional std of held-name returns, 21d mean, log-z", "unit_w, stocks",
                     "dispersion of the held names", "Pollet & Wilson 2010"),
    "worst_dec_share": ("unit-book weight in names whose 63d drawdown is in the worst PIT-universe decile, raw z",
                        "unit_w, stocks, universe_mask", "concentration in names already in deep drawdown",
                        "Ang, Chen & Xing 2006"),
    "beta_u_63": ("unit-book rolling 63d beta to SPY, raw z", "unit_ret, spy", "market sensitivity of the book",
                  "Frazzini & Pedersen 2014 (beta)"),
    "pct_gt50": ("share of PIT-eligible universe above 50d MA, raw z", "stocks, universe_mask",
                 "breadth; SURVIVOR-BIASED before 2015 (delisted names absent)", "Zweig 1973 (breadth)"),
    "pct_gt200": ("share of PIT-eligible universe above 200d MA, raw z", "stocks, universe_mask",
                  "long breadth; SURVIVOR-BIASED before 2015", "Zweig 1973"),
    "netnewhl": ("(52w highs - 52w lows) / PIT-eligible count, raw z", "stocks, universe_mask",
                 "new-high/new-low breadth; SURVIVOR-BIASED before 2015", ""),
    "ew_vs_spy_63": ("equal-weight PIT universe 63d return minus SPY 63d return, raw z",
                     "stocks, universe_mask, spy", "breadth vs cap weighting; SURVIVOR-BIASED before 2015", ""),
    "tlt_mom_63": ("TLT 63-day return, raw z", "tlt", "rates momentum (flight to quality)", ""),
    "gld_mom_63": ("GLD 63-day return, raw z", "gld", "gold momentum", ""),
    "uup_mom_63": ("UUP 63-day return, raw z", "uup", "dollar momentum", ""),
    "tlt_vol_21": ("TLT realised vol 21d, log-z", "tlt", "rates volatility", ""),
    "corr_sb_21": ("SPY-TLT daily return correlation, 21d, raw z", "spy, tlt",
                   "stock-bond correlation regime (diversification)", "Campbell et al. 2014 (stock-bond correlation)"),
    "corr_sb_63": ("SPY-TLT daily return correlation, 63d, raw z", "spy, tlt", "longer stock-bond correlation",
                   "Campbell et al. 2014"),
    "base_gross": ("baseline gross exposure in force (B.4 output), raw z; NaN pre-inception", "base_gross",
                   "current leverage of the baseline book", ""),
    "base_beta_63": ("baseline rolling 63d beta to SPY, raw z", "base_ret, spy", "baseline market beta",
                     "Frazzini & Pedersen 2014"),
    "stress_b5": ("B.5 stress score in force, raw z", "stress (B.5 pipeline output)", "pipeline stress state",
                  ""),
}

GROUP_RATIONALE = {"a_vol": "volatility dynamics", "a_regime": "downside regime", "b_dd": "drawdown state",
                   "c_xs": "cross-sectional structure of the traded book", "d_breadth": "market breadth (PIT universe)",
                   "e_xasset": "cross-asset stress", "g_base": "baseline-book state"}


def _lag_for(name: str) -> str:
    if name in ("vix_level", "vix_chg_5", "vrp_vs_rv21", "vrp_har_s"):
        return "0 (VIX close of t, same day as the decision; fill at the close of t)"
    return "0 (close of t)"


def feature_meta_table(P: pd.DataFrame, absent) -> pd.DataFrame:
    rows = []
    for k in L.FEATURE_NAMES:
        g, tr = L.FEATURES[k]
        s = P[k]
        fv = s.first_valid_index()
        d_def, inp, why, ref = DOC[k]
        rows.append(dict(
            name=k, group=g, group_rationale=GROUP_RATIONALE[g], transform=("z(log)" if tr == "log" else "z(raw)"),
            definition=d_def, inputs=inp, lag=_lag_for(k),
            warmup=f"expanding z, min {L.Z_MIN} valid obs; book inputs start 2008-01-07",
            first_valid_date=str(fv.date()) if fv is not None else "",
            n_valid_2008_2026Apr=int(s.notna().sum()),
            gfc_coverage_by_2008_07_31=bool(fv is not None and fv <= pd.Timestamp("2008-07-31")),
            survivor_biased_pre2015=k in L.SURVIVOR_BIASED_PRE2015,
            rationale=why, literature_reference=ref, version="v4.1"))
    for k, why in L.REMOVED_V41.items():
        rows.append(dict(name=k, group="REMOVED", group_rationale="", transform="", definition="removed in v4.1",
                         inputs="", lag="", warmup="", first_valid_date="", n_valid_2008_2026Apr=np.nan,
                         gfc_coverage_by_2008_07_31=np.nan, survivor_biased_pre2015=np.nan,
                         rationale=why, literature_reference="", version="v4.1 (removed)"))
    return pd.DataFrame(rows)
