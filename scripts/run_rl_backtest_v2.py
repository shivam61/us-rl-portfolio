"""Phase E.6 — Five-way comparison on holdout 2019–2026-04-24.

Policies:
  1. B.5 locked           — no RL; vol_score + B.5 harness only
  2. RL no-op             — raw_action=[1,-1,-1] (equity=1, trend=0, cash=0); pass-through
  3. Random bounded       — 50 seeds; uniform raw_action in [−1,+1]^3; reports mean/median/p25/p75/p95
  4. Rule-based           — VIX + SPY drawdown/trend regime table; hard-coded heuristic
  5. Trained Phase E RL   — load artifacts/models/rl_e_ppo_best.zip

Usage:
    # Full five-way comparison:
    .venv/bin/python scripts/run_rl_backtest_v2.py

    # Single-policy smoke tests:
    .venv/bin/python scripts/run_rl_backtest_v2.py --policy b5
    .venv/bin/python scripts/run_rl_backtest_v2.py --policy no_op
    .venv/bin/python scripts/run_rl_backtest_v2.py --policy random --seeds 5
    .venv/bin/python scripts/run_rl_backtest_v2.py --policy rule_based
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

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b2_turnover_control import B1_COST_BPS, COST_BPS
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import build_promoted_weights, compute_net_returns
from src.reporting.metrics import calculate_metrics
from src.rl.environment_v2 import PortfolioEnvV2
from src.rl.exposure_mix import _EQ_MIN, _EQ_MAX, _TR_MIN, _TR_MAX, _CA_MIN, _CA_MAX

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HOLDOUT_START = "2019-01-01"
HOLDOUT_END   = "2026-04-24"
RANDOM_SEEDS  = 50

HOLDOUT_REGIMES = [
    ("2019 bull market",    "2019-01-01", "2019-12-31"),
    ("2020 COVID crash",    "2020-01-01", "2020-12-31"),
    ("2021 recovery",       "2021-01-01", "2021-12-31"),
    ("2022 bear market",    "2022-01-01", "2022-12-31"),
    ("2023–2026 recovery",  "2023-01-01", "2026-04-24"),
]

# B.5 holdout benchmark (from phase_d0_holdout_baseline.md)
D0_HOLDOUT_SHARPE       = 1.270
D0_HOLDOUT_MAXDD        = -0.3298
D0_HOLDOUT_50BPS_SHARPE = 1.135

GATE_PATH_A_SHARPE = D0_HOLDOUT_SHARPE
GATE_PATH_A_MAXDD  = D0_HOLDOUT_MAXDD
GATE_PATH_B_SHARPE = D0_HOLDOUT_SHARPE - 0.03
GATE_PATH_B_MAXDD  = D0_HOLDOUT_MAXDD + 0.015
GATE_50BPS_SHARPE  = 0.90
GATE_HARD_MAXDD    = -0.35


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


def _cost_adjusted_metrics(
    raw_returns: pd.Series,
    daily_turnover: pd.Series,
    cost_bps: float,
    start: str,
    end: str,
) -> dict:
    aligned = daily_turnover.reindex(raw_returns.index).fillna(0.0)
    adj = (1.0 - aligned * cost_bps / 10_000.0).clip(lower=0.0) * (1.0 + raw_returns) - 1.0
    return _metrics_window(adj, start, end)


def _cost_sensitivity(
    raw_returns: pd.Series,
    daily_turnover: pd.Series,
    cost_bps_list: list = COST_BPS,
) -> pd.DataFrame:
    rows = []
    for bps in cost_bps_list:
        m = _cost_adjusted_metrics(raw_returns, daily_turnover, bps, HOLDOUT_START, HOLDOUT_END)
        rows.append({"cost_bps": bps, "cagr": m["cagr"], "sharpe": m["sharpe"], "max_dd": m["max_dd"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Policy runners
# ---------------------------------------------------------------------------

def run_b5_locked(inputs: dict, b5_weights_df: pd.DataFrame, validation_end: pd.Timestamp) -> dict:
    """B.5 locked — no RL."""
    net_ret = compute_net_returns(inputs, b5_weights_df, validation_end, B1_COST_BPS)
    m = _metrics_window(net_ret, HOLDOUT_START, HOLDOUT_END)
    cost_rows = []
    for bps in COST_BPS:
        nr = compute_net_returns(inputs, b5_weights_df, validation_end, bps)
        cm = _metrics_window(nr, HOLDOUT_START, HOLDOUT_END)
        cost_rows.append({"cost_bps": bps, "sharpe": cm["sharpe"]})
    return {
        "policy": "B.5 locked",
        "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"],
        "cost_rows": cost_rows,
        "avg_equity_frac": np.nan,
        "net_returns": net_ret,
    }


def _run_env_policy_v2(
    env: PortfolioEnvV2,
    action_fn,
    label: str,
) -> tuple[pd.Series, pd.Series, list, list, list]:
    """Run a policy on env; return (daily_returns, daily_turnover, equity_fracs, trend_fracs, cash_fracs).

    Env must be constructed with cost_bps=0; costs applied post-hoc.
    """
    obs, _ = env.reset()
    done = False
    ep_equity, ep_trend, ep_cash = [], [], []
    step_turnover: dict[pd.Timestamp, float] = {}

    while not done:
        action = action_fn(obs)
        obs, _reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        ep_equity.append(float(info.get("equity_frac", np.nan)))
        ep_trend.append(float(info.get("trend_frac", np.nan)))
        ep_cash.append(float(info.get("cash_frac", np.nan)))

        current_dt = pd.Timestamp(info["date"])
        prices_idx = env.prices.index
        first_day_idx = prices_idx.searchsorted(current_dt, side="right")
        if first_day_idx < len(prices_idx):
            step_turnover[prices_idx[first_day_idx]] = info["turnover"]

    nav = env._nav_series
    daily_returns = nav.pct_change().dropna()
    daily_turnover = pd.Series(0.0, index=daily_returns.index)
    for d, to in step_turnover.items():
        if d in daily_turnover.index:
            daily_turnover[d] = to

    return daily_returns, daily_turnover, ep_equity, ep_trend, ep_cash


def run_noop_policy_v2(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """RL no-op: raw_action=[1,-1,-1] → equity≈1, trend≈0, cash≈0.

    Note: Phase E no-op removes the trend sleeve entirely (unlike B.5 locked which
    has TLT/GLD/UUP). Expected Sharpe will differ from B.5 locked. This is by design.
    """
    env = PortfolioEnvV2(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START, end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates, cost_bps=0.0,
        sector_features_df=sector_features_df,
    )
    noop_action = np.array([1.0, -1.0, -1.0], dtype=np.float32)

    def action_fn(_obs):
        return noop_action

    raw_ret, daily_to, eq_f, tr_f, ca_f = _run_env_policy_v2(env, action_fn, "RL no-op v2")
    m = _cost_adjusted_metrics(raw_ret, daily_to, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
    cost_df = _cost_sensitivity(raw_ret, daily_to)
    return {
        "policy": "RL no-op",
        "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"],
        "avg_equity_frac": float(np.nanmean(eq_f)) if eq_f else np.nan,
        "avg_trend_frac":  float(np.nanmean(tr_f)) if tr_f else np.nan,
        "avg_cash_frac":   float(np.nanmean(ca_f)) if ca_f else np.nan,
        "raw_returns": raw_ret, "daily_turnover": daily_to, "cost_sensitivity": cost_df,
    }


def run_random_policy_v2(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    n_seeds: int = RANDOM_SEEDS,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Random bounded: uniform raw_action in [−1,+1]^3 per step, 50 seeds.

    Reports: mean, median, p25, p75, p95. Promotion gates use MEDIAN (harder bar than mean).
    """
    all_sharpes, all_cagrs, all_maxdds = [], [], []
    all_cost_dfs, all_seed_records = [], []

    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        env = PortfolioEnvV2(
            inputs, b5_weights_df,
            start_date=HOLDOUT_START, end_date=HOLDOUT_END,
            rebalance_dates=rebalance_dates, cost_bps=0.0,
            sector_features_df=sector_features_df,
        )

        def action_fn(_obs, _rng=rng):
            return _rng.uniform(-1.0, 1.0, 3).astype(np.float32)

        raw_ret, daily_to, _, _, _ = _run_env_policy_v2(env, action_fn, f"random-{seed}")
        m = _cost_adjusted_metrics(raw_ret, daily_to, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
        all_sharpes.append(m["sharpe"])
        all_cagrs.append(m["cagr"])
        all_maxdds.append(m["max_dd"])
        all_cost_dfs.append(_cost_sensitivity(raw_ret, daily_to))
        all_seed_records.append({"seed": seed, "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"]})
        logger.info("Random seed %d/%d: Sharpe=%.3f", seed + 1, n_seeds, m["sharpe"] if np.isfinite(m["sharpe"]) else -99)

    valid_sharpes = [s for s in all_sharpes if np.isfinite(s)]
    if valid_sharpes:
        pcts = np.nanpercentile(valid_sharpes, [25, 50, 75, 90, 95])
    else:
        pcts = [np.nan] * 5

    cost_df = pd.concat(all_cost_dfs).groupby("cost_bps").mean().reset_index() if all_cost_dfs else pd.DataFrame()

    return {
        "policy": f"Random bounded ({n_seeds} seeds)",
        "sharpe":         float(np.nanmean(all_sharpes)),      # mean (for display)
        "sharpe_median":  float(pcts[1]),                       # MEDIAN — used in promotion gates
        "sharpe_p25":     float(pcts[0]),
        "sharpe_p75":     float(pcts[2]),
        "sharpe_p90":     float(pcts[3]),
        "sharpe_p95":     float(pcts[4]),
        "sharpe_std":     float(np.nanstd(valid_sharpes)) if valid_sharpes else np.nan,
        "cagr":   float(np.nanmean(all_cagrs)),
        "max_dd": float(np.nanmean(all_maxdds)),
        "avg_equity_frac": np.nan,
        "cost_sensitivity": cost_df,
        "seed_records": all_seed_records,
    }


def _targets_to_raw_action(eq: float, tr: float, ca: float) -> np.ndarray:
    """Reverse-map target proportions to raw actions in [−1,+1]^3.

    Inverts the Step 1 box-mapping in apply_exposure_mix:
        prop = min + (max - min) * (raw + 1) / 2
        ⟹  raw = 2 * (prop - min) / (max - min) - 1
    """
    raw_eq = 2.0 * (eq - _EQ_MIN) / (_EQ_MAX - _EQ_MIN) - 1.0
    raw_tr = 2.0 * (tr - _TR_MIN) / (_TR_MAX - _TR_MIN) - 1.0
    raw_ca = 2.0 * (ca - _CA_MIN) / (_CA_MAX - _CA_MIN) - 1.0
    return np.array([raw_eq, raw_tr, raw_ca], dtype=np.float32)


def run_rule_based_policy_v2(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Rule-based VIX + SPY regime controller.

    Regime table:
        Tier 1 (high stress):    vix_pct > 0.75 OR spy_drawdown < -0.15
          → equity=0.50, trend=0.40, cash=0.10
        Tier 2 (moderate stress): vix_pct > 0.50 OR spy_3m_ret < 0
          → equity=0.70, trend=0.20, cash=0.10
        Benign:
          → equity=0.85, trend=0.10, cash=0.05

    Signal sources (42-dim state vector indices):
        obs[0]  = vix_percentile_1y
        obs[1]  = spy_drawdown_from_peak  (negative; < −0.15 means deep drawdown)
        obs[2]  = spy_ret_3m              (negative means SPY in 3m downtrend)
    """
    env = PortfolioEnvV2(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START, end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates, cost_bps=0.0,
        sector_features_df=sector_features_df,
    )

    def action_fn(obs):
        vix_pct    = float(obs[0])
        spy_dd     = float(obs[1])   # ≤ 0
        spy_ret_3m = float(obs[2])

        if vix_pct > 0.75 or spy_dd < -0.15:
            eq, tr, ca = 0.50, 0.40, 0.10
        elif vix_pct > 0.50 or spy_ret_3m < 0.0:
            eq, tr, ca = 0.70, 0.20, 0.10
        else:
            eq, tr, ca = 0.85, 0.10, 0.05

        return _targets_to_raw_action(eq, tr, ca)

    raw_ret, daily_to, eq_f, tr_f, ca_f = _run_env_policy_v2(env, action_fn, "Rule-based")
    m = _cost_adjusted_metrics(raw_ret, daily_to, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
    cost_df = _cost_sensitivity(raw_ret, daily_to)
    return {
        "policy": "Rule-based controller",
        "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"],
        "avg_equity_frac": float(np.nanmean(eq_f)) if eq_f else np.nan,
        "avg_trend_frac":  float(np.nanmean(tr_f)) if tr_f else np.nan,
        "avg_cash_frac":   float(np.nanmean(ca_f)) if ca_f else np.nan,
        "raw_returns": raw_ret, "daily_turnover": daily_to, "cost_sensitivity": cost_df,
    }


def run_trained_rl_v2(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    model_path: Path,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Trained Phase E RL: load best checkpoint, run on holdout without retraining."""
    from stable_baselines3 import PPO

    if not model_path.exists():
        logger.warning("Model not found at %s — skipping trained RL", model_path)
        return {
            "policy": "Trained Phase E RL",
            "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan,
            "avg_equity_frac": np.nan, "raw_returns": None, "cost_sensitivity": pd.DataFrame(),
        }

    model = PPO.load(str(model_path))
    env = PortfolioEnvV2(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START, end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates, cost_bps=0.0,
        sector_features_df=sector_features_df,
    )

    def action_fn(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action

    raw_ret, daily_to, eq_f, tr_f, ca_f = _run_env_policy_v2(env, action_fn, "Trained Phase E RL")
    m = _cost_adjusted_metrics(raw_ret, daily_to, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
    cost_df = _cost_sensitivity(raw_ret, daily_to)
    return {
        "policy": "Trained Phase E RL",
        "sharpe": m["sharpe"], "cagr": m["cagr"], "max_dd": m["max_dd"],
        "avg_equity_frac": float(np.nanmean(eq_f)) if eq_f else np.nan,
        "avg_trend_frac":  float(np.nanmean(tr_f)) if tr_f else np.nan,
        "avg_cash_frac":   float(np.nanmean(ca_f)) if ca_f else np.nan,
        "raw_returns": raw_ret, "daily_turnover": daily_to, "cost_sensitivity": cost_df,
    }


def _regime_metrics(result: dict, label: str) -> list[dict]:
    """Compute per-regime Sharpe and MaxDD for a policy result."""
    rows = []
    raw = result.get("raw_returns")
    if raw is None:
        raw = result.get("net_returns")
    to = result.get("daily_turnover", pd.Series(dtype=float))
    if raw is None:
        return [{"regime": r, f"{label} Sharpe": np.nan, f"{label} MaxDD": np.nan} for r, *_ in HOLDOUT_REGIMES]
    for name, start, end in HOLDOUT_REGIMES:
        if isinstance(raw, pd.Series) and to is not None and len(to) > 0:
            m = _cost_adjusted_metrics(raw, to, B1_COST_BPS, start, end)
        else:
            m = _metrics_window(raw, start, end)
        rows.append({
            "regime": name,
            f"{label} Sharpe": m["sharpe"],
            f"{label} MaxDD": m["max_dd"],
        })
    return rows


# ---------------------------------------------------------------------------
# Promotion gate evaluation
# ---------------------------------------------------------------------------

def evaluate_promotion_gates_v2(
    rl_result: dict,
    noop_result: dict,
    random_result: dict,
    rule_based_result: dict,
    sharpe_50bps: float,
) -> pd.DataFrame:
    rl_sharpe  = rl_result["sharpe"]
    rl_maxdd   = rl_result["max_dd"]
    rand_med   = random_result.get("sharpe_median", np.nan)
    rand_p75   = random_result.get("sharpe_p75", np.nan)
    rb_sharpe  = rule_based_result["sharpe"]

    def _fs(v): return f"{v:.3f}" if np.isfinite(v) else "N/A"
    def _fp(v): return f"{v:.2%}"  if np.isfinite(v) else "N/A"

    gates = []

    path_a = (np.isfinite(rl_sharpe) and rl_sharpe >= GATE_PATH_A_SHARPE
              and np.isfinite(rl_maxdd)  and rl_maxdd  >= GATE_PATH_A_MAXDD)
    path_b = (np.isfinite(rl_sharpe) and rl_sharpe >= GATE_PATH_B_SHARPE
              and np.isfinite(rl_maxdd)  and rl_maxdd  >= GATE_PATH_B_MAXDD)

    gates.append({"gate": f"Path A: Sharpe ≥ {GATE_PATH_A_SHARPE:.3f} AND MaxDD ≥ {GATE_PATH_A_MAXDD:.2%}",
                  "value": f"Sharpe={_fs(rl_sharpe)}, MaxDD={_fp(rl_maxdd)}", "pass": path_a, "required": "either path"})
    gates.append({"gate": f"Path B: Sharpe ≥ {GATE_PATH_B_SHARPE:.3f} AND MaxDD ≥ {GATE_PATH_B_MAXDD:.2%}",
                  "value": f"Sharpe={_fs(rl_sharpe)}, MaxDD={_fp(rl_maxdd)}", "pass": path_b, "required": "either path"})
    gates.append({"gate": f"50 bps Sharpe ≥ {GATE_50BPS_SHARPE:.2f}",
                  "value": _fs(sharpe_50bps), "pass": bool(np.isfinite(sharpe_50bps) and sharpe_50bps >= GATE_50BPS_SHARPE), "required": "yes"})

    beats_noop = bool(np.isfinite(rl_sharpe) and np.isfinite(noop_result["sharpe"]) and rl_sharpe > noop_result["sharpe"])
    gates.append({"gate": f"Beats RL no-op Sharpe ({_fs(noop_result['sharpe'])})",
                  "value": _fs(rl_sharpe), "pass": beats_noop, "required": "yes"})

    # Random gates: median = hard minimum; p75 = preferred
    beats_rand_med = bool(np.isfinite(rl_sharpe) and np.isfinite(rand_med) and rl_sharpe > rand_med)
    beats_rand_p75 = bool(np.isfinite(rl_sharpe) and np.isfinite(rand_p75) and rl_sharpe > rand_p75)
    gates.append({"gate": f"Beats random median Sharpe ({_fs(rand_med)}) [hard minimum]",
                  "value": _fs(rl_sharpe), "pass": beats_rand_med, "required": "yes"})
    gates.append({"gate": f"Beats random p75 Sharpe ({_fs(rand_p75)}) [preferred]",
                  "value": _fs(rl_sharpe), "pass": beats_rand_p75, "required": "preferred"})

    beats_rule = bool(np.isfinite(rl_sharpe) and np.isfinite(rb_sharpe) and rl_sharpe > rb_sharpe)
    gates.append({"gate": f"Beats rule-based controller Sharpe ({_fs(rb_sharpe)})",
                  "value": _fs(rl_sharpe), "pass": beats_rule, "required": "yes"})

    hard_fail = np.isfinite(rl_maxdd) and rl_maxdd < GATE_HARD_MAXDD
    gates.append({"gate": f"Hard rejection: MaxDD ≥ {GATE_HARD_MAXDD:.0%} (no blowup)",
                  "value": _fp(rl_maxdd), "pass": not hard_fail, "required": "yes"})

    gates_df = pd.DataFrame(gates)
    either_path = path_a or path_b
    required_pass = gates_df[gates_df["required"] == "yes"]["pass"].all()
    # Conditional pass: beats median but not p75 — flag but don't block
    gates_df["promoted"] = bool(either_path and required_pass)
    if either_path and required_pass and not beats_rand_p75:
        gates_df["verdict_note"] = "CONDITIONAL: beats random median but not p75"
    else:
        gates_df["verdict_note"] = ""
    return gates_df


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report_v2(
    b5: dict, noop: dict, random: dict, rule_based: dict, trained: dict,
    regime_df: pd.DataFrame, gates_df: pd.DataFrame,
    primary_cost_bps: float = B1_COST_BPS,
) -> str:
    promoted = bool(gates_df["promoted"].any())
    conditional_note = gates_df["verdict_note"].iloc[0] if "verdict_note" in gates_df.columns else ""
    if promoted and conditional_note:
        verdict = f"**CONDITIONAL PROMOTE — {conditional_note}**"
    elif promoted:
        verdict = "**PROMOTE trained Phase E RL**"
    else:
        verdict = "**REJECT trained Phase E RL — keep B.5 as production system**"

    def _s(v): return f"{v:.3f}" if np.isfinite(v) else "N/A"
    def _p(v): return f"{v:.2%}"  if np.isfinite(v) else "N/A"

    lines = [
        "# Phase E.6 — RL Regime Controller v2 vs B.5 Five-Way Comparison",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Holdout window: {HOLDOUT_START} → {HOLDOUT_END}",
        f"- B.5 holdout benchmark (D.0): Sharpe {D0_HOLDOUT_SHARPE:.3f}, MaxDD {D0_HOLDOUT_MAXDD:.2%}",
        f"- Primary comparison cost: {primary_cost_bps:.0f} bps (same basis for all policies)",
        f"- Cost methodology: B.5 locked via compute_net_returns; RL policies via post-hoc turnover.",
        f"- Phase E no-op note: no-op removes trend sleeve (equity=1, trend=0). Expect Sharpe",
        f"  below B.5 locked (which keeps TLT/GLD/UUP ~20–30% of portfolio).",
        "",
        f"## Verdict: {verdict}",
        "",
    ]

    # Policy comparison table
    lines += [f"## Policy Comparison ({primary_cost_bps:.0f} bps, holdout 2019–2026)", ""]
    rows = []
    rand_sharpe_str = (
        f"{_s(random.get('sharpe'))} (mean) / "
        f"{_s(random.get('sharpe_median'))} (med) / "
        f"{_s(random.get('sharpe_p75'))} (p75)"
    )
    for r in [b5, noop, rule_based, trained]:
        rows.append({
            "Policy": r["policy"],
            "CAGR": _p(r.get("cagr", np.nan)),
            "Sharpe": _s(r.get("sharpe", np.nan)),
            "MaxDD": _p(r.get("max_dd", np.nan)),
            "Avg equity": _s(r.get("avg_equity_frac", np.nan)),
        })
    # Random row with extended stats
    rows.insert(3, {
        "Policy": random["policy"],
        "CAGR": _p(random.get("cagr", np.nan)),
        "Sharpe": rand_sharpe_str,
        "MaxDD": _p(random.get("max_dd", np.nan)),
        "Avg equity": "—",
    })
    lines.append(pd.DataFrame(rows).to_markdown(index=False))
    lines.append("")

    # Random distribution detail
    lines += ["## Random Baseline Distribution (50 seeds, 10 bps)", ""]
    pct_rows = [
        {"Stat": "Mean",    "Sharpe": _s(random.get("sharpe"))},
        {"Stat": "Median",  "Sharpe": _s(random.get("sharpe_median"))},
        {"Stat": "p25",     "Sharpe": _s(random.get("sharpe_p25"))},
        {"Stat": "p75",     "Sharpe": _s(random.get("sharpe_p75"))},
        {"Stat": "p90",     "Sharpe": _s(random.get("sharpe_p90"))},
        {"Stat": "p95",     "Sharpe": _s(random.get("sharpe_p95"))},
        {"Stat": "Std dev", "Sharpe": _s(random.get("sharpe_std"))},
    ]
    lines.append(pd.DataFrame(pct_rows).to_markdown(index=False))
    lines += [
        "",
        "> Promotion uses **median** as hard minimum and **p75** as preferred.",
        "> p90/p95 are reported for context only.",
        "",
    ]

    # Cost sensitivity
    lines += ["## Cost Sensitivity (all policies, post-hoc cost adjustment)", ""]
    b5_cost_df = pd.DataFrame(b5.get("cost_rows", []))[["cost_bps", "sharpe"]].rename(columns={"sharpe": "B.5 locked"})
    for label, r in [("No-op", noop), ("Rule-based", rule_based), ("Random mean", random), ("Trained RL", trained)]:
        cs = r.get("cost_sensitivity")
        if cs is not None and not cs.empty:
            col = cs[["cost_bps", "sharpe"]].rename(columns={"sharpe": label})
            b5_cost_df = b5_cost_df.merge(col, on="cost_bps", how="left")
    lines.append(b5_cost_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Regime Breakdown", ""]
    lines.append(regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Promotion Gate Evaluation", ""]
    lines.append(gates_df[["gate", "value", "pass", "required"]].to_markdown(index=False))
    lines.append("")

    lines += [
        "## Notes",
        "",
        "- Path A = clear win: Sharpe ≥ B.5 holdout (1.270) AND MaxDD ≥ B.5 holdout MaxDD (-32.98%).",
        "- Path B = tail improvement: Sharpe ≥ 1.240 AND MaxDD ≥ −31.48% (1.5pp better than B.5).",
        "- Both paths require 50 bps Sharpe ≥ 0.90, beat no-op, beat random median, beat rule-based.",
        "- Random p75 gate: preferred; conditional-pass if RL beats median but not p75.",
        "- Hard rejections: MaxDD < −35%.",
        "",
        "## Artifacts",
        "",
        "- `artifacts/reports/phase_e6_rl_evaluation.md` — this file",
        "- `artifacts/reports/e6_policy_comparison.csv`",
        "- `artifacts/reports/e6_regime_breakdown.csv`",
        "- `artifacts/reports/e6_promotion_gates.csv`",
        "- `artifacts/reports/e6_random_distribution.csv`",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase E.6 — RL Regime Controller v2 five-way comparison")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--model-path", default="artifacts/models/rl_e_ppo_best.zip")
    parser.add_argument(
        "--policy",
        choices=["all", "b5", "no_op", "random", "rule_based", "trained"],
        default="all",
    )
    parser.add_argument("--seeds", type=int, default=RANDOM_SEEDS)
    args = parser.parse_args()

    reports_dir = REPO_ROOT / "artifacts" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    model_path = REPO_ROOT / args.model_path

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )

    logger.info("Building beta/stress …")
    beta_frame    = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 weights …")
    b5_weights_df, _diag, _ctrl = build_promoted_weights(inputs, validation_end, beta_frame, stress_series)
    logger.info("B.5 weights built in %.1fs", time.perf_counter() - t0)

    logger.info("Loading sector features …")
    sector_features_df = pd.read_parquet(REPO_ROOT / "data" / "features" / "sector_features.parquet")

    primary_cost = B1_COST_BPS

    # ── B.5 locked ──────────────────────────────────────────────────────
    logger.info("Running B.5 locked …")
    r_b5 = run_b5_locked(inputs, b5_weights_df, validation_end)
    logger.info("B.5 locked: Sharpe=%.3f MaxDD=%.2f%% (@ %.0f bps)", r_b5["sharpe"], r_b5["max_dd"] * 100, primary_cost)

    if args.policy in ("all", "no_op"):
        logger.info("Running RL no-op …")
        r_noop = run_noop_policy_v2(inputs, b5_weights_df, sector_features_df, _ctrl, primary_cost)
        logger.info("RL no-op: Sharpe=%.3f (note: trend sleeve removed; expected below B.5)", r_noop["sharpe"])
    else:
        r_noop = {"policy": "RL no-op", "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan, "avg_equity_frac": np.nan, "cost_sensitivity": pd.DataFrame()}

    if args.policy in ("all", "random"):
        n_seeds = args.seeds
        logger.info("Running random bounded (%d seeds) …", n_seeds)
        r_random = run_random_policy_v2(inputs, b5_weights_df, sector_features_df, n_seeds, _ctrl, primary_cost)
        logger.info(
            "Random: mean=%.3f median=%.3f p75=%.3f",
            r_random["sharpe"], r_random.get("sharpe_median", np.nan), r_random.get("sharpe_p75", np.nan),
        )
    else:
        r_random = {"policy": "Random bounded (50 seeds)", "sharpe": np.nan, "sharpe_median": np.nan,
                    "sharpe_p75": np.nan, "sharpe_p25": np.nan, "sharpe_p90": np.nan, "sharpe_p95": np.nan,
                    "sharpe_std": np.nan, "cagr": np.nan, "max_dd": np.nan, "avg_equity_frac": np.nan,
                    "cost_sensitivity": pd.DataFrame(), "seed_records": []}

    if args.policy in ("all", "rule_based"):
        logger.info("Running rule-based controller …")
        r_rule = run_rule_based_policy_v2(inputs, b5_weights_df, sector_features_df, _ctrl, primary_cost)
        logger.info("Rule-based: Sharpe=%.3f MaxDD=%.2f%%", r_rule["sharpe"], r_rule["max_dd"] * 100)
    else:
        r_rule = {"policy": "Rule-based controller", "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan, "avg_equity_frac": np.nan, "cost_sensitivity": pd.DataFrame()}

    if args.policy in ("all", "trained"):
        logger.info("Running trained Phase E RL …")
        r_trained = run_trained_rl_v2(inputs, b5_weights_df, sector_features_df, model_path, _ctrl, primary_cost)
        logger.info("Trained RL: Sharpe=%.3f MaxDD=%.2f%%", r_trained["sharpe"], r_trained["max_dd"] * 100 if np.isfinite(r_trained["max_dd"]) else float("nan"))
    else:
        r_trained = {"policy": "Trained Phase E RL", "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan, "avg_equity_frac": np.nan, "cost_sensitivity": pd.DataFrame()}

    # ── Regime breakdown ─────────────────────────────────────────────────
    b5_reg   = _regime_metrics(r_b5,     "B.5 locked")
    noop_reg = _regime_metrics(r_noop,   "RL no-op")
    rl_reg   = _regime_metrics(r_trained, "Trained RL")
    regime_df = pd.DataFrame([
        {**b5_reg[i], **{k: v for k, v in noop_reg[i].items() if k != "regime"},
         **{k: v for k, v in rl_reg[i].items() if k != "regime"}}
        for i in range(len(HOLDOUT_REGIMES))
    ])

    # ── Promotion gates ──────────────────────────────────────────────────
    sharpe_50bps = np.nan
    if r_trained.get("cost_sensitivity") is not None and not r_trained["cost_sensitivity"].empty:
        cs = r_trained["cost_sensitivity"]
        row_50 = cs[cs["cost_bps"] == 50.0]
        if not row_50.empty:
            sharpe_50bps = float(row_50["sharpe"].iloc[0])

    gates_df = evaluate_promotion_gates_v2(r_trained, r_noop, r_random, r_rule, sharpe_50bps)

    # ── Policy comparison CSV ────────────────────────────────────────────
    comparison_rows = []
    for r in [r_b5, r_noop, r_rule, r_trained]:
        comparison_rows.append({
            "policy": r["policy"],
            "sharpe": r.get("sharpe"), "cagr": r.get("cagr"), "max_dd": r.get("max_dd"),
            "avg_equity_frac": r.get("avg_equity_frac"),
        })
    comparison_rows.append({
        "policy": r_random["policy"],
        "sharpe": r_random.get("sharpe"),
        "sharpe_median": r_random.get("sharpe_median"),
        "sharpe_p75": r_random.get("sharpe_p75"),
        "cagr": r_random.get("cagr"), "max_dd": r_random.get("max_dd"),
    })
    pd.DataFrame(comparison_rows).to_csv(reports_dir / "e6_policy_comparison.csv", index=False)
    regime_df.to_csv(reports_dir / "e6_regime_breakdown.csv", index=False)
    gates_df.to_csv(reports_dir / "e6_promotion_gates.csv", index=False)

    # Random distribution CSV
    if r_random.get("seed_records"):
        pd.DataFrame(r_random["seed_records"]).to_csv(reports_dir / "e6_random_distribution.csv", index=False)

    # ── Report markdown ──────────────────────────────────────────────────
    report_md = render_report_v2(r_b5, r_noop, r_random, r_rule, r_trained, regime_df, gates_df, primary_cost)
    (reports_dir / "phase_e6_rl_evaluation.md").write_text(report_md, encoding="utf-8")

    logger.info("Report written: phase_e6_rl_evaluation.md")
    logger.info("Total time: %.1fs", time.perf_counter() - t0)


if __name__ == "__main__":
    main()
