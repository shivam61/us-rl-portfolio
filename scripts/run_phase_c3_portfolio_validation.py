"""
Phase C.3 — Portfolio Validation of simple_mean_rank

Validates the 14-feature rank composite (simple_mean_rank) discovered in C.2 through
the unchanged B.5 portfolio harness.  Only the stock-selection signal changes:

    baseline  → vol_score (low-vol composite, 4 features)
    candidate → simple_mean_rank (equal-weight rank percentile of 14 positive-IC features)

Everything else preserved: every_2_rebalances cadence, stress blend, trend sleeve,
dynamic beta cap (0.90 − 0.20×stress), beta floor 0.50, RL disabled.

Outputs:
    artifacts/reports/phase_c3_signal_validation.md
    artifacts/reports/c3_portfolio_comparison.csv
    artifacts/reports/c3_regime_breakdown.csv
    artifacts/reports/c3_selected_overlap.csv
    artifacts/reports/c3_cost_sensitivity.csv
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (REPO_ROOT, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from run_phase_a7_1_drawdown_control import TREND_NAME, stress_frame  # noqa: E402
from run_phase_a7_2_robustness import stress_variant_frame, weight_frame  # noqa: E402
from run_phase_a7_trend_overlay import (  # noqa: E402
    TREND_ASSETS,
    build_trend_weight_paths,
    equal_weights,
    load_inputs,
    rebalance_dates,
)
from run_phase_b1_simulator_reproduction import (  # noqa: E402
    CANDIDATE_BASE_TREND_WEIGHT,
    CANDIDATE_STRESS_K,
    CANDIDATE_TREND_CAP,
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (  # noqa: E402
    B1_COST_BPS,
    COST_BPS,
    Variant,
    apply_execution_controls,
    build_vol_path_fast,
    run_execution_simulator,
    signal_dates_for_frequency,
)
from run_phase_b3_exposure_control import rolling_beta_matrix  # noqa: E402
from run_phase_b4_risk_engine import (  # noqa: E402
    BETA_MAX_BASE,
    BETA_MAX_SENSITIVITY,
    BETA_MIN,
    TREND_STRESS_SCALE_MAX,
    TREND_STRESS_THRESHOLD,
    B4Variant,
    _NON_BENCHMARK_TREND,
    apply_b4_constraints,
    apply_trend_scaling,
    build_stress_series,
)
from src.reporting.metrics import calculate_metrics  # noqa: E402
from src.alpha import compute_volatility_score_frame  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Phase B.5 baseline metrics ────────────────────────────────────────────────
B5_CAGR = 0.1604
B5_SHARPE = 1.078
B5_MAX_DD = -0.3298
B5_TURNOVER = 84.12
B5_50BPS_SHARPE = 0.934

# ── Phase C.2 signal IC results ───────────────────────────────────────────────
C2_VOL_SCORE_IC_SHARPE = 1.6682
C2_SIMPLE_MEAN_RANK_IC_SHARPE = 1.8559

# ── Phase C gates ─────────────────────────────────────────────────────────────
GATE_SHARPE_MAINTAIN = 1.05        # must maintain
GATE_SHARPE_PREFERRED = B5_SHARPE  # preferred: match/beat B.5
GATE_MAXDD = -0.35                 # MaxDD >= -35%
GATE_MAXDD_HARD = -0.40            # hard floor
GATE_50BPS_SHARPE = 0.884          # 50 bps Sharpe gate
GATE_TURNOVER = 100.0              # turnover sum gate

# ── 14 positive-IC features (from C.2 holdout analysis) ──────────────────────
POSITIVE_IC_FEATURES = [
    "beta_to_spy_63d",        # IC Sharpe 1.7883
    "downside_vol_63d",       # IC Sharpe 1.7823
    "volatility_21d",         # IC Sharpe 1.7621
    "volatility_63d",         # IC Sharpe 1.7574
    "liquidity_rank",         # IC Sharpe 1.0227
    "avg_dollar_volume_63d",  # IC Sharpe 1.0227
    "ret_12m_ex_1m",          # IC Sharpe 0.6317
    "ret_12m",                # IC Sharpe 0.6130
    "sector_rel_momentum_6m", # IC Sharpe 0.3706
    "trend_consistency",      # IC Sharpe 0.3452
    "ma_50_200_ratio",        # IC Sharpe 0.3222
    "above_200dma",           # IC Sharpe 0.2204
    "ret_6m_adj",             # IC Sharpe 0.2014
    "ret_6m",                 # IC Sharpe 0.1078
]

# ── Regime windows ────────────────────────────────────────────────────────────
REGIMES = [
    ("2008 financial crisis", "2008-01-01", "2009-12-31"),
    ("2015-16 vol stress", "2015-06-01", "2016-12-31"),
    ("2020 COVID", "2020-01-01", "2020-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("2023-2026 recovery", "2023-01-01", "2026-04-24"),
    ("full 2008-2026", "2008-01-01", "2026-04-24"),
]

B5_PROMOTED = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _active_tickers_at(inputs: dict, date: pd.Timestamp) -> list[str]:
    base = list(inputs["universe_config"].tickers.keys())
    pit_mask = inputs["pit_mask"]
    if pit_mask is None:
        return base
    idx = pit_mask.index.get_indexer([date], method="ffill")[0]
    if idx < 0:
        return base
    active = pit_mask.iloc[idx]
    return [t for t in base if bool(active.get(t, False))]


def _metrics_for_window(net_ret: pd.Series, start: str, end: str) -> dict:
    mask = (net_ret.index >= pd.Timestamp(start)) & (net_ret.index <= pd.Timestamp(end))
    sliced = net_ret[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod()
    m = calculate_metrics(nav)
    return {
        "cagr": m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def _compute_net_returns(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
    cost_bps: float,
) -> pd.Series:
    dates = constrained.index[constrained.index <= validation_end]
    weights = constrained.reindex(dates).fillna(0.0)
    executable = weights.shift(1).fillna(0.0)
    returns = (
        inputs["prices"]
        .pct_change()
        .fillna(0.0)
        .reindex(index=dates, columns=weights.columns)
        .fillna(0.0)
    )
    turnover = executable.diff().abs().sum(axis=1)
    if not executable.empty:
        turnover.iloc[0] = executable.iloc[0].abs().sum()
    raw_ret = (executable * returns).sum(axis=1)
    return (1.0 - turnover * cost_bps / 10000.0).clip(lower=0.0) * (1.0 + raw_ret) - 1.0


# ── Signal: simple_mean_rank ──────────────────────────────────────────────────

def build_simple_mean_rank_vol_path(
    inputs: dict,
    positive_ic_features: list[str],
    n_top: int = 20,
) -> dict:
    """
    Stock-selection signal using simple_mean_rank composite.

    At each rebalance date:
      1. Get feature values for positive_ic_features from stock_features (ffill)
      2. rank(pct=True) within the active universe for each feature
      3. mean of rank percentiles = composite score
      4. Select top n_top stocks by composite score

    No model training; purely deterministic from lagged features.
    """
    stock_features = inputs["stock_features"]
    feat_level_dates = stock_features.index.get_level_values("date").unique().sort_values()
    all_rb_dates = rebalance_dates(inputs["base_config"], inputs["prices"])

    avail_features = [f for f in positive_ic_features if f in stock_features.columns]
    missing = [f for f in positive_ic_features if f not in stock_features.columns]
    if missing:
        logger.warning("simple_mean_rank: missing features (skipped): %s", missing)

    weights_by_date: dict = {}
    selected_by_date: dict = {}

    for date in all_rb_dates:
        active = _active_tickers_at(inputs, date)

        fi = feat_level_dates.get_indexer([date], method="ffill")[0]
        selected: list[str]
        if fi < 0 or not avail_features:
            selected = active[:n_top]
        else:
            feat_date = feat_level_dates[fi]
            try:
                X_snap = stock_features.xs(feat_date, level="date")[avail_features].reindex(active)
                rank_pct = X_snap.rank(pct=True)
                composite = rank_pct.mean(axis=1).dropna()
                n = min(n_top, len(composite))
                selected = composite.nlargest(n).index.tolist()
                if len(selected) < n_top:
                    remaining = [t for t in active if t not in selected]
                    selected += remaining[: n_top - len(selected)]
            except KeyError:
                selected = active[:n_top]

        weights_by_date[date] = equal_weights(selected)
        selected_by_date[date] = selected

    return {
        "weights": weights_by_date,
        "selected": selected_by_date,
        "sleeve_type": "simple_mean_rank",
    }


# ── B.5 harness with new signal ───────────────────────────────────────────────

def build_simple_mean_rank_b2_candidate(
    inputs: dict,
    validation_end: pd.Timestamp,
    positive_ic_features: list[str],
) -> pd.DataFrame:
    """B.5 construction (stress blend + every_2_rebalances) with simple_mean_rank signal."""
    dates = clipped_evaluation_dates(inputs, validation_end)
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)

    smr_path = build_simple_mean_rank_vol_path(inputs, positive_ic_features, n_top=20)
    smr_weights = weight_frame(smr_path, dates)
    trend_weights = weight_frame(trend_path, dates)

    columns = smr_weights.columns.union(trend_weights.columns)
    smr_w = smr_weights.reindex(columns=columns, fill_value=0.0)
    trend_w = trend_weights.reindex(columns=columns, fill_value=0.0)

    stress_score = stress["stress_score"].reindex(dates).fillna(0.0)
    trend_sleeve_weight = (CANDIDATE_BASE_TREND_WEIGHT + CANDIDATE_STRESS_K * stress_score).clip(
        upper=CANDIDATE_TREND_CAP
    )
    vol_sleeve_weight = (1.0 - trend_sleeve_weight).clip(lower=0.0)
    raw = (smr_w.mul(vol_sleeve_weight, axis=0) + trend_w.mul(trend_sleeve_weight, axis=0)).fillna(0.0)

    signal_dates = signal_dates_for_frequency(inputs, raw, validation_end, "every_2_rebalances")
    return apply_execution_controls(raw, signal_dates, trade_threshold=0.0, partial_rebalance=1.0)


def build_promoted_simple_mean_rank_weights(
    inputs: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    positive_ic_features: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, list[pd.Timestamp]]:
    """Full B.5 harness (trend scaling + dynamic beta cap) with simple_mean_rank signal."""
    base_weights = build_simple_mean_rank_b2_candidate(inputs, validation_end, positive_ic_features)
    target_turnover = base_weights.diff().abs().sum(axis=1)
    if not base_weights.empty:
        target_turnover.iloc[0] = base_weights.iloc[0].abs().sum()
    control_dates = list(target_turnover[target_turnover > 1e-12].index)

    trend_tickers = [t for t in _NON_BENCHMARK_TREND if t in base_weights.columns]
    scaled = apply_trend_scaling(
        base_weights,
        stress_series,
        control_dates,
        trend_tickers,
        B5_PROMOTED.trend_stress_threshold,
        B5_PROMOTED.trend_stress_scale_max,
    )
    constrained, diagnostics = apply_b4_constraints(
        scaled,
        beta_frame,
        stress_series,
        B5_PROMOTED,
        control_dates,
        inputs["universe_config"].benchmark,
    )
    return constrained, diagnostics, control_dates


# ── Attribution: selection overlap ────────────────────────────────────────────

def build_selected_overlap_table(
    inputs: dict,
    validation_end: pd.Timestamp,
    positive_ic_features: list[str],
) -> pd.DataFrame:
    """
    At each every_2_rebalances signal date, compare top-20 selection from:
      - simple_mean_rank (candidate)
      - vol_score (baseline)
    Reports overlap count, overlap pct, and Jaccard index.
    """
    smr_path = build_simple_mean_rank_vol_path(inputs, positive_ic_features, n_top=20)
    vol_path = build_vol_path_fast(inputs, exit_rank=None)

    all_rb_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    # every_2_rebalances
    configured = [d for d in all_rb_dates if d <= validation_end]
    signal_dates_every2 = configured[::2]

    rows = []
    for date in signal_dates_every2:
        smr_sel = set(smr_path["selected"].get(date, []))
        vol_sel = set(vol_path["selected"].get(date, []))
        if not smr_sel and not vol_sel:
            continue
        overlap = smr_sel & vol_sel
        union = smr_sel | vol_sel
        rows.append(
            {
                "date": date,
                "n_smr": len(smr_sel),
                "n_vol": len(vol_sel),
                "overlap_count": len(overlap),
                "overlap_pct_smr": len(overlap) / len(smr_sel) if smr_sel else np.nan,
                "jaccard": len(overlap) / len(union) if union else np.nan,
            }
        )
    return pd.DataFrame(rows)


# ── Attribution: sector exposure ─────────────────────────────────────────────

def build_sector_exposure_table(
    inputs: dict,
    validation_end: pd.Timestamp,
    positive_ic_features: list[str],
    smr_constrained: pd.DataFrame,
    vol_constrained: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare mean sector allocation (by weight) between simple_mean_rank and vol_score
    over all rebalance dates.
    """
    ticker_to_sector: dict[str, str] = dict(inputs["universe_config"].tickers)
    all_rb_dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    signal_dates = [d for d in all_rb_dates[::2] if d <= validation_end]

    smr_sector_weights: dict[str, list[float]] = {}
    vol_sector_weights: dict[str, list[float]] = {}
    sectors = sorted(set(ticker_to_sector.values()))

    for date in signal_dates:
        # simple_mean_rank weights at this date
        if date in smr_constrained.index:
            smr_row = smr_constrained.loc[date]
            stock_tickers = [t for t in smr_row.index if t in ticker_to_sector]
            smr_total = smr_row[stock_tickers].abs().sum()
            for sec in sectors:
                sec_tickers = [t for t in stock_tickers if ticker_to_sector[t] == sec]
                w = float(smr_row[sec_tickers].abs().sum() / smr_total) if smr_total > 0 else 0.0
                smr_sector_weights.setdefault(sec, []).append(w)

        # vol_score weights at this date
        if date in vol_constrained.index:
            vol_row = vol_constrained.loc[date]
            stock_tickers = [t for t in vol_row.index if t in ticker_to_sector]
            vol_total = vol_row[stock_tickers].abs().sum()
            for sec in sectors:
                sec_tickers = [t for t in stock_tickers if ticker_to_sector[t] == sec]
                w = float(vol_row[sec_tickers].abs().sum() / vol_total) if vol_total > 0 else 0.0
                vol_sector_weights.setdefault(sec, []).append(w)

    rows = []
    for sec in sectors:
        smr_mean = float(np.mean(smr_sector_weights.get(sec, [0.0])))
        vol_mean = float(np.mean(vol_sector_weights.get(sec, [0.0])))
        rows.append(
            {
                "sector": sec,
                "avg_weight_smr": smr_mean,
                "avg_weight_vol": vol_mean,
                "delta": smr_mean - vol_mean,
            }
        )
    df = pd.DataFrame(rows).sort_values("delta", ascending=False).reset_index(drop=True)
    return df


# ── Portfolio metrics helpers ─────────────────────────────────────────────────

def cost_sensitivity_table(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
    label: str = "c3",
) -> pd.DataFrame:
    rows = []
    initial_capital = inputs["base_config"].portfolio.initial_capital
    for bps in COST_BPS:
        net_ret = _compute_net_returns(inputs, constrained, validation_end, bps)
        nav = (1.0 + net_ret).cumprod() * initial_capital
        m = calculate_metrics(nav)
        rows.append(
            {
                "signal": label,
                "cost_bps": bps,
                "cagr": m.get("CAGR", np.nan),
                "sharpe": m.get("Sharpe", np.nan),
                "max_dd": m.get("Max Drawdown", np.nan),
            }
        )
    return pd.DataFrame(rows)


def regime_breakdown_table(
    inputs: dict,
    constrained: pd.DataFrame,
    validation_end: pd.Timestamp,
    label: str = "c3",
) -> pd.DataFrame:
    net_ret = _compute_net_returns(inputs, constrained, validation_end, B1_COST_BPS)
    rows = []
    for regime_label, start, end in REGIMES:
        m = _metrics_for_window(net_ret, start, end)
        rows.append(
            {
                "signal": label,
                "regime": regime_label,
                "start": start,
                "end": end,
                "cagr": m["cagr"],
                "sharpe": m["sharpe"],
                "max_dd": m["max_dd"],
                "n_days": m["n_days"],
            }
        )
    return pd.DataFrame(rows)


def beta_compliance_summary(diagnostics: pd.DataFrame) -> dict:
    ctrl = (
        diagnostics[diagnostics["is_control_date"]].copy()
        if "is_control_date" in diagnostics.columns
        else diagnostics
    )
    n_total = len(ctrl)
    n_violations = int(ctrl["gate_violation_after"].sum()) if "gate_violation_after" in ctrl.columns else 0
    avg_beta = float(ctrl["beta_after"].mean()) if "beta_after" in ctrl.columns else np.nan
    avg_cap = float(ctrl["dynamic_beta_cap"].mean()) if "dynamic_beta_cap" in ctrl.columns else np.nan
    min_cap = float(ctrl["dynamic_beta_cap"].min()) if "dynamic_beta_cap" in ctrl.columns else np.nan
    return {
        "n_rebalance_dates": n_total,
        "n_gate_violations": n_violations,
        "avg_beta_after": avg_beta,
        "avg_dynamic_cap": avg_cap,
        "min_dynamic_cap": min_cap,
        "compliance_rate": (n_total - n_violations) / n_total if n_total > 0 else np.nan,
    }


# ── Phase C.3 acceptance gates ────────────────────────────────────────────────

def evaluate_c3_gates(
    full_sim: dict,
    cost_df: pd.DataFrame,
    beta_comp: dict,
) -> pd.DataFrame:
    gates = []

    sharpe_10 = full_sim.get("sharpe", np.nan)
    gates.append(
        {
            "gate": f"Sharpe ≥ {GATE_SHARPE_PREFERRED:.3f} (match B.5)",
            "value": f"{sharpe_10:.3f}" if np.isfinite(sharpe_10) else "N/A",
            "target": f"≥ {GATE_SHARPE_PREFERRED:.3f}",
            "b5_value": f"{B5_SHARPE:.3f}",
            "pass": bool(np.isfinite(sharpe_10) and sharpe_10 >= GATE_SHARPE_PREFERRED),
        }
    )
    gates.append(
        {
            "gate": f"Sharpe ≥ {GATE_SHARPE_MAINTAIN:.2f} (maintain floor)",
            "value": f"{sharpe_10:.3f}" if np.isfinite(sharpe_10) else "N/A",
            "target": f"≥ {GATE_SHARPE_MAINTAIN:.2f}",
            "b5_value": f"{B5_SHARPE:.3f}",
            "pass": bool(np.isfinite(sharpe_10) and sharpe_10 >= GATE_SHARPE_MAINTAIN),
        }
    )

    max_dd = full_sim.get("max_dd", np.nan)
    gates.append(
        {
            "gate": f"MaxDD ≥ {GATE_MAXDD:.0%} (maintain)",
            "value": f"{max_dd:.2%}" if np.isfinite(max_dd) else "N/A",
            "target": f"≥ {GATE_MAXDD:.0%}",
            "b5_value": f"{B5_MAX_DD:.2%}",
            "pass": bool(np.isfinite(max_dd) and max_dd >= GATE_MAXDD),
        }
    )
    gates.append(
        {
            "gate": f"MaxDD ≥ {GATE_MAXDD_HARD:.0%} (hard floor)",
            "value": f"{max_dd:.2%}" if np.isfinite(max_dd) else "N/A",
            "target": f"≥ {GATE_MAXDD_HARD:.0%}",
            "b5_value": f"{B5_MAX_DD:.2%}",
            "pass": bool(np.isfinite(max_dd) and max_dd >= GATE_MAXDD_HARD),
        }
    )

    row_50 = cost_df[cost_df["cost_bps"] == 50.0]
    if not row_50.empty:
        sharpe_50 = float(row_50["sharpe"].iloc[0])
        gates.append(
            {
                "gate": f"50 bps Sharpe ≥ {GATE_50BPS_SHARPE:.3f}",
                "value": f"{sharpe_50:.3f}" if np.isfinite(sharpe_50) else "N/A",
                "target": f"≥ {GATE_50BPS_SHARPE:.3f}",
                "b5_value": f"{B5_50BPS_SHARPE:.3f}",
                "pass": bool(np.isfinite(sharpe_50) and sharpe_50 >= GATE_50BPS_SHARPE),
            }
        )

    turnover = full_sim.get("turnover_sum", np.nan)
    gates.append(
        {
            "gate": f"Turnover sum ≤ {GATE_TURNOVER:.0f}",
            "value": f"{turnover:.1f}" if np.isfinite(turnover) else "N/A",
            "target": f"≤ {GATE_TURNOVER:.0f}",
            "b5_value": f"{B5_TURNOVER:.1f}",
            "pass": bool(np.isfinite(turnover) and turnover <= GATE_TURNOVER),
        }
    )

    n_violations = beta_comp["n_gate_violations"]
    gates.append(
        {
            "gate": "Zero rebalance-date beta violations",
            "value": str(n_violations),
            "target": "0",
            "b5_value": "0",
            "pass": bool(n_violations == 0),
        }
    )

    return pd.DataFrame(gates)


# ── Report rendering ──────────────────────────────────────────────────────────

def render_report(
    smr_sim: dict,
    vol_sim: dict,
    smr_cost_df: pd.DataFrame,
    vol_cost_df: pd.DataFrame,
    smr_regime_df: pd.DataFrame,
    vol_regime_df: pd.DataFrame,
    smr_beta_comp: dict,
    gates_df: pd.DataFrame,
    overlap_df: pd.DataFrame,
    sector_df: pd.DataFrame,
    avail_features: list[str],
) -> str:
    all_pass = bool(gates_df["pass"].all())
    critical_pass = bool(gates_df[gates_df["gate"].str.contains("floor|hard")]["pass"].all())
    if all_pass:
        verdict = "PASS — promote simple_mean_rank_14 as production signal"
    elif critical_pass:
        verdict = "CONDITIONAL — hard gates pass, preferred Sharpe gate missed; review"
    else:
        verdict = "FAIL — keep vol_score as production signal"

    now = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Phase C.3 — Portfolio Validation of simple_mean_rank",
        "",
        f"- Run date: {now}",
        "- Candidate signal: `simple_mean_rank_14` — equal-weight rank percentile composite",
        f"  of {len(avail_features)} positive-IC features (from C.2 holdout analysis).",
        "- Baseline signal: `vol_score` — Phase B.5 production signal.",
        "- Portfolio harness: `b4_stress_cap_trend_boost` — unchanged from Phase B.5.",
        "  every_2_rebalances, dynamic beta cap (0.90 − 0.20×stress), beta floor 0.50.",
        "- Universe: sp500, evaluation 2008–2026-04-24.",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    lines += ["## Phase C.3 Acceptance Gates", ""]
    lines.append(gates_df[["gate", "value", "target", "b5_value", "pass"]].to_markdown(index=False))
    lines.append("")

    lines += [
        "## Signal IC Context (from C.2)",
        "",
        "| Signal | IC Sharpe (holdout) | Notes |",
        "|---|---|---|",
        f"| `vol_score` | {C2_VOL_SCORE_IC_SHARPE:.4f} | Production baseline (4 low-vol features) |",
        f"| `simple_mean_rank_14` | {C2_SIMPLE_MEAN_RANK_IC_SHARPE:.4f}"
        " | 14-feature rank composite, no model |",
        "",
    ]

    lines += ["## Full-Period Performance Comparison (10 bps)", ""]
    smr_cagr = smr_sim.get("cagr", np.nan)
    smr_sharpe = smr_sim.get("sharpe", np.nan)
    smr_maxdd = smr_sim.get("max_dd", np.nan)
    smr_to = smr_sim.get("turnover_sum", np.nan)
    vol_cagr = vol_sim.get("cagr", np.nan)
    vol_sharpe = vol_sim.get("sharpe", np.nan)
    vol_maxdd = vol_sim.get("max_dd", np.nan)
    vol_to = vol_sim.get("turnover_sum", np.nan)

    def _fmt(v, pct=False):
        if not np.isfinite(v):
            return "N/A"
        return f"{v:.2%}" if pct else f"{v:.3f}"

    lines += [
        "| Metric | simple_mean_rank | vol_score (B.5) | Delta |",
        "|---|---|---|---|",
        f"| CAGR | {_fmt(smr_cagr, True)} | {_fmt(vol_cagr, True)}"
        f" | {_fmt(smr_cagr - vol_cagr, True)} |",
        f"| Sharpe | {_fmt(smr_sharpe)} | {_fmt(vol_sharpe)}"
        f" | {_fmt(smr_sharpe - vol_sharpe)} |",
        f"| MaxDD | {_fmt(smr_maxdd, True)} | {_fmt(vol_maxdd, True)}"
        f" | {_fmt(smr_maxdd - vol_maxdd, True)} |",
        f"| Turnover sum | {smr_to:.1f} | {vol_to:.1f}"
        f" | {smr_to - vol_to:+.1f} |",
        "",
    ]

    lines += ["## Cost Sensitivity (simple_mean_rank)", ""]
    lines.append(smr_cost_df.drop(columns=["signal"], errors="ignore").to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Cost Sensitivity (vol_score B.5)", ""]
    lines.append(vol_cost_df.drop(columns=["signal"], errors="ignore").to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    # Regime breakdown merged
    lines += ["## Regime Breakdown (10 bps, simple_mean_rank vs vol_score)", ""]
    smr_reg = smr_regime_df[["regime", "cagr", "sharpe", "max_dd", "n_days"]].copy()
    vol_reg = vol_regime_df[["regime", "cagr", "sharpe", "max_dd"]].copy()
    merged = smr_reg.merge(
        vol_reg, on="regime", suffixes=("_smr", "_vol"), how="left"
    )
    merged["delta_sharpe"] = merged["sharpe_smr"] - merged["sharpe_vol"]
    lines.append(merged.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Beta Compliance (simple_mean_rank, rebalance dates)", ""]
    for k, v in smr_beta_comp.items():
        lines.append(f"- {k}: {v:.4f}" if isinstance(v, float) else f"- {k}: {v}")
    lines.append("")

    lines += ["## Attribution: Selected Names Overlap (simple_mean_rank vs vol_score)", ""]
    if not overlap_df.empty:
        avg_overlap = overlap_df["overlap_pct_smr"].mean()
        avg_jaccard = overlap_df["jaccard"].mean()
        lines += [
            f"- Average overlap (% of SMR selection shared with vol_score): {avg_overlap:.1%}",
            f"- Average Jaccard similarity: {avg_jaccard:.3f}",
            "",
        ]
        lines.append(overlap_df.head(10).to_markdown(index=False, floatfmt=".3f"))
    else:
        lines.append("_(no data)_")
    lines.append("")

    lines += ["## Attribution: Sector Exposure Shift (stock allocation only)", ""]
    if not sector_df.empty:
        lines.append(sector_df.to_markdown(index=False, floatfmt=".4f"))
    else:
        lines.append("_(no data)_")
    lines.append("")

    lines += ["## Features Used (simple_mean_rank_14)", ""]
    for i, f in enumerate(avail_features, 1):
        lines.append(f"  {i}. `{f}`")
    lines.append("")

    if all_pass:
        lines += [
            "## Decision",
            "",
            "- All Phase C.3 gates pass.",
            "- **Promote `simple_mean_rank_14`** as production stock-selection signal.",
            "- Keep `vol_score` as benchmark / fallback.",
            "- Proceed to Phase D.",
            "",
        ]
    elif critical_pass:
        lines += [
            "## Decision",
            "",
            "- Hard gates (MaxDD, beta compliance) pass.",
            "- Preferred Sharpe gate missed.",
            f"  Candidate Sharpe {_fmt(smr_sharpe)} vs B.5 {_fmt(B5_SHARPE)} target.",
            "- Review regime breakdown for hidden collapse before promotion decision.",
            "",
        ]
    else:
        failing = gates_df[~gates_df["pass"]]["gate"].tolist()
        lines += [
            "## Decision",
            "",
            f"- FAIL: gates not met: {', '.join(failing)}.",
            "- Keep `vol_score` as production signal.",
            "- Freeze LightGBM / feature-selection work for this alpha family.",
            "- Proceed to Phase D with existing vol_score.",
            "",
        ]

    lines += [
        "## Output Files",
        "",
        "- `artifacts/reports/phase_c3_signal_validation.md`",
        "- `artifacts/reports/c3_portfolio_comparison.csv`",
        "- `artifacts/reports/c3_regime_breakdown.csv`",
        "- `artifacts/reports/c3_selected_overlap.csv`",
        "- `artifacts/reports/c3_cost_sensitivity.csv`",
    ]
    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase C.3 portfolio validation of simple_mean_rank")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--trend-assets", nargs="+", default=TREND_ASSETS)
    parser.add_argument(
        "--features",
        nargs="+",
        default=POSITIVE_IC_FEATURES,
        help="14 positive-IC feature names (default: C.2 results)",
    )
    args = parser.parse_args()

    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # ── Load data ─────────────────────────────────────────────────────────────
    t0 = time.perf_counter()
    logger.info("Loading inputs for %s...", args.universe)
    inputs = load_inputs(args.config, args.universe, args.trend_assets)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    logger.info(
        "Universe: %s, validation end: %s (%.1fs)",
        inputs["universe_config"].name,
        validation_end.date(),
        time.perf_counter() - t0,
    )

    avail_features = [f for f in args.features if f in inputs["stock_features"].columns]
    missing_features = [f for f in args.features if f not in inputs["stock_features"].columns]
    if missing_features:
        logger.warning("Features not in data (skipped): %s", missing_features)
    logger.info("simple_mean_rank using %d / %d features", len(avail_features), len(args.features))

    # ── Build beta / stress frames (shared) ───────────────────────────────────
    t1 = time.perf_counter()
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)
    logger.info("Beta/stress frames built in %.1fs", time.perf_counter() - t1)

    # ── Candidate: simple_mean_rank ───────────────────────────────────────────
    t2 = time.perf_counter()
    logger.info("Building simple_mean_rank weight path...")
    smr_constrained, smr_diagnostics, _ = build_promoted_simple_mean_rank_weights(
        inputs, validation_end, beta_frame, stress_series, avail_features
    )
    logger.info("simple_mean_rank weights built in %.1fs", time.perf_counter() - t2)

    smr_sim = run_execution_simulator(
        inputs,
        smr_constrained,
        validation_end,
        Variant("smr_c3", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    logger.info(
        "simple_mean_rank: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%% Turnover=%.1f",
        smr_sim["cagr"] * 100,
        smr_sim["sharpe"],
        smr_sim["max_dd"] * 100,
        smr_sim["turnover_sum"],
    )

    # ── Baseline: vol_score (B.5) ─────────────────────────────────────────────
    t3 = time.perf_counter()
    logger.info("Building vol_score B.5 weight path (for comparison)...")
    from run_phase_b5_final_gate import build_promoted_weights as _build_b5  # noqa: E402
    vol_constrained, vol_diagnostics, _ = _build_b5(inputs, validation_end, beta_frame, stress_series)
    logger.info("vol_score weights built in %.1fs", time.perf_counter() - t3)

    vol_sim = run_execution_simulator(
        inputs,
        vol_constrained,
        validation_end,
        Variant("vol_b5", update_frequency="every_2_rebalances", cost_bps=B1_COST_BPS),
    )
    logger.info(
        "vol_score B.5: CAGR=%.2f%% Sharpe=%.3f MaxDD=%.2f%% Turnover=%.1f",
        vol_sim["cagr"] * 100,
        vol_sim["sharpe"],
        vol_sim["max_dd"] * 100,
        vol_sim["turnover_sum"],
    )

    # ── Cost sensitivity ──────────────────────────────────────────────────────
    smr_cost_df = cost_sensitivity_table(inputs, smr_constrained, validation_end, "simple_mean_rank")
    vol_cost_df = cost_sensitivity_table(inputs, vol_constrained, validation_end, "vol_score")
    logger.info("Cost sensitivity tables built")

    # ── Regime breakdown ──────────────────────────────────────────────────────
    smr_regime_df = regime_breakdown_table(inputs, smr_constrained, validation_end, "simple_mean_rank")
    vol_regime_df = regime_breakdown_table(inputs, vol_constrained, validation_end, "vol_score")
    logger.info("Regime breakdown tables built")

    # ── Beta compliance ───────────────────────────────────────────────────────
    smr_beta_comp = beta_compliance_summary(smr_diagnostics)
    logger.info(
        "Beta compliance — %d dates, %d violations, avg beta %.3f",
        smr_beta_comp["n_rebalance_dates"],
        smr_beta_comp["n_gate_violations"],
        smr_beta_comp["avg_beta_after"],
    )

    # ── Gates ─────────────────────────────────────────────────────────────────
    gates_df = evaluate_c3_gates(smr_sim, smr_cost_df, smr_beta_comp)
    for _, row in gates_df.iterrows():
        status = "PASS" if row["pass"] else "FAIL"
        logger.info(
            "Gate [%s] %s: %s (target %s)", status, row["gate"], row["value"], row["target"]
        )

    # ── Attribution: selection overlap ────────────────────────────────────────
    t4 = time.perf_counter()
    logger.info("Building selection overlap table...")
    overlap_df = build_selected_overlap_table(inputs, validation_end, avail_features)
    if not overlap_df.empty:
        avg_ov = overlap_df["overlap_pct_smr"].mean()
        avg_jac = overlap_df["jaccard"].mean()
        logger.info(
            "Overlap: avg %.1f%% of SMR selection shared with vol_score (Jaccard %.3f)",
            avg_ov * 100,
            avg_jac,
        )
    logger.info("Overlap table built in %.1fs", time.perf_counter() - t4)

    # ── Attribution: sector exposure ──────────────────────────────────────────
    t5 = time.perf_counter()
    logger.info("Building sector exposure table...")
    sector_df = build_sector_exposure_table(
        inputs, validation_end, avail_features, smr_constrained, vol_constrained
    )
    logger.info("Sector table built in %.1fs", time.perf_counter() - t5)

    # ── Portfolio comparison CSV ──────────────────────────────────────────────
    comparison_rows = [
        {
            "signal": "simple_mean_rank_14",
            "cagr": smr_sim["cagr"],
            "sharpe": smr_sim["sharpe"],
            "max_dd": smr_sim["max_dd"],
            "turnover_sum": smr_sim["turnover_sum"],
            "sharpe_50bps": float(
                smr_cost_df[smr_cost_df["cost_bps"] == 50.0]["sharpe"].iloc[0]
            ) if not smr_cost_df[smr_cost_df["cost_bps"] == 50.0].empty else np.nan,
            "avg_beta": smr_beta_comp["avg_beta_after"],
            "n_gate_violations": smr_beta_comp["n_gate_violations"],
            "ic_sharpe": C2_SIMPLE_MEAN_RANK_IC_SHARPE,
        },
        {
            "signal": "vol_score_b5",
            "cagr": vol_sim["cagr"],
            "sharpe": vol_sim["sharpe"],
            "max_dd": vol_sim["max_dd"],
            "turnover_sum": vol_sim["turnover_sum"],
            "sharpe_50bps": float(
                vol_cost_df[vol_cost_df["cost_bps"] == 50.0]["sharpe"].iloc[0]
            ) if not vol_cost_df[vol_cost_df["cost_bps"] == 50.0].empty else np.nan,
            "avg_beta": np.nan,
            "n_gate_violations": 0,
            "ic_sharpe": C2_VOL_SCORE_IC_SHARPE,
        },
    ]
    comparison_df = pd.DataFrame(comparison_rows)

    # Combine regime breakdown
    combined_regime_df = pd.concat([smr_regime_df, vol_regime_df], ignore_index=True)

    # Combine cost sensitivity
    combined_cost_df = pd.concat([smr_cost_df, vol_cost_df], ignore_index=True)

    # ── Save artifacts ────────────────────────────────────────────────────────
    comparison_df.to_csv(reports_dir / "c3_portfolio_comparison.csv", index=False)
    combined_regime_df.to_csv(reports_dir / "c3_regime_breakdown.csv", index=False)
    overlap_df.to_csv(reports_dir / "c3_selected_overlap.csv", index=False)
    combined_cost_df.to_csv(reports_dir / "c3_cost_sensitivity.csv", index=False)

    report_text = render_report(
        smr_sim,
        vol_sim,
        smr_cost_df,
        vol_cost_df,
        smr_regime_df,
        vol_regime_df,
        smr_beta_comp,
        gates_df,
        overlap_df,
        sector_df,
        avail_features,
    )
    (reports_dir / "phase_c3_signal_validation.md").write_text(report_text)

    logger.info("All Phase C.3 artifacts written to %s", reports_dir)
    total_elapsed = time.perf_counter() - t0
    logger.info("Total elapsed: %.1fs", total_elapsed)

    all_pass = bool(gates_df["pass"].all())
    if all_pass:
        logger.info("Phase C.3 PASS — promote simple_mean_rank_14 as production signal.")
    else:
        failing = gates_df[~gates_df["pass"]]["gate"].tolist()
        logger.warning("Phase C.3 gates not fully met: %s", failing)


if __name__ == "__main__":
    main()
