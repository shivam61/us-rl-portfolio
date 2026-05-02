"""Phase D.1 — 28-dimensional state vector builder.

obs = [
    vix_252d_pct,          # 0   VIX rolling 252d rank [0,1]
    spy_252d_drawdown,     # 1   SPY drawdown from 252d rolling max [−1,0]
    yield_curve_proxy,     # 2   z-scored TLT−SPY 63d momentum
    stress_score,          # 3   weighted_50_50 stress from build_stress_series
    sector_vol_score[0:11],# 4–14 median vol_score rank per GICS sector
    sector_weight[0:11],   # 15–25 B.5 stock-sleeve weight summed per sector (normalised)
    portfolio_drawdown,    # 26  current NAV drawdown from peak [−1,0]
    weeks_since_rebalance, # 27  (date − last_rebalance_date).days / 7
]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from run_phase_a7_trend_overlay import latest_scores  # noqa: E402

# Canonical 11-sector ordering (matches config/universes/sp500.yaml sector_etfs)
SECTOR_ORDER = ["XLK", "XLF", "XLV", "XLY", "XLP", "XLE", "XLI", "XLU", "XLB", "XLRE", "XLC"]

# Assets that belong to the trend sleeve — excluded from sector weight computation
TREND_ASSETS = {"TLT", "GLD", "UUP", "SPY"}


def _latest_value(series: pd.Series, date: pd.Timestamp) -> float:
    """Return the most recent value in series at or before date."""
    available = series[series.index <= date]
    if available.empty:
        return 0.0
    return float(available.iloc[-1])


def build_state(
    inputs: dict,
    b5_weights: pd.DataFrame,
    nav_series: pd.Series,
    date: pd.Timestamp,
    stress_series: pd.Series,
    last_rebalance_date: pd.Timestamp | None = None,
) -> np.ndarray:
    """Build 28-dim observation vector at a given rebalance date.

    Args:
        inputs: Standard inputs dict (prices, vol_scores, universe_config, …).
        b5_weights: B.5 constrained weights DataFrame (dates × tickers).
        nav_series: Portfolio NAV series up to (and including) date.
        date: Current rebalance date.
        stress_series: stress_score series from build_stress_series.
        last_rebalance_date: Previous rebalance date (for weeks_since_rebalance).

    Returns:
        np.ndarray shape (28,), dtype float32.
    """
    prices: pd.DataFrame = inputs["prices"]
    vol_scores: pd.DataFrame = inputs["vol_scores"]
    universe_config = inputs["universe_config"]
    ticker_to_sector: dict[str, str] = dict(universe_config.tickers)

    obs = np.zeros(28, dtype=np.float32)

    # --- Macro features (indices 0–2) ---
    prices_to_date = prices[prices.index <= date]

    # 0: VIX 252d rolling rank
    vix_col = universe_config.vix_proxy  # typically "^VIX"
    if vix_col in prices.columns:
        vix_series = prices_to_date[vix_col].dropna()
        if len(vix_series) >= 252:
            vix_rank = vix_series.rolling(252).rank(pct=True)
            obs[0] = float(np.clip(vix_rank.iloc[-1], 0.0, 1.0))

    # 1: SPY 252d drawdown from rolling max
    spy_col = universe_config.benchmark  # "SPY"
    if spy_col in prices.columns:
        spy_series = prices_to_date[spy_col].dropna()
        if len(spy_series) >= 252:
            rolling_max = spy_series.rolling(252).max()
            drawdown = (spy_series - rolling_max) / rolling_max.clip(lower=1e-12)
            obs[1] = float(np.clip(drawdown.iloc[-1], -1.0, 0.0))

    # 2: Yield-curve proxy — z-score of (TLT_63d_ret - SPY_63d_ret), rolling 252d window
    if "TLT" in prices.columns and spy_col in prices.columns:
        tlt_ret = prices_to_date["TLT"].pct_change(63).dropna()
        spy_ret_63 = prices_to_date[spy_col].pct_change(63).dropna()
        common_idx = tlt_ret.index.intersection(spy_ret_63.index)
        if len(common_idx) >= 252:
            spread = (tlt_ret.reindex(common_idx) - spy_ret_63.reindex(common_idx))
            rolling_mean = spread.rolling(252).mean()
            rolling_std = spread.rolling(252).std(ddof=1)
            last_mean = float(rolling_mean.iloc[-1])
            last_std = float(rolling_std.iloc[-1])
            if last_std > 1e-12:
                obs[2] = float(np.clip((float(spread.iloc[-1]) - last_mean) / last_std, -3.0, 3.0))

    # --- Stress score (index 3) ---
    obs[3] = float(np.clip(_latest_value(stress_series, date), 0.0, 1.0))

    # --- Sector vol_score signals (indices 4–14) ---
    # vol_scores is a MultiIndex (date, ticker) DataFrame — use latest_scores to get snapshot
    vol_snap = latest_scores(vol_scores, date, "volatility_score")  # Series: ticker → score
    if not vol_snap.empty:
        for i, sector_etf in enumerate(SECTOR_ORDER):
            sector_tickers = [
                t for t, s in ticker_to_sector.items()
                if s == sector_etf and t in vol_snap.index
            ]
            if sector_tickers:
                sector_scores = vol_snap.reindex(sector_tickers).dropna()
                if not sector_scores.empty:
                    obs[4 + i] = float(np.clip(sector_scores.median(), 0.0, 1.0))

    # --- Sector weights from B.5 (indices 15–25) ---
    available_weights = b5_weights[b5_weights.index <= date]
    if not available_weights.empty:
        w_snap = available_weights.iloc[-1].dropna()
        # Stock sleeve only (exclude trend assets)
        stock_weights = w_snap[
            [t for t in w_snap.index if t not in TREND_ASSETS and abs(float(w_snap[t])) > 1e-12]
        ]
        stock_total = float(stock_weights.abs().sum())

        sector_weights = np.zeros(11, dtype=np.float32)
        for i, sector_etf in enumerate(SECTOR_ORDER):
            sector_tickers = [
                t for t in stock_weights.index if ticker_to_sector.get(t) == sector_etf
            ]
            sector_weights[i] = float(stock_weights.reindex(sector_tickers).fillna(0.0).sum())

        if stock_total > 1e-12:
            sector_weights = sector_weights / stock_total

        obs[15:26] = sector_weights.astype(np.float32)

    # --- Portfolio state (indices 26–27) ---
    # 26: current drawdown from NAV peak
    if nav_series is not None and len(nav_series) > 0:
        nav_to_date = nav_series[nav_series.index <= date]
        if len(nav_to_date) > 0:
            peak = float(nav_to_date.cummax().iloc[-1])
            nav_now = float(nav_to_date.iloc[-1])
            if peak > 1e-12:
                dd = (nav_now - peak) / peak
                obs[26] = float(np.clip(dd, -1.0, 0.0))

    # 27: weeks since last rebalance
    if last_rebalance_date is not None:
        delta_days = (date - last_rebalance_date).days
        obs[27] = float(max(0.0, delta_days / 7.0))

    return obs
