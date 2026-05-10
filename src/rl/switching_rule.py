"""Phase G.4 — Dual-Mode Allocation Switching Rule.

Automatic mode switching between b5_only (safe fallback) and rl_e7 (performance mode)
based on quantitative triggers.

Usage
-----
from src.rl.switching_rule import SwitchingRuleEngine
from src.rl.audit_trail import query_decisions

engine = SwitchingRuleEngine(b5_sharpe_ref=1.296, b5_maxdd_ref=-0.2448)
audit_df = query_decisions(end=str(as_of_date.date()))
drift_flags_df = pd.read_parquet("data/drift/flags.parquet")

new_mode, reason = engine.evaluate(
    audit_df, drift_flags_df, mode="rl_e7", manual_override=None
)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ── Helper functions ──────────────────────────────────────────────────────────

def _consecutive_count(bool_series: pd.Series) -> int:
    """Return the number of consecutive True values at the tail of bool_series."""
    if bool_series.empty:
        return 0
    runs = bool_series.ne(bool_series.shift()).cumsum()
    consecutive = bool_series.groupby(runs).cumsum()
    return int(consecutive.iloc[-1])


def _rolling_sharpe(nav_series: pd.Series, window: int = 63, ann: int = 252) -> pd.Series:
    """Compute rolling Sharpe ratio from NAV series."""
    rets = nav_series.pct_change().dropna()
    roll_mean = rets.rolling(window).mean()
    roll_std  = rets.rolling(window).std()
    sharpe = (roll_mean / roll_std * np.sqrt(ann)).dropna()
    return sharpe


# ── Core switching engine ─────────────────────────────────────────────────────

@dataclass
class SwitchingDecision:
    mode: str              # "rl_e7" | "b5_only"
    reason: str            # Human-readable trigger reason
    trigger_type: str      # "sharpe_degradation" | "maxdd_excess" | "drift_cooccur" | ...
    diagnostics: dict      # Additional metrics for logging


class SwitchingRuleEngine:
    """Quantitative mode-switching rule for dual-mode allocation system."""

    def __init__(
        self,
        b5_sharpe_ref: float = 1.296,
        b5_maxdd_ref: float = -0.2448,
        rolling_window: int = 63,
    ):
        self.b5_sharpe_ref = b5_sharpe_ref
        self.b5_maxdd_ref = b5_maxdd_ref
        self.rolling_window = rolling_window

    def evaluate(
        self,
        audit_df: pd.DataFrame,
        drift_flags_df: pd.DataFrame,
        mode: str,
        manual_override: Optional[str] = None,
        nav_b5_backtest: Optional[pd.Series] = None,
        nav_rl_backtest: Optional[pd.Series] = None,
    ) -> tuple[str, str]:
        """
        Evaluate switching rule and return (new_mode, reason).

        Args:
            audit_df: Historical allocation decisions (columns: as_of_date, nav, equity_frac, ...)
            drift_flags_df: Flag history (columns: as_of_date, flag_sharpe_degradation, ...)
            mode: Current mode ("rl_e7" | "b5_only")
            manual_override: Force mode ("rl_e7" | "b5_only" | None)
            nav_b5_backtest: Pre-computed B.5 NAV series (optional, for B.5→RL recovery check)
            nav_rl_backtest: Pre-computed RL NAV series (optional, for B.5→RL recovery check)

        Returns:
            (new_mode, reason) tuple
        """
        # Manual override takes precedence
        if manual_override is not None:
            logger.info("Manual override to mode=%s", manual_override)
            return manual_override, f"manual_override_to_{manual_override}"

        # Cold start check
        if audit_df.empty or len(audit_df) < 65:
            logger.warning(
                "Insufficient audit history (%d records) for switching logic",
                len(audit_df),
            )
            return mode, "cold_start_insufficient_data"

        # Route to appropriate evaluation path
        if mode == "rl_e7":
            return self._evaluate_rl_to_b5(audit_df, drift_flags_df)
        else:  # mode == "b5_only"
            return self._evaluate_b5_to_rl(audit_df, drift_flags_df, nav_b5_backtest, nav_rl_backtest)

    # ── RL → B.5 Switching Logic (ANY of 4 triggers fires) ───────────────────

    def _evaluate_rl_to_b5(
        self,
        audit_df: pd.DataFrame,
        drift_flags_df: pd.DataFrame,
    ) -> tuple[str, str]:
        """Check if we should switch from rl_e7 → b5_only."""

        # Trigger 1: Sharpe degradation (threshold −0.10, sustained ≥21d)
        sharpe_active, sharpe_reason = self._check_sharpe_degradation(
            audit_df, threshold=-0.10, sustained_days=21
        )
        if sharpe_active:
            logger.warning("Sharpe degradation trigger fired: %s", sharpe_reason)
            return "b5_only", f"sharpe_degradation: {sharpe_reason}"

        # Trigger 2: MaxDD excess (> 7pp worse than B.5)
        maxdd_active, maxdd_reason = self._check_maxdd_excess(
            audit_df, excess_pp=0.07
        )
        if maxdd_active:
            logger.warning("MaxDD excess trigger fired: %s", maxdd_reason)
            return "b5_only", f"maxdd_excess: {maxdd_reason}"

        # Trigger 3: 2+ drift flags co-occur within 5 trading days
        drift_active, drift_reason = self._check_drift_flags_5day(
            drift_flags_df, window_days=5
        )
        if drift_active:
            logger.warning("Drift flags co-occurrence trigger fired: %s", drift_reason)
            return "b5_only", f"drift_cooccur: {drift_reason}"

        # No triggers fired → stay in rl_e7
        return "rl_e7", "no_trigger_all_within_bounds"

    def _check_sharpe_degradation(
        self,
        audit_df: pd.DataFrame,
        threshold: float = -0.10,
        sustained_days: int = 21,
    ) -> tuple[bool, str]:
        """
        Check if rolling 63d Sharpe < (B.5_ref + threshold) for ≥ sustained_days.

        Threshold: -0.10 (vs G.3 flag at -0.05 to prevent chattering)
        """
        nav = audit_df.set_index("as_of_date")["nav"].sort_index()
        if len(nav) < 65:
            return False, f"insufficient_data ({len(nav)} records)"

        roll_sharpe = _rolling_sharpe(nav, window=self.rolling_window)
        if roll_sharpe.empty:
            return False, "rolling_sharpe_empty"

        floor = self.b5_sharpe_ref + threshold
        below = roll_sharpe < floor
        n_consec = _consecutive_count(below)
        current = float(roll_sharpe.iloc[-1])

        active = n_consec >= sustained_days
        reason = (
            f"rolling_sharpe={current:.3f} vs floor={floor:.3f} "
            f"(ref={self.b5_sharpe_ref:.3f} + {threshold:.3f}); "
            f"days_below={n_consec} (flag_at≥{sustained_days}d)"
        )
        return active, reason

    def _check_maxdd_excess(
        self,
        audit_df: pd.DataFrame,
        excess_pp: float = 0.07,
    ) -> tuple[bool, str]:
        """
        Check if live MaxDD exceeds B.5 MaxDD by > excess_pp (7pp).

        Threshold: 7pp (vs G.3 flag at 5pp)
        """
        nav = audit_df.set_index("as_of_date")["nav"].sort_index()
        if len(nav) < 2:
            return False, f"insufficient_data ({len(nav)} records)"

        running_max = nav.expanding().max()
        drawdowns = (nav / running_max) - 1.0
        live_maxdd = float(drawdowns.min())

        # excess > 0 means live is worse (deeper drawdown) than B.5
        # e.g., -0.30 - (-0.2448) = -0.0552 → excess is 5.52pp worse
        excess = live_maxdd - self.b5_maxdd_ref

        active = excess < -excess_pp
        reason = (
            f"live_maxdd={live_maxdd:.1%} vs b5_ref={self.b5_maxdd_ref:.1%} "
            f"(excess={abs(excess):.1%}; flag_at>{excess_pp:.0%})"
        )
        return active, reason

    def _check_drift_flags_5day(
        self,
        drift_flags_df: pd.DataFrame,
        window_days: int = 5,
    ) -> tuple[bool, str]:
        """
        Check if 2+ drift flags co-occur within any 5-trading-day window.

        Uses flag history from data/drift/flags.parquet.
        """
        if drift_flags_df.empty:
            return False, "no_flag_data"

        df = drift_flags_df.copy()
        df["as_of_date"] = pd.to_datetime(df["as_of_date"])
        df = df.set_index("as_of_date").sort_index()

        # Expected columns from G.3 drift monitor
        flag_cols = [
            "flag_sharpe_degradation",
            "flag_drawdown_excess",
            "flag_cash_trap",
            "flag_feature_psi",
            "flag_stress_breach",
        ]

        # Check which columns exist
        available_flags = [col for col in flag_cols if col in df.columns]
        if len(available_flags) < 2:
            return False, f"insufficient_flag_columns ({len(available_flags)} available)"

        # Convert to bool
        flag_bool = df[available_flags].astype(bool)

        # Count active flags per day
        daily_count = flag_bool.sum(axis=1)

        # Rolling max over 5 trading days
        rolling_max = daily_count.rolling(window=window_days).max()

        # Alert if any 5-day window has 2+ flags
        cooccur_active = (rolling_max >= 2).any()

        if cooccur_active:
            # Find which flags co-occurred in the most recent window
            last_window_start = df.index.max() - pd.Timedelta(days=window_days)
            window_df = flag_bool[flag_bool.index >= last_window_start]
            co_firing = [col.replace("flag_", "") for col in available_flags if window_df[col].any()]
            reason = f"2+ flags co-occurred within {window_days}d window: {', '.join(co_firing)}"
        else:
            reason = f"no 2+ flag co-occurrences in last {window_days} days"

        return cooccur_active, reason

    # ── B.5 → RL Recovery Logic (ALL of 2 triggers must fire) ────────────────

    def _evaluate_b5_to_rl(
        self,
        audit_df: pd.DataFrame,
        drift_flags_df: pd.DataFrame,
        nav_b5_backtest: Optional[pd.Series],
        nav_rl_backtest: Optional[pd.Series],
    ) -> tuple[str, str]:
        """Check if we should switch from b5_only → rl_e7."""

        # Trigger 1: Flags quiescent for ≥10 consecutive trading days
        quiescent_active, quiescent_reason = self._check_flags_quiescent(
            drift_flags_df, min_quiescent_days=10
        )
        if not quiescent_active:
            return "b5_only", f"flags_not_quiescent: {quiescent_reason}"

        # Trigger 2: RL paper-trading Sharpe ≥ B.5 rolling Sharpe − 0.05
        if nav_b5_backtest is None or nav_rl_backtest is None:
            logger.info(
                "No B.5/RL NAV backtests provided — cannot check recovery trigger"
            )
            return "b5_only", "missing_nav_backtests_for_recovery_check"

        recovered_active, recovered_reason = self._check_paper_rl_sharpe(
            audit_df, nav_b5_backtest, nav_rl_backtest, threshold=-0.05
        )
        if not recovered_active:
            return "b5_only", f"rl_not_recovered: {recovered_reason}"

        # Both triggers fired → switch to rl_e7
        logger.info(
            "B.5→RL switch triggered: flags quiescent (%s) AND RL recovered (%s)",
            quiescent_reason, recovered_reason,
        )
        return "rl_e7", f"recovery: {quiescent_reason} + {recovered_reason}"

    def _check_flags_quiescent(
        self,
        drift_flags_df: pd.DataFrame,
        min_quiescent_days: int = 10,
    ) -> tuple[bool, str]:
        """Check if no flags have been active for ≥ min_quiescent_days."""
        if drift_flags_df.empty:
            return False, "no_flag_data"

        df = drift_flags_df.copy()
        df["as_of_date"] = pd.to_datetime(df["as_of_date"])
        df = df.set_index("as_of_date").sort_index()

        flag_cols = [
            "flag_sharpe_degradation",
            "flag_drawdown_excess",
            "flag_cash_trap",
            "flag_feature_psi",
            "flag_stress_breach",
        ]
        available_flags = [col for col in flag_cols if col in df.columns]
        if not available_flags:
            return False, "no_flag_columns"

        # Any flag active on a given date?
        any_flag_active = (df[available_flags].astype(bool)).any(axis=1)

        # Find longest consecutive False run at tail
        false_run = _consecutive_count(~any_flag_active)

        quiescent = false_run >= min_quiescent_days
        reason = (
            f"flags_quiescent_for={false_run}d (need≥{min_quiescent_days}d)"
        )
        return quiescent, reason

    def _check_paper_rl_sharpe(
        self,
        audit_df: pd.DataFrame,
        nav_b5_backtest: pd.Series,
        nav_rl_backtest: pd.Series,
        threshold: float = -0.05,
    ) -> tuple[bool, str]:
        """
        Check if RL paper-trading Sharpe ≥ B.5 rolling Sharpe + threshold.

        Threshold: -0.05 (more lenient than RL→B.5 at -0.10)
        """
        if len(audit_df) < 65:
            return False, "insufficient_audit_data"

        # Get latest date from audit
        latest_date = pd.Timestamp(audit_df["as_of_date"].max())

        # Slice both backtest series to include latest_date
        b5_nav = nav_b5_backtest[nav_b5_backtest.index <= latest_date]
        rl_nav = nav_rl_backtest[nav_rl_backtest.index <= latest_date]

        if len(b5_nav) < 65 or len(rl_nav) < 65:
            return False, "insufficient_backtest_data"

        b5_sharpe = _rolling_sharpe(b5_nav, window=self.rolling_window).iloc[-1]
        rl_sharpe = _rolling_sharpe(rl_nav, window=self.rolling_window).iloc[-1]

        delta = rl_sharpe - b5_sharpe
        recovered = delta >= threshold

        reason = (
            f"rl_paper_sharpe={rl_sharpe:.3f} vs b5_rolling={b5_sharpe:.3f} "
            f"(delta={delta:+.3f}, need≥{threshold:.3f})"
        )
        return recovered, reason
