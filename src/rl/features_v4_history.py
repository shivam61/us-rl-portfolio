"""Canonical history adapter for the v4 risk feature library (v4.1, experiment FH).

Turns B.5 stock weights and price data into the causal history dict consumed by
``features_risk_v4.build_panel``. No hard-coded paths, no other worktree, no H1 cache.

Unit book (canonical, daily): the equity-only book of the env routine,
    w_t = B.5 weights in force at close t, non-tradable names dropped (finalize_equity_only),
    gross-normalised to 1. B.5 weights change only on the B.5 control dates (the 8w grid), so
    w_t is piecewise constant between them.
Unit return (canonical): unit_ret_t = sum_i w_i(t-1) * r_i(t), r_i(t) = close_t/close_{t-1} - 1.
    Weights set at close t-1 earn the return of day t, the same timing as
    PortfolioEnvV2._compute_daily_returns (fill at the close of the decision date).
    NaN, never zero-filled, when a held name has no return on day t.

This reproduces H1's 8w cache exactly (max deviation 3.6e-16) and the env routine on the
8w control dates. The 14d H1 cache is NOT the same series: it re-sets the weights on the
14d grid, so its book is grid-dependent (see docs/phases/rl_feature_certification.md).
"""
from __future__ import annotations

import pandas as pd

from src.rl.exposure_mix import NON_TRADABLE_ASSETS

NON_TRADABLE = tuple(NON_TRADABLE_ASSETS)
# ETFs and index proxies that sit in the price file but are not single-stock universe members
ETF_EXCLUDE = ("IWM", "QQQ", "^VIX")


def is_single_stock(col) -> bool:
    c = str(col)
    return c not in NON_TRADABLE and c not in ETF_EXCLUDE and not c.startswith("XL") and not c.startswith("^")


def unit_weights(b5_weights: pd.DataFrame, index: pd.DatetimeIndex, columns) -> pd.DataFrame:
    """Daily unit-book weights: B.5 weights in force (forward-filled from B.5 dates), non-tradables
    dropped, gross-normalised to 1 (0 where the book is empty). Row t uses B.5 rows dated <= t."""
    W = b5_weights.reindex(index, method="ffill")
    W = W.drop(columns=[c for c in NON_TRADABLE if c in W.columns]).fillna(0.0)
    W = W.reindex(columns=[c for c in columns if c not in NON_TRADABLE]).fillna(0.0)
    tot = W.abs().sum(axis=1).replace(0.0, float("nan"))
    return W.div(tot, axis=0).fillna(0.0)


def unit_ret_from_weights(unit_w: pd.DataFrame, stocks: pd.DataFrame) -> pd.Series:
    """unit_ret_t = sum_i unit_w_i(t-1) * r_i(t). NaN where a name held at t-1 has no return at t."""
    R = stocks.reindex(index=unit_w.index, columns=unit_w.columns).pct_change(fill_method=None)
    held = unit_w.shift(1).fillna(0.0)
    missing = ((held != 0.0) & R.isna()).any(axis=1)
    empty = held.abs().sum(axis=1) == 0.0  # no book before inception: undefined, not zero
    out = (held * R.fillna(0.0)).sum(axis=1)
    return out.where(~missing & ~empty)


def history_from_inputs(prices: pd.DataFrame, b5_weights: pd.DataFrame, stress: pd.Series,
                        vix: pd.Series, spy_high: pd.Series, spy_low: pd.Series,
                        universe_mask: pd.DataFrame) -> dict:
    """Assemble the causal history dict (see features_risk_v4 for the keys).

    universe_mask: point-in-time ADV eligibility (bool, dates x tickers). Required: there is no default,
    so a missing mask cannot silently mean 'everyone eligible'."""
    idx = prices.index
    px = prices
    stock_cols = [c for c in px.columns if is_single_stock(c)]
    stocks = px[stock_cols]
    unit_w = unit_weights(b5_weights, idx, stock_cols)
    unit_ret = unit_ret_from_weights(unit_w, stocks)
    # a stock with no mask column is treated as NOT eligible (conservative); the list is kept in the
    # history so the manifest can report it
    absent = [c for c in stock_cols if c not in universe_mask.columns]
    mask = universe_mask.reindex(index=idx, columns=stock_cols).fillna(False).astype(bool)
    # baseline (B.5 + B.4 constrained) book: signed weights in force, not normalised
    base_w = b5_weights.reindex(idx, method="ffill").reindex(columns=stock_cols).fillna(0.0)
    base_ret = (base_w.shift(1).fillna(0.0) * stocks.pct_change(fill_method=None).fillna(0.0)).sum(axis=1)
    base_ret = base_ret.where(base_w.shift(1).abs().sum(axis=1) > 0)
    return {
        "spy": px["SPY"], "iwm": px["IWM"], "tlt": px["TLT"], "gld": px["GLD"], "uup": px["UUP"],
        "vix": vix.reindex(idx), "spy_high": spy_high.reindex(idx), "spy_low": spy_low.reindex(idx),
        "stocks": stocks, "universe_mask": mask, "universe_mask_absent": absent,
        "unit_w": unit_w, "unit_ret": unit_ret, "base_ret": base_ret,
        "base_gross": base_w.abs().sum(axis=1), "stress": stress.reindex(idx),
    }
