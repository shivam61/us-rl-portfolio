"""Phase E.1 — 42-dimensional state vector builder for RL Regime Controller v2.

obs layout:
  [0]     vix_percentile_1y          VIX rolling 252d rank [0,1]
  [1]     spy_drawdown_from_peak      SPY expanding-max drawdown [−1,0]
  [2]     spy_ret_3m                  SPY 63d return
  [3]     spy_ret_6m                  SPY 126d return
  [4]     realized_market_vol_63d     SPY 63d realised vol (annualised)
  [5]     iwm_spy_spread_63d          IWM 63d ret − SPY 63d ret (size factor)
  [6]     qqq_spy_spread_63d          QQQ 63d ret − SPY 63d ret (growth/tech)
  [7]     tlt_ret_3m                  TLT 63d return
  [8]     tlt_ret_6m                  TLT 126d return
  [9]     gld_ret_3m                  GLD 63d return
  [10]    gld_ret_6m                  GLD 126d return
  [11]    uup_ret_3m                  UUP 63d return (0 if <63d history)
  [12]    uup_ret_6m                  UUP 126d return (0 if <126d history)
  [13]    stress_score                B.5 stress score [0,1]
  [14-24] sector_mom_vs_spy[11]       sector ETF 3m ret − SPY 3m ret (XLK…XLC)
  [25-35] sector_vol_63d[11]          sector ETF 63d vol, daily scale (XLK…XLC)
  [36]    current_equity_frac         equity sleeve fraction [0,1]
  [37]    current_trend_frac          trend sleeve fraction [0,1]
  [38]    current_cash_frac           cash fraction [0,1]
  [39]    portfolio_drawdown          portfolio expanding-max drawdown [−1,0]
  [40]    portfolio_vol_63d           portfolio 63d realised vol (annualised)
  [41]    portfolio_ret_21d_zscore    21d return z-scored over 252d, clipped [−3,3]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Canonical sector ordering — matches SECTOR_ORDER in state_builder.py
SECTOR_ORDER_V2 = [
    "XLK", "XLF", "XLV", "XLY", "XLP",
    "XLE", "XLI", "XLU", "XLB", "XLRE", "XLC",
]

OBS_DIM = 42

_DEFAULT_SECTOR_FEATURES_PATH = _REPO_ROOT / "data" / "features" / "sector_features.parquet"


def _latest_px(prices_to_date: pd.DataFrame, col: str) -> pd.Series | None:
    """Return the price series for col up to the current date, or None if absent."""
    if col not in prices_to_date.columns:
        return None
    s = prices_to_date[col].dropna()
    return s if not s.empty else None


def _pct_change_at(prices_to_date: pd.DataFrame, col: str, window: int) -> float:
    """Return the most recent `window`-day pct_change for col, or 0.0 if unavailable."""
    s = _latest_px(prices_to_date, col)
    if s is None or len(s) < window + 1:
        return 0.0
    return float(s.pct_change(window).iloc[-1]) if not np.isnan(s.pct_change(window).iloc[-1]) else 0.0


def _sector_latest(sector_features_df: pd.DataFrame, sec: str, col: str, date: pd.Timestamp) -> float:
    """Return the most recent value of col for sector ETF sec at or before date."""
    try:
        sec_df = sector_features_df.xs(sec, level="ticker")[col]
    except KeyError:
        return 0.0
    available = sec_df[sec_df.index <= date].dropna()
    if available.empty:
        return 0.0
    return float(available.iloc[-1])


def build_state_v2(
    inputs: dict,
    b5_weights: pd.DataFrame,
    nav_series: pd.Series,
    date: pd.Timestamp,
    stress_series: pd.Series,
    last_rebalance_date: pd.Timestamp | None = None,
    current_equity_frac: float = 1.0,
    current_trend_frac: float = 0.0,
    current_cash_frac: float = 0.0,
    sector_features_df: pd.DataFrame | None = None,
) -> np.ndarray:
    """Build 42-dim Phase E observation vector at a given rebalance date.

    Args:
        inputs: Standard inputs dict (prices, vol_scores, universe_config, …).
        b5_weights: B.5 constrained weights DataFrame (dates × tickers); used only
                    to infer initial trend sleeve fraction on first step.
        nav_series: Portfolio NAV series up to (and including) date.
        date: Current rebalance date.
        stress_series: B.5 stress_score series from build_stress_series.
        last_rebalance_date: Unused in Phase E (kept for API symmetry with build_state).
        current_equity_frac: Equity sleeve fraction from most recent RL action [0,1].
        current_trend_frac: Trend sleeve fraction from most recent RL action [0,1].
        current_cash_frac: Cash fraction from most recent RL action [0,1].
        sector_features_df: MultiIndex(date, ticker) parquet; loaded lazily if None.

    Returns:
        np.ndarray shape (42,), dtype float32. No NaN values.
    """
    if sector_features_df is None:
        sector_features_df = pd.read_parquet(_DEFAULT_SECTOR_FEATURES_PATH)

    prices: pd.DataFrame = inputs["prices"]
    universe_config = inputs["universe_config"]
    spy_col: str = universe_config.benchmark          # "SPY"
    vix_col: str = universe_config.vix_proxy          # "^VIX"

    obs = np.zeros(OBS_DIM, dtype=np.float32)
    prices_to_date = prices[prices.index <= date]

    # ------------------------------------------------------------------ #
    # Market features (0–4)                                               #
    # ------------------------------------------------------------------ #

    # [0] VIX 252d rolling rank
    if vix_col in prices.columns:
        vix_s = prices_to_date[vix_col].dropna()
        if len(vix_s) >= 252:
            rank = vix_s.rolling(252).rank(pct=True).iloc[-1]
            obs[0] = float(np.clip(rank, 0.0, 1.0))

    # [1] SPY expanding-max drawdown
    spy_s = _latest_px(prices_to_date, spy_col)
    if spy_s is not None and len(spy_s) >= 2:
        peak = spy_s.expanding().max()
        dd = (spy_s - peak) / peak.clip(lower=1e-12)
        obs[1] = float(np.clip(dd.iloc[-1], -1.0, 0.0))

    # [2] SPY 3m return
    obs[2] = float(np.clip(_pct_change_at(prices_to_date, spy_col, 63), -1.0, 2.0))

    # [3] SPY 6m return
    obs[3] = float(np.clip(_pct_change_at(prices_to_date, spy_col, 126), -1.0, 2.0))

    # [4] SPY realised vol 63d (annualised)
    if spy_s is not None and len(spy_s) >= 64:
        daily_ret = spy_s.pct_change().iloc[-63:]
        obs[4] = float(np.clip(daily_ret.std(ddof=1) * np.sqrt(252), 0.0, 2.0))

    # ------------------------------------------------------------------ #
    # Size / style regime (5–6)                                           #
    # ------------------------------------------------------------------ #

    spy_ret_63 = _pct_change_at(prices_to_date, spy_col, 63)
    obs[5] = float(np.clip(_pct_change_at(prices_to_date, "IWM", 63) - spy_ret_63, -0.5, 0.5))
    obs[6] = float(np.clip(_pct_change_at(prices_to_date, "QQQ", 63) - spy_ret_63, -0.5, 0.5))

    # ------------------------------------------------------------------ #
    # Trend asset signals (7–12)                                          #
    # ------------------------------------------------------------------ #

    obs[7]  = float(np.clip(_pct_change_at(prices_to_date, "TLT", 63),  -0.5, 0.5))
    obs[8]  = float(np.clip(_pct_change_at(prices_to_date, "TLT", 126), -0.5, 0.5))
    obs[9]  = float(np.clip(_pct_change_at(prices_to_date, "GLD", 63),  -0.5, 0.5))
    obs[10] = float(np.clip(_pct_change_at(prices_to_date, "GLD", 126), -0.5, 0.5))
    obs[11] = float(np.clip(_pct_change_at(prices_to_date, "UUP", 63),  -0.5, 0.5))
    obs[12] = float(np.clip(_pct_change_at(prices_to_date, "UUP", 126), -0.5, 0.5))

    # ------------------------------------------------------------------ #
    # Stress score (13)                                                   #
    # ------------------------------------------------------------------ #

    stress_avail = stress_series[stress_series.index <= date]
    if not stress_avail.empty:
        obs[13] = float(np.clip(float(stress_avail.iloc[-1]), 0.0, 1.0))

    # ------------------------------------------------------------------ #
    # Sector momentum vs SPY (14–24) and sector volatility (25–35)       #
    # ------------------------------------------------------------------ #

    spy_ret_3m = _pct_change_at(prices_to_date, spy_col, 63)
    for i, sec in enumerate(SECTOR_ORDER_V2):
        sec_ret_3m = _sector_latest(sector_features_df, sec, "sector_ret_3m", date)
        obs[14 + i] = float(np.clip(sec_ret_3m - spy_ret_3m, -0.5, 0.5))
        obs[25 + i] = float(np.clip(
            _sector_latest(sector_features_df, sec, "sector_volatility_63d", date),
            0.0, 0.10,
        ))

    # ------------------------------------------------------------------ #
    # Portfolio exposure state (36–38)                                    #
    # ------------------------------------------------------------------ #

    obs[36] = float(np.clip(current_equity_frac, 0.0, 1.0))
    obs[37] = float(np.clip(current_trend_frac,  0.0, 1.0))
    obs[38] = float(np.clip(current_cash_frac,   0.0, 1.0))

    # ------------------------------------------------------------------ #
    # Portfolio risk state (39–41)                                        #
    # ------------------------------------------------------------------ #

    if nav_series is not None and len(nav_series) > 0:
        nav = nav_series[nav_series.index <= date] if hasattr(nav_series.index, 'date') else nav_series

        # [39] portfolio drawdown from expanding peak
        if len(nav) > 0:
            peak_nav = float(nav.expanding().max().iloc[-1])
            nav_now  = float(nav.iloc[-1])
            if peak_nav > 1e-12:
                obs[39] = float(np.clip((nav_now - peak_nav) / peak_nav, -1.0, 0.0))

        # [40] portfolio 63d realised vol (annualised)
        if len(nav) >= 64:
            port_rets = nav.pct_change().iloc[-63:]
            obs[40] = float(np.clip(port_rets.std(ddof=1) * np.sqrt(252), 0.0, 2.0))

        # [41] 21d return z-scored over rolling 252d window, clipped [−3, 3]
        if len(nav) >= 22:
            port_rets_all = nav.pct_change().dropna()
            ret_21d = float((1.0 + port_rets_all.iloc[-21:]).prod() - 1.0)
            if len(port_rets_all) >= 252:
                rolling_21d = port_rets_all.rolling(21).apply(
                    lambda x: float((1.0 + x).prod() - 1.0), raw=False
                ).dropna()
                mu_r = float(rolling_21d.rolling(252).mean().iloc[-1])
                sd_r = float(rolling_21d.rolling(252).std(ddof=1).iloc[-1])
                if sd_r > 1e-12:
                    obs[41] = float(np.clip((ret_21d - mu_r) / sd_r, -3.0, 3.0))

    # Final NaN guard
    obs = np.where(np.isfinite(obs), obs, 0.0).astype(np.float32)
    return obs
