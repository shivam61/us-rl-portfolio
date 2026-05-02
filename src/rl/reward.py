"""Phase D.4 — RL reward function.

reward_t = rolling_sharpe_21d(returns[-21:])
         - lambda_tilt * sum(abs(sector_tilts))
         - lambda_dd * max(0.0, -portfolio_drawdown_from_peak)
"""
import numpy as np
import pandas as pd


def _annualised_sharpe(returns: pd.Series) -> float:
    if len(returns) < 2:
        return 0.0
    mu = float(returns.mean())
    sigma = float(returns.std(ddof=1))
    if sigma < 1e-12:
        return 0.0
    return float(mu / sigma * np.sqrt(252))


def compute_reward(
    daily_returns: pd.Series,
    sector_tilts: np.ndarray,
    portfolio_nav: pd.Series,
    lambda_tilt: float = 0.01,
    lambda_dd: float = 0.05,
) -> float:
    """Three-term reward: rolling Sharpe minus tilt penalty minus drawdown penalty.

    Args:
        daily_returns: Portfolio daily net returns since last rebalance.
        sector_tilts: Applied sector tilts, shape (11,).
        portfolio_nav: Full NAV history (for cumulative drawdown from peak).
        lambda_tilt: Penalty weight on total absolute tilt.
        lambda_dd: Penalty weight on current drawdown below NAV peak.

    Returns:
        Scalar reward (float).
    """
    if portfolio_nav is not None and (
        len(portfolio_nav) > 0 and float(portfolio_nav.iloc[-1]) <= 0.0
    ):
        return -1.0

    n = len(daily_returns)
    if n < 5:
        return 0.0

    window = daily_returns.iloc[-21:] if n >= 21 else daily_returns
    rolling_sharpe = _annualised_sharpe(window)

    tilt_penalty = lambda_tilt * float(np.sum(np.abs(sector_tilts)))

    dd_penalty = 0.0
    if portfolio_nav is not None and len(portfolio_nav) > 0:
        peak = float(portfolio_nav.cummax().iloc[-1])
        nav_now = float(portfolio_nav.iloc[-1])
        if peak > 1e-12:
            drawdown = (nav_now - peak) / peak
            dd_penalty = lambda_dd * max(0.0, -drawdown)

    return rolling_sharpe - tilt_penalty - dd_penalty
