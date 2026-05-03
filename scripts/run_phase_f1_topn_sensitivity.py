"""Phase F.1 — Top-N sensitivity under E.7 RL.

Step F.1a: Run E.7 RL policy (no retraining) on:
  - Top-10 (diagnostic)
  - Top-15
  - Top-20 (E.7 baseline)
  - Top-30

Evaluate: CAGR, Sharpe, MaxDD, 50 bps Sharpe, avg equity, turnover,
          beta/gross violations, regime breakdown, sector concentration.

Step F.1b: Flag for retraining only if Top-15 or Top-30 beats Top-20 materially.

Promotion gate (any non-20 Top-N):
  - Sharpe >= 1.270
  - MaxDD >= -27%
  - CAGR > E.7 (17.79%)
  - beats random p75 (1.280, from E.7 evaluation)
  - 50 bps Sharpe >= 1.0

Outputs:
  artifacts/reports/phase_f1_topn_sensitivity.md
  artifacts/reports/f1_topn_comparison.csv
  artifacts/reports/f1_regime_breakdown.csv
  artifacts/reports/f1_sector_concentration.csv

Usage:
    .venv/bin/python scripts/run_phase_f1_topn_sensitivity.py
    .venv/bin/python scripts/run_phase_f1_topn_sensitivity.py --random-seeds 10
    .venv/bin/python scripts/run_phase_f1_topn_sensitivity.py --top-n 20 30
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
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_phase_a7_1_drawdown_control import TREND_NAME, stress_frame
from run_phase_a7_2_robustness import stress_variant_frame, weight_frame
from run_phase_a7_trend_overlay import (
    TREND_ASSETS,
    build_trend_weight_paths,
    equal_weights,
    load_inputs,
    rebalance_dates,
)
from run_phase_b1_simulator_reproduction import (
    CANDIDATE_BASE_TREND_WEIGHT,
    CANDIDATE_STRESS_K,
    CANDIDATE_TREND_CAP,
    clipped_evaluation_dates,
    recommended_end_for_universe,
)
from run_phase_b2_turnover_control import (
    B1_COST_BPS,
    COST_BPS,
    active_mask_frame,
    apply_execution_controls,
    combine_candidate_weights,
    signal_dates_for_frequency,
    volatility_score_matrix,
)
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import (
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
from run_phase_b5_final_gate import compute_net_returns
from run_rl_backtest_v2 import (
    HOLDOUT_END,
    HOLDOUT_REGIMES,
    HOLDOUT_START,
    _cost_adjusted_metrics,
    _run_env_policy_v2,
)
from src.reporting.metrics import calculate_metrics
from src.rl.environment_v2 import PortfolioEnvV2
from src.rl.exposure_mix import _CA_MAX, _CA_MIN, _EQ_MAX, _EQ_MIN, _TR_MAX, _TR_MIN

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# E.7 promoted baseline metrics (holdout 2019-01-01 → 2026-04-24, 10 bps)
E7_SHARPE = 1.296
E7_MAXDD = -0.2448
E7_CAGR = 0.1779
E7_RANDOM_P75 = 1.280

# Promotion gates for any non-20 Top-N
GATE_SHARPE = 1.270
GATE_MAXDD = -0.27          # MaxDD must be >= -27%
GATE_CAGR_GT_E7 = E7_CAGR
GATE_RANDOM_P75 = E7_RANDOM_P75
GATE_50BPS_SHARPE = 1.0

# Material improvement threshold for F.1b retraining recommendation
MATERIAL_SHARPE_DELTA = 0.010   # >= +0.01 Sharpe vs Top-20 to flag retrain
MATERIAL_CAGR_DELTA = 0.005     # >= +0.5pp CAGR vs Top-20

DEFAULT_TOP_N_LIST = [10, 15, 20, 30]
DEFAULT_RANDOM_SEEDS = 20

B5_VARIANT = B4Variant(
    name="b4_stress_cap_trend_boost",
    beta_min=BETA_MIN,
    beta_max_base=BETA_MAX_BASE,
    beta_max_sensitivity=BETA_MAX_SENSITIVITY,
    trend_stress_boost=True,
    trend_stress_threshold=TREND_STRESS_THRESHOLD,
    trend_stress_scale_max=TREND_STRESS_SCALE_MAX,
)


# ---------------------------------------------------------------------------
# Top-N parameterized weight builders
# ---------------------------------------------------------------------------

def build_vol_path_topn(inputs: dict, top_n: int) -> dict:
    """Like build_vol_path_fast but with configurable Top-N (no persistence)."""
    weights_by_date: dict = {}
    selected_by_date: dict = {}
    dates = rebalance_dates(inputs["base_config"], inputs["prices"])
    scores_by_date = volatility_score_matrix(inputs).reindex(dates, method="ffill")
    active = active_mask_frame(inputs, dates, scores_by_date.columns)
    for date in dates:
        scores = scores_by_date.loc[date].where(active.loc[date]).dropna()
        ranked = scores.sort_values(ascending=False)
        selected = ranked.head(top_n).index.tolist()
        weights_by_date[date] = equal_weights(selected)
        selected_by_date[date] = selected
    return {"weights": weights_by_date, "selected": selected_by_date, "sleeve_type": "volatility"}


def build_b2_candidate_topn(
    inputs: dict,
    validation_end: pd.Timestamp,
    top_n: int,
) -> pd.DataFrame:
    """Like build_b2_candidate but with Top-N equity sleeve."""
    dates = clipped_evaluation_dates(inputs, validation_end)
    trend_path = build_trend_weight_paths(inputs, target_vol=0.10, gross_cap=1.5, vol_window=63)[TREND_NAME]
    base_stress = stress_frame(
        inputs["prices"],
        vix_col=inputs["universe_config"].vix_proxy,
        spy_col=inputs["universe_config"].benchmark,
    )
    stress = stress_variant_frame(base_stress, "weighted_50_50", 0.5, 0.5)
    raw = combine_candidate_weights(
        dates,
        build_vol_path_topn(inputs, top_n),
        trend_path,
        stress,
    )
    signal_dates = signal_dates_for_frequency(inputs, raw, validation_end, "every_2_rebalances")
    return apply_execution_controls(raw, signal_dates, trade_threshold=0.0, partial_rebalance=1.0)


def build_promoted_weights_topn(
    inputs: dict,
    validation_end: pd.Timestamp,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    top_n: int,
) -> tuple[pd.DataFrame, pd.DataFrame, list]:
    """Like build_promoted_weights but with Top-N equity sleeve."""
    base_weights = build_b2_candidate_topn(inputs, validation_end, top_n)
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
        B5_VARIANT.trend_stress_threshold,
        B5_VARIANT.trend_stress_scale_max,
    )
    constrained, diagnostics = apply_b4_constraints(
        scaled,
        beta_frame,
        stress_series,
        B5_VARIANT,
        control_dates,
        inputs["universe_config"].benchmark,
    )
    return constrained, diagnostics, control_dates


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def _metrics_window(net_returns: pd.Series, start: str, end: str) -> dict:
    mask = (net_returns.index >= pd.Timestamp(start)) & (net_returns.index <= pd.Timestamp(end))
    sliced = net_returns[mask]
    if len(sliced) < 21:
        return {"cagr": np.nan, "sharpe": np.nan, "max_dd": np.nan, "n_days": len(sliced)}
    nav = (1.0 + sliced).cumprod()
    m = calculate_metrics(nav)
    return {
        "cagr":   m.get("CAGR", np.nan),
        "sharpe": m.get("Sharpe", np.nan),
        "max_dd": m.get("Max Drawdown", np.nan),
        "n_days": len(sliced),
    }


def _beta_gross_violations(diagnostics: pd.DataFrame) -> dict:
    ctrl = (
        diagnostics[diagnostics["is_control_date"]].copy()
        if "is_control_date" in diagnostics.columns
        else diagnostics
    )
    n_total = len(ctrl)
    n_beta_viol = int(ctrl["gate_violation_after"].sum()) if "gate_violation_after" in ctrl.columns else 0
    max_gross_val = float(ctrl["gross_after"].max()) if "gross_after" in ctrl.columns else np.nan
    return {
        "n_rebalances": n_total,
        "beta_violations": n_beta_viol,
        "max_gross": max_gross_val,
    }


# ---------------------------------------------------------------------------
# Sector concentration from weights
# ---------------------------------------------------------------------------

def compute_sector_concentration(
    weights_df: pd.DataFrame,
    ticker_to_sector: dict[str, str],
    trend_tickers: list[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Compute average sector weight in the EQUITY sleeve only over holdout window."""
    mask = (weights_df.index >= pd.Timestamp(start)) & (weights_df.index <= pd.Timestamp(end))
    w = weights_df[mask].copy()
    if w.empty:
        return pd.DataFrame()

    eq_cols = [c for c in w.columns if c not in trend_tickers and c != "CASH"]
    w_eq = w[eq_cols].copy()

    # Normalize to equity sleeve (so sector weights sum to 1 per date)
    row_sum = w_eq.abs().sum(axis=1).replace(0, np.nan)
    w_eq_norm = w_eq.div(row_sum, axis=0).fillna(0.0)

    rows = []
    for ticker in eq_cols:
        sector = ticker_to_sector.get(ticker, "Unknown")
        rows.append({"ticker": ticker, "sector": sector, "avg_weight": float(w_eq_norm[ticker].mean())})

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    sector_df = (
        df.groupby("sector")["avg_weight"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"avg_weight": "avg_equity_weight"})
    )
    return sector_df


# ---------------------------------------------------------------------------
# Run a single Top-N variant
# ---------------------------------------------------------------------------

def run_topn_variant(
    inputs: dict,
    beta_frame: pd.DataFrame,
    stress_series: pd.Series,
    validation_end: pd.Timestamp,
    sector_features_df: pd.DataFrame,
    model_path: Path,
    top_n: int,
    n_random_seeds: int,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Run E.7 RL policy and B.5 no-RL baseline for a given Top-N equity sleeve."""
    logger.info("=== Top-%d: building promoted weights ===", top_n)
    weights_df, diagnostics, control_dates = build_promoted_weights_topn(
        inputs, validation_end, beta_frame, stress_series, top_n
    )
    logger.info("Top-%d: weights built, %d control dates", top_n, len(control_dates))

    viol_info = _beta_gross_violations(diagnostics)

    # ── B.5 no-RL (locked) baseline ─────────────────────────────────────
    net_ret_b5 = compute_net_returns(inputs, weights_df, validation_end, primary_cost_bps)
    m_b5 = _metrics_window(net_ret_b5, HOLDOUT_START, HOLDOUT_END)

    # Compute turnover for the B.5 baseline (in holdout window)
    dates_in_holdout = weights_df.index[
        (weights_df.index >= pd.Timestamp(HOLDOUT_START))
        & (weights_df.index <= pd.Timestamp(HOLDOUT_END))
    ]
    executable = weights_df.shift(1).reindex(dates_in_holdout).fillna(0.0)
    turnover_sum_b5 = float(executable.diff().abs().sum(axis=1).sum())

    # ── Trained E.7 RL ──────────────────────────────────────────────────
    rl_result: dict | None = None
    if model_path.exists():
        try:
            from stable_baselines3 import PPO
            model = PPO.load(str(model_path))
            env = PortfolioEnvV2(
                inputs, weights_df,
                start_date=HOLDOUT_START, end_date=HOLDOUT_END,
                rebalance_dates=control_dates, cost_bps=0.0,
                sector_features_df=sector_features_df,
            )

            def action_fn(obs, _model=model):
                action, _ = _model.predict(obs, deterministic=True)
                return action

            raw_ret, daily_to, eq_f, tr_f, ca_f = _run_env_policy_v2(env, action_fn, f"E7RL-top{top_n}")
            m_rl = _cost_adjusted_metrics(raw_ret, daily_to, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)

            # 50 bps Sharpe
            m_50 = _cost_adjusted_metrics(raw_ret, daily_to, 50.0, HOLDOUT_START, HOLDOUT_END)

            # Turnover
            turnover_sum_rl = float(daily_to.sum())

            rl_result = {
                "cagr":         m_rl["cagr"],
                "sharpe":       m_rl["sharpe"],
                "max_dd":       m_rl["max_dd"],
                "sharpe_50bps": m_50["sharpe"],
                "avg_equity":   float(np.nanmean(eq_f)) if eq_f else np.nan,
                "avg_trend":    float(np.nanmean(tr_f)) if tr_f else np.nan,
                "avg_cash":     float(np.nanmean(ca_f)) if ca_f else np.nan,
                "turnover_sum": turnover_sum_rl,
                "raw_returns":  raw_ret,
                "daily_turnover": daily_to,
            }
            logger.info(
                "Top-%d RL: Sharpe=%.3f MaxDD=%.2f%% CAGR=%.2f%% avgEQ=%.3f",
                top_n, m_rl["sharpe"], m_rl["max_dd"] * 100, m_rl["cagr"] * 100,
                float(np.nanmean(eq_f)) if eq_f else float("nan"),
            )
        except Exception as exc:
            logger.warning("Top-%d RL failed: %s", top_n, exc)

    # ── Random baseline ──────────────────────────────────────────────────
    rand_sharpes = []
    for seed in range(n_random_seeds):
        rng = np.random.default_rng(seed)
        env = PortfolioEnvV2(
            inputs, weights_df,
            start_date=HOLDOUT_START, end_date=HOLDOUT_END,
            rebalance_dates=control_dates, cost_bps=0.0,
            sector_features_df=sector_features_df,
        )

        def _rand_action(_obs, _rng=rng):
            return _rng.uniform(-1.0, 1.0, 3).astype(np.float32)

        raw_r, daily_t, _, _, _ = _run_env_policy_v2(env, _rand_action, f"rand-top{top_n}-s{seed}")
        m_r = _cost_adjusted_metrics(raw_r, daily_t, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
        rand_sharpes.append(m_r["sharpe"])
        logger.info("Top-%d random seed %d/%d: Sharpe=%.3f", top_n, seed + 1, n_random_seeds, m_r["sharpe"] if np.isfinite(m_r["sharpe"]) else float("nan"))

    valid_rand = [s for s in rand_sharpes if np.isfinite(s)]
    rand_median = float(np.nanpercentile(valid_rand, 50)) if valid_rand else np.nan
    rand_p75    = float(np.nanpercentile(valid_rand, 75)) if valid_rand else np.nan

    # ── Sector concentration ─────────────────────────────────────────────
    ticker_to_sector: dict[str, str] = dict(inputs["universe_config"].tickers)
    trend_tickers = [t for t in _NON_BENCHMARK_TREND if t in weights_df.columns]
    sector_df = compute_sector_concentration(
        weights_df, ticker_to_sector, trend_tickers, HOLDOUT_START, HOLDOUT_END
    )
    sector_df["top_n"] = top_n

    # ── Regime breakdown ─────────────────────────────────────────────────
    regime_rows = []
    if rl_result is not None:
        raw_ret_rl = rl_result["raw_returns"]
        to_rl = rl_result["daily_turnover"]
        for name, start, end in HOLDOUT_REGIMES:
            m = _cost_adjusted_metrics(raw_ret_rl, to_rl, primary_cost_bps, start, end)
            regime_rows.append({
                "top_n": top_n, "regime": name,
                "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"],
            })

    return {
        "top_n": top_n,
        # B.5 no-RL
        "b5_cagr":    m_b5["cagr"],
        "b5_sharpe":  m_b5["sharpe"],
        "b5_max_dd":  m_b5["max_dd"],
        "b5_turnover": turnover_sum_b5,
        # RL
        "rl_cagr":         rl_result["cagr"]         if rl_result else np.nan,
        "rl_sharpe":       rl_result["sharpe"]       if rl_result else np.nan,
        "rl_max_dd":       rl_result["max_dd"]       if rl_result else np.nan,
        "rl_sharpe_50bps": rl_result["sharpe_50bps"] if rl_result else np.nan,
        "rl_avg_equity":   rl_result["avg_equity"]   if rl_result else np.nan,
        "rl_avg_trend":    rl_result["avg_trend"]    if rl_result else np.nan,
        "rl_avg_cash":     rl_result["avg_cash"]     if rl_result else np.nan,
        "rl_turnover":     rl_result["turnover_sum"] if rl_result else np.nan,
        # beta/gross
        "beta_violations": viol_info["beta_violations"],
        "max_gross":       viol_info["max_gross"],
        "n_rebalances":    viol_info["n_rebalances"],
        # random
        "rand_median":     rand_median,
        "rand_p75":        rand_p75,
        # sub-dfs
        "_sector_df":      sector_df,
        "_regime_rows":    regime_rows,
    }


# ---------------------------------------------------------------------------
# Promotion gate evaluator
# ---------------------------------------------------------------------------

def evaluate_promotion(result: dict, baseline_top20: dict | None) -> dict:
    """Check F.1 promotion gates for a given Top-N result vs E.7 and Top-20."""
    s = result["rl_sharpe"]
    dd = result["rl_max_dd"]
    cagr = result["rl_cagr"]
    s50 = result["rl_sharpe_50bps"]
    rp75 = result["rand_p75"]

    def _fp(v): return f"{v:.3f}" if np.isfinite(v) else "N/A"

    g_sharpe  = bool(np.isfinite(s)    and s    >= GATE_SHARPE)
    g_maxdd   = bool(np.isfinite(dd)   and dd   >= GATE_MAXDD)
    g_cagr    = bool(np.isfinite(cagr) and cagr >  GATE_CAGR_GT_E7)
    g_50bps   = bool(np.isfinite(s50)  and s50  >= GATE_50BPS_SHARPE)
    g_rand_p75 = bool(np.isfinite(s) and np.isfinite(rp75) and s > rp75)

    all_pass = g_sharpe and g_maxdd and g_cagr and g_50bps and g_rand_p75

    material_vs_20 = False
    if baseline_top20 is not None:
        s20   = baseline_top20["rl_sharpe"]
        cagr20 = baseline_top20["rl_cagr"]
        material_vs_20 = (
            (np.isfinite(s) and np.isfinite(s20) and s - s20 >= MATERIAL_SHARPE_DELTA)
            or (np.isfinite(cagr) and np.isfinite(cagr20) and cagr - cagr20 >= MATERIAL_CAGR_DELTA)
        )

    verdict = "PROMOTE" if all_pass else "REJECT"
    retrain_flag = all_pass and material_vs_20

    return {
        "top_n": result["top_n"],
        "verdict": verdict,
        "all_gates_pass": all_pass,
        "retrain_recommended": retrain_flag,
        "gate_sharpe":   g_sharpe,
        "gate_maxdd":    g_maxdd,
        "gate_cagr":     g_cagr,
        "gate_50bps":    g_50bps,
        "gate_rand_p75": g_rand_p75,
        "material_vs_top20": material_vs_20,
    }


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report(results: list[dict], top20_result: dict, promo_table: pd.DataFrame) -> str:
    lines = [
        "# Phase F.1 — Top-N Sensitivity Under E.7 RL",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Holdout window: {HOLDOUT_START} → {HOLDOUT_END}",
        f"- E.7 baseline (Top-20): Sharpe {E7_SHARPE:.3f}, MaxDD {E7_MAXDD:.2%}, CAGR {E7_CAGR:.2%}",
        f"- E.7 random p75: {E7_RANDOM_P75:.3f}",
        "",
        "## Step F.1a — Top-N Comparison (E.7 RL, 10 bps holdout)",
        "",
    ]

    def _s(v): return f"{v:.3f}" if np.isfinite(v) else "N/A"
    def _p(v): return f"{v:.2%}"  if np.isfinite(v) else "N/A"

    # Main comparison table
    rows = []
    for r in results:
        note = "(baseline)" if r["top_n"] == 20 else ""
        rows.append({
            "Top-N":         f"{r['top_n']} {note}".strip(),
            "CAGR":          _p(r["rl_cagr"]),
            "Sharpe":        _s(r["rl_sharpe"]),
            "MaxDD":         _p(r["rl_max_dd"]),
            "50bps Sharpe":  _s(r["rl_sharpe_50bps"]),
            "Avg equity":    _s(r["rl_avg_equity"]),
            "RL turnover":   f"{r['rl_turnover']:.1f}" if np.isfinite(r["rl_turnover"]) else "N/A",
            "Beta violations": int(r["beta_violations"]),
            "Max gross":     _s(r["max_gross"]),
            "Rand p75":      _s(r["rand_p75"]),
        })
    lines.append(pd.DataFrame(rows).to_markdown(index=False))
    lines.append("")

    # B.5 no-RL rows for reference
    lines += ["### B.5 No-RL Baseline by Top-N (10 bps)", ""]
    rows_b5 = []
    for r in results:
        note = "(baseline)" if r["top_n"] == 20 else ""
        rows_b5.append({
            "Top-N":  f"{r['top_n']} {note}".strip(),
            "CAGR":   _p(r["b5_cagr"]),
            "Sharpe": _s(r["b5_sharpe"]),
            "MaxDD":  _p(r["b5_max_dd"]),
        })
    lines.append(pd.DataFrame(rows_b5).to_markdown(index=False))
    lines.append("")

    # Promotion gates
    lines += ["## Promotion Gate Evaluation (non-Top-20 only)", ""]
    if not promo_table.empty:
        lines.append(promo_table.to_markdown(index=False))
    lines.append("")

    # F.1b recommendation
    lines += ["## Step F.1b — Retrain Recommendation", ""]
    retrain_candidates = promo_table[promo_table["retrain_recommended"] == True]["top_n"].tolist() if not promo_table.empty else []
    if retrain_candidates:
        lines.append(f"**RETRAIN RECOMMENDED** for Top-N = {retrain_candidates}.")
        lines.append(
            "These variants beat Top-20 materially on Sharpe (>= +0.010) or CAGR (>= +0.5pp) "
            "while passing all promotion gates. Proceed to F.1b retraining."
        )
    else:
        lines.append("**No retrain required.** No non-20 Top-N variant beats Top-20 materially "
                     "while passing all promotion gates. Top-20 remains the recommended breadth.")
    lines.append("")

    # Notes
    lines += [
        "## Methodology",
        "",
        "- E.7 RL model used as-is (no retraining). Only the equity sleeve breadth (Top-N) changes.",
        "- Trend sleeve, reward, RL policy, beta constraints: all unchanged from E.7.",
        "- Random baselines re-run per Top-N with fewer seeds for diagnostic use.",
        "- Promotion gates: Sharpe >= 1.270, MaxDD >= -27%, CAGR > E.7 (17.79%), "
          "50bps Sharpe >= 1.0, beats per-variant random p75.",
        "",
        "## Artifacts",
        "",
        "- `artifacts/reports/phase_f1_topn_sensitivity.md` — this file",
        "- `artifacts/reports/f1_topn_comparison.csv`",
        "- `artifacts/reports/f1_regime_breakdown.csv`",
        "- `artifacts/reports/f1_sector_concentration.csv`",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase F.1 — Top-N sensitivity under E.7 RL")
    parser.add_argument("--config",   default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--model-path", default="artifacts/models/rl_e_ppo_best.zip")
    parser.add_argument("--top-n", type=int, nargs="+", default=DEFAULT_TOP_N_LIST,
                        help="Top-N values to test (default: 10 15 20 30)")
    parser.add_argument("--random-seeds", type=int, default=DEFAULT_RANDOM_SEEDS,
                        help="Random seeds per Top-N variant (default: 20)")
    args = parser.parse_args()

    reports_dir = REPO_ROOT / "artifacts" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    model_path = REPO_ROOT / args.model_path

    if not model_path.exists():
        logger.error("Model not found at %s — aborting", model_path)
        sys.exit(1)

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )

    logger.info("Building beta/stress (shared across all Top-N) …")
    beta_frame    = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Loading sector features …")
    sector_features_df = pd.read_parquet(REPO_ROOT / "data" / "features" / "sector_features.parquet")

    top_n_list = sorted(set(args.top_n))
    logger.info("Top-N variants to test: %s", top_n_list)

    all_results = []
    all_regime_rows: list[dict] = []
    all_sector_dfs: list[pd.DataFrame] = []

    for top_n in top_n_list:
        res = run_topn_variant(
            inputs=inputs,
            beta_frame=beta_frame,
            stress_series=stress_series,
            validation_end=validation_end,
            sector_features_df=sector_features_df,
            model_path=model_path,
            top_n=top_n,
            n_random_seeds=args.random_seeds,
            primary_cost_bps=B1_COST_BPS,
        )
        all_results.append(res)
        all_regime_rows.extend(res.pop("_regime_rows", []))
        sector_df = res.pop("_sector_df", pd.DataFrame())
        if not sector_df.empty:
            all_sector_dfs.append(sector_df)

    # ── Promotion gates (skip Top-20 baseline) ──────────────────────────
    top20_result = next((r for r in all_results if r["top_n"] == 20), None)
    promo_rows = []
    for r in all_results:
        if r["top_n"] == 20:
            continue
        pg = evaluate_promotion(r, top20_result)
        promo_rows.append(pg)
    promo_table = pd.DataFrame(promo_rows) if promo_rows else pd.DataFrame()

    # ── Write CSVs ──────────────────────────────────────────────────────
    comparison_rows = []
    for r in all_results:
        comparison_rows.append({
            "top_n":          r["top_n"],
            "rl_cagr":        r["rl_cagr"],
            "rl_sharpe":      r["rl_sharpe"],
            "rl_max_dd":      r["rl_max_dd"],
            "rl_sharpe_50bps": r["rl_sharpe_50bps"],
            "rl_avg_equity":  r["rl_avg_equity"],
            "rl_avg_trend":   r["rl_avg_trend"],
            "rl_avg_cash":    r["rl_avg_cash"],
            "rl_turnover":    r["rl_turnover"],
            "b5_cagr":        r["b5_cagr"],
            "b5_sharpe":      r["b5_sharpe"],
            "b5_max_dd":      r["b5_max_dd"],
            "b5_turnover":    r["b5_turnover"],
            "beta_violations": r["beta_violations"],
            "max_gross":       r["max_gross"],
            "n_rebalances":   r["n_rebalances"],
            "rand_median":    r["rand_median"],
            "rand_p75":       r["rand_p75"],
        })
    comparison_df = pd.DataFrame(comparison_rows)
    comparison_df.to_csv(reports_dir / "f1_topn_comparison.csv", index=False)
    logger.info("Saved f1_topn_comparison.csv")

    if all_regime_rows:
        regime_df = pd.DataFrame(all_regime_rows)
        regime_df.to_csv(reports_dir / "f1_regime_breakdown.csv", index=False)
        logger.info("Saved f1_regime_breakdown.csv")

    if all_sector_dfs:
        sector_concat = pd.concat(all_sector_dfs, ignore_index=True)
        pivot = sector_concat.pivot_table(
            index="sector", columns="top_n", values="avg_equity_weight", aggfunc="first"
        ).reset_index()
        pivot.columns.name = None
        col_rename = {n: f"top_{n}" for n in top_n_list if n in pivot.columns}
        pivot = pivot.rename(columns=col_rename)
        pivot.to_csv(reports_dir / "f1_sector_concentration.csv", index=False)
        logger.info("Saved f1_sector_concentration.csv")

    # ── Render markdown report ───────────────────────────────────────────
    report_md = render_report(all_results, top20_result, promo_table)
    (reports_dir / "phase_f1_topn_sensitivity.md").write_text(report_md, encoding="utf-8")
    logger.info("Report written: phase_f1_topn_sensitivity.md")

    logger.info("Phase F.1 complete in %.1fs", time.perf_counter() - t0)

    # ── Summary to stdout ────────────────────────────────────────────────
    print("\n=== Phase F.1 Summary ===")
    for r in all_results:
        note = " (baseline)" if r["top_n"] == 20 else ""
        print(
            f"  Top-{r['top_n']:2d}{note:10s}: "
            f"RL Sharpe={r['rl_sharpe']:.3f}  MaxDD={r['rl_max_dd']:.2%}  "
            f"CAGR={r['rl_cagr']:.2%}  50bps={r['rl_sharpe_50bps']:.3f}  "
            f"avgEQ={r['rl_avg_equity']:.3f}  randP75={r['rand_p75']:.3f}"
        )

    if not promo_table.empty:
        print("\n=== Promotion Gates ===")
        print(promo_table[["top_n", "verdict", "all_gates_pass", "retrain_recommended"]].to_string(index=False))


if __name__ == "__main__":
    main()
