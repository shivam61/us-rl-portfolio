"""Phase E.4 — RL reward function for Regime Controller v2.

reward_t = sharpe_63d(daily_returns)
         + 0.10 × recovery_bonus(portfolio_nav)
         − lambda_dd    × max(0.0, −drawdown_from_peak)
         − lambda_cash  × cash_frac × bull_regime_indicator
         − lambda_churn × |equity_frac − prev_equity_frac|

Sign conventions (consistent with Phase D reward.py):
  - drawdown_from_peak = (nav_now − peak) / peak  ≤ 0 (negative when underwater)
  - dd_penalty = lambda_dd × max(0.0, −drawdown_from_peak)  → positive penalty
  - cash_drag fires when spy_trend_positive=True (stress gate removed in E.7)

E.7 calibration changes (vs original E.4 defaults):
  - lambda_dd:   0.15 → 0.08  (was dominant over Sharpe term; halved)
  - lambda_cash: 0.03 → 0.05  (strengthened to match order-of-magnitude of reduced λ_dd)
  - bull_regime: spy_trend only — stress < 0.30 gate removed (fired too rarely in 2021/2023)

E.8 tested rolling 252d peak — REJECTED (regression: Sharpe 1.296→1.277, avg equity
0.406→0.396, p75 gate failed). Rolling peak resets faster in recovery regimes, creating
fresh penalties earlier and making the RL more defensive, not less. Expanding peak retained.
"""
import numpy as np
import pandas as pd


def _annualised_sharpe(returns: pd.Series) -> float:
    """Annualised Sharpe from a daily return series."""
    if len(returns) < 2:
        return 0.0
    mu = float(returns.mean())
    sigma = float(returns.std(ddof=1))
    if sigma < 1e-12:
        return 0.0
    return float(mu / sigma * np.sqrt(252))


def compute_reward_v2(
    daily_returns: pd.Series,
    portfolio_nav: pd.Series,
    equity_frac: float,
    prev_equity_frac: float,
    cash_frac: float,
    stress_score: float = 0.0,
    spy_trend_positive: bool = True,
    lambda_dd: float = 0.08,
    lambda_cash: float = 0.05,
    lambda_churn: float = 0.02,
) -> float:
    """Five-term reward for Phase E exposure-control RL.

    Args:
        daily_returns: Portfolio daily net returns since last rebalance.
        portfolio_nav: Full NAV history (for cumulative drawdown from peak and recovery).
        equity_frac: Equity sleeve fraction applied at this step [0,1].
        prev_equity_frac: Equity fraction from the previous step (for churn penalty).
        cash_frac: Cash fraction applied at this step [0, 0.60].
        stress_score: B.5 stress score at current step [0,1].
        spy_trend_positive: True if SPY 63d return > 0 at current step date.
        lambda_dd: Drawdown penalty weight (E.7 default 0.08; original E.4 was 0.15).
        lambda_cash: Cash-drag penalty weight (E.7 default 0.05; original E.4 was 0.03).
        lambda_churn: Equity-churn penalty weight (default 0.02).

    Returns:
        Scalar reward (float).
    """
    # Hard guard: collapsed portfolio
    if portfolio_nav is not None and len(portfolio_nav) > 0:
        if float(portfolio_nav.iloc[-1]) <= 0.0:
            return -1.0

    n = len(daily_returns)
    if n < 5:
        return 0.0

    # ------------------------------------------------------------------ #
    # Term 1 — 63d Sharpe (longer window than Phase D's 21d)             #
    # ------------------------------------------------------------------ #
    window = daily_returns.iloc[-63:] if n >= 63 else daily_returns
    sharpe = _annualised_sharpe(window)

    # ------------------------------------------------------------------ #
    # Term 2 — Recovery bonus (0.10)                                     #
    # Rewards rising from a recent trough; incentivises re-risking.      #
    # ------------------------------------------------------------------ #
    recovery_bonus = 0.0
    if portfolio_nav is not None and len(portfolio_nav) >= 2:
        recent_nav = portfolio_nav.iloc[-63:] if len(portfolio_nav) >= 63 else portfolio_nav
        nav_now = float(recent_nav.iloc[-1])
        nav_trough = float(recent_nav.min())
        if nav_trough > 1e-12:
            recovery_bonus = 0.10 * max(0.0, (nav_now - nav_trough) / nav_trough)

    # ------------------------------------------------------------------ #
    # Term 3 — Drawdown penalty                                          #
    # drawdown_from_peak ≤ 0 (negative); −drawdown ≥ 0 → positive penalty
    # ------------------------------------------------------------------ #
    dd_penalty = 0.0
    if portfolio_nav is not None and len(portfolio_nav) > 0:
        peak = float(portfolio_nav.expanding().max().iloc[-1])
        nav_now = float(portfolio_nav.iloc[-1])
        if peak > 1e-12:
            drawdown_from_peak = (nav_now - peak) / peak   # ≤ 0
            dd_penalty = lambda_dd * max(0.0, -drawdown_from_peak)

    # ------------------------------------------------------------------ #
    # Term 4 — Cash-drag penalty (bull regimes only)                     #
    # Prevents RL hiding in cash to avoid drawdown penalty.              #
    # ------------------------------------------------------------------ #
    bull_regime = spy_trend_positive
    cash_drag = lambda_cash * float(cash_frac) * (1.0 if bull_regime else 0.0)

    # ------------------------------------------------------------------ #
    # Term 5 — Equity churn penalty                                      #
    # ------------------------------------------------------------------ #
    churn_penalty = lambda_churn * abs(float(equity_frac) - float(prev_equity_frac))

    return sharpe + recovery_bonus - dd_penalty - cash_drag - churn_penalty
