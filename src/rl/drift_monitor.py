"""Phase G.3 — Live drift monitoring for RL policy.

Five flags (rolling 63d unless noted):
  1. sharpe_degradation  — rolling 63d live Sharpe < B.5 ref − 0.05 for ≥ 21d
  2. drawdown_excess     — live MaxDD exceeds B.5 MaxDD by > 5pp
  3. cash_trap           — equity_frac < 0.25 for ≥ 10 consecutive rebalances
  4. feature_psi         — PSI > 0.20 on any key state feature (VIX, vol, stress)
  5. stress_breach       — stress_score > 0.70 for ≥ 5 consecutive days

Alert rule: any 2 flags active simultaneously → escalate to manual review,
consider switching to b5_only mode (G.4 switching rule).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Key state features monitored via PSI (column name → human name)
PSI_KEY_FEATURES = {
    "state_0":  "vix_percentile_1y",
    "state_4":  "realized_market_vol_63d",
    "state_13": "stress_score",
}

PSI_WARN  = 0.10  # moderate change — monitor
PSI_ALERT = 0.20  # significant change — flag


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class FlagResult:
    active: bool
    value: float        # current metric value
    threshold: float    # the boundary that triggers the flag
    message: str        # human-readable detail


@dataclass
class DriftReport:
    as_of_date: str
    flags: dict         # flag_name -> FlagResult
    alert_active: bool
    alert_flags: list   # names of co-firing flags
    alert_message: str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _consecutive_count(bool_series: pd.Series) -> int:
    """Return the number of consecutive True values at the tail of bool_series."""
    if bool_series.empty:
        return 0
    runs = bool_series.ne(bool_series.shift()).cumsum()
    consecutive = bool_series.groupby(runs).cumsum()
    return int(consecutive.iloc[-1])


def _rolling_sharpe(nav_series: pd.Series, window: int = 63, ann: int = 252) -> pd.Series:
    rets = nav_series.pct_change().dropna()
    roll_mean = rets.rolling(window).mean()
    roll_std  = rets.rolling(window).std()
    sharpe = (roll_mean / roll_std * np.sqrt(ann)).dropna()
    return sharpe


def _psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index between two 1-d arrays."""
    if len(expected) < 5 or len(actual) < 5:
        return 0.0
    all_vals = np.concatenate([expected, actual])
    edges = np.percentile(all_vals, np.linspace(0, 100, bins + 1))
    edges[0]  -= 1e-9
    edges[-1] += 1e-9
    exp_cnt, _ = np.histogram(expected, bins=edges)
    act_cnt, _ = np.histogram(actual,   bins=edges)
    eps = 1e-9
    exp_pct = np.maximum(exp_cnt / max(exp_cnt.sum(), 1), eps)
    act_pct = np.maximum(act_cnt / max(act_cnt.sum(), 1), eps)
    return float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))


# ── Flag detectors ────────────────────────────────────────────────────────────

def flag_sharpe_degradation(
    audit_df: pd.DataFrame,
    b5_sharpe_ref: float = 1.296,
    delta_threshold: float = -0.05,
    sustained_days: int = 21,
) -> FlagResult:
    """Flag if rolling 63d Sharpe < (b5_sharpe_ref + delta_threshold) for >= sustained_days."""
    nav = audit_df.set_index("as_of_date")["nav"].sort_index()
    if len(nav) < 65:
        return FlagResult(
            False, float("nan"), delta_threshold,
            f"Insufficient data ({len(nav)} records; need ≥65 for 63d rolling Sharpe)",
        )
    roll_sharpe = _rolling_sharpe(nav, window=63)
    if roll_sharpe.empty:
        return FlagResult(False, float("nan"), delta_threshold, "Rolling Sharpe returned empty")

    floor = b5_sharpe_ref + delta_threshold
    below = roll_sharpe < floor
    n_consec = _consecutive_count(below)
    current = float(roll_sharpe.iloc[-1])
    active = n_consec >= sustained_days
    msg = (
        f"Rolling Sharpe={current:.3f} vs B.5 ref {b5_sharpe_ref:.3f} "
        f"(delta={current - b5_sharpe_ref:+.3f}); "
        f"days below {floor:.3f} = {n_consec} (flag at ≥{sustained_days}d)"
    )
    return FlagResult(active, current - b5_sharpe_ref, delta_threshold, msg)


def flag_drawdown_excess(
    audit_df: pd.DataFrame,
    b5_maxdd_ref: float = -0.2448,
    excess_pp: float = 0.05,
) -> FlagResult:
    """Flag if live MaxDD exceeds B.5 MaxDD by > excess_pp (5pp)."""
    nav = audit_df.set_index("as_of_date")["nav"].sort_index()
    if len(nav) < 2:
        return FlagResult(
            False, float("nan"), excess_pp,
            f"Insufficient data ({len(nav)} records)",
        )
    running_max = nav.expanding().max()
    drawdowns  = (nav / running_max) - 1.0
    live_maxdd = float(drawdowns.min())
    # excess > 0 means live is worse (deeper drawdown) than B.5
    excess = live_maxdd - b5_maxdd_ref  # e.g. -0.30 - (-0.2448) = -0.055
    active = excess < -excess_pp
    msg = (
        f"Live MaxDD={live_maxdd:.1%} vs B.5 ref {b5_maxdd_ref:.1%} "
        f"(excess={-excess:.1%}; flag at >{excess_pp:.0%})"
    )
    return FlagResult(active, float(excess), -excess_pp, msg)


def flag_cash_trap(
    audit_df: pd.DataFrame,
    equity_threshold: float = 0.25,
    consecutive_rebalances: int = 10,
) -> FlagResult:
    """Flag if equity_frac < threshold for >= consecutive_rebalances rebalance events."""
    reb = audit_df[audit_df["is_rebalance"] == True].sort_values("as_of_date").reset_index(drop=True)
    if reb.empty:
        return FlagResult(False, float("nan"), equity_threshold, "No rebalance records")
    below = reb["equity_frac"] < equity_threshold
    n_consec = _consecutive_count(below)
    current_eq = float(reb["equity_frac"].iloc[-1])
    active = n_consec >= consecutive_rebalances
    msg = (
        f"equity_frac={current_eq:.3f} (threshold={equity_threshold:.2f}); "
        f"consecutive rebalances below threshold = {n_consec} (flag at ≥{consecutive_rebalances})"
    )
    return FlagResult(active, current_eq, equity_threshold, msg)


def flag_feature_psi(
    audit_df: pd.DataFrame,
    baseline_df: Optional[pd.DataFrame] = None,
    psi_threshold: float = PSI_ALERT,
    baseline_window: int = 63,
) -> FlagResult:
    """Flag if PSI > psi_threshold on any key state feature vs training baseline.

    Baseline defaults to the first `baseline_window` audit records when not provided.
    Reports 'insufficient data' if the audit log is too short to split.
    """
    df = audit_df.sort_values("as_of_date").reset_index(drop=True)
    if baseline_df is None:
        min_needed = baseline_window + 10
        if len(df) < min_needed:
            return FlagResult(
                False, float("nan"), psi_threshold,
                f"Insufficient data for PSI ({len(df)} records; need ≥{min_needed})",
            )
        baseline_df = df.head(baseline_window)
        live_df = df.tail(min(63, len(df) - baseline_window))
    else:
        live_df = df.tail(63)

    max_psi = 0.0
    worst_feat = ""
    psi_by_feat: dict[str, float] = {}
    for col, name in PSI_KEY_FEATURES.items():
        if col not in baseline_df.columns or col not in live_df.columns:
            continue
        base_vals = baseline_df[col].dropna().values
        live_vals = live_df[col].dropna().values
        if len(base_vals) < 5 or len(live_vals) < 5:
            continue
        psi_val = _psi(base_vals, live_vals)
        psi_by_feat[name] = psi_val
        if psi_val > max_psi:
            max_psi = psi_val
            worst_feat = name

    if not psi_by_feat:
        return FlagResult(False, float("nan"), psi_threshold, "No PSI features available")

    active = max_psi > psi_threshold
    detail = ", ".join(f"{k}={v:.3f}" for k, v in psi_by_feat.items())
    msg = (
        f"Max PSI={max_psi:.3f} on '{worst_feat}' (threshold={psi_threshold:.2f}); "
        f"by feature: {detail}"
    )
    return FlagResult(active, max_psi, psi_threshold, msg)


def flag_stress_breach(
    audit_df: pd.DataFrame,
    stress_threshold: float = 0.70,
    consecutive_days: int = 5,
) -> FlagResult:
    """Flag if stress_score > threshold for >= consecutive_days."""
    df = audit_df.sort_values("as_of_date").reset_index(drop=True)
    if df.empty:
        return FlagResult(False, float("nan"), stress_threshold, "No records")
    above = df["stress_score"] > stress_threshold
    n_consec = _consecutive_count(above)
    current_stress = float(df["stress_score"].iloc[-1])
    active = n_consec >= consecutive_days
    msg = (
        f"stress_score={current_stress:.3f} (threshold={stress_threshold:.2f}); "
        f"consecutive days above threshold = {n_consec} (flag at ≥{consecutive_days}d)"
    )
    return FlagResult(active, current_stress, stress_threshold, msg)


# ── Alert aggregation ─────────────────────────────────────────────────────────

def check_alert(flag_results: dict) -> tuple[bool, list, str]:
    """Return (alert_active, co_firing_flag_names, message).

    Alert fires when ≥2 flags are simultaneously active (same snapshot = within
    the same daily observation window, satisfying the '5 trading days' rule).
    """
    active_flags = [name for name, r in flag_results.items() if r.active]
    alert = len(active_flags) >= 2
    msg = ""
    if alert:
        msg = (
            f"ALERT: {len(active_flags)} drift flags active simultaneously "
            f"({', '.join(active_flags)}) — escalate to manual review; "
            f"consider switching to b5_only mode (G.4 switching rule)"
        )
    return alert, active_flags, msg


# ── Public entry point ────────────────────────────────────────────────────────

def run_drift_check(
    audit_df: pd.DataFrame,
    b5_sharpe_ref: float = 1.296,
    b5_maxdd_ref: float = -0.2448,
    baseline_df: Optional[pd.DataFrame] = None,
) -> DriftReport:
    """Run all 5 drift flags on audit_df and return a DriftReport."""
    as_of = (
        str(audit_df["as_of_date"].max().date())
        if not audit_df.empty
        else "N/A"
    )
    flags = {
        "sharpe_degradation": flag_sharpe_degradation(audit_df, b5_sharpe_ref),
        "drawdown_excess":    flag_drawdown_excess(audit_df, b5_maxdd_ref),
        "cash_trap":          flag_cash_trap(audit_df),
        "feature_psi":        flag_feature_psi(audit_df, baseline_df),
        "stress_breach":      flag_stress_breach(audit_df),
    }
    alert_active, alert_flags, alert_message = check_alert(flags)
    return DriftReport(
        as_of_date=as_of,
        flags=flags,
        alert_active=alert_active,
        alert_flags=alert_flags,
        alert_message=alert_message,
    )
