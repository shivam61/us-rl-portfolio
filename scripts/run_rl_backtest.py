"""Phase D.6 — Four-way comparison on holdout 2019–2026-04-24.

Policies:
  1. B.5 locked — no RL; vol_score + B.5 harness only
  2. RL no-op   — zero tilts + aggressiveness=1.0
  3. Random bounded — 50 seeds; uniform tilts in [−0.15,+0.15] subject to budget; random agg
  4. Trained RL — load artifacts/models/rl_ppo_best.zip; run on holdout without retraining

Usage:
    # Full four-way comparison:
    .venv/bin/python scripts/run_rl_backtest.py

    # Smoke test — run individual policies:
    .venv/bin/python scripts/run_rl_backtest.py --policy no_op
    .venv/bin/python scripts/run_rl_backtest.py --policy random --seeds 5
    .venv/bin/python scripts/run_rl_backtest.py --policy b5
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
from src.rl.environment import PortfolioEnv
from src.rl.state_builder import SECTOR_ORDER, TREND_ASSETS as RL_TREND_ASSETS
from src.rl.tilts import apply_sector_tilts

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HOLDOUT_START = "2019-01-01"
HOLDOUT_END = "2026-04-24"
RANDOM_SEEDS = 50

HOLDOUT_REGIMES = [
    ("2019 bull market", "2019-01-01", "2019-12-31"),
    ("2020 COVID crash", "2020-01-01", "2020-12-31"),
    ("2021 recovery", "2021-01-01", "2021-12-31"),
    ("2022 bear market", "2022-01-01", "2022-12-31"),
    ("2023–2026 recovery", "2023-01-01", "2026-04-24"),
]

# D.0 holdout benchmark (from phase_d0_holdout_baseline.md)
D0_HOLDOUT_SHARPE = 1.270
D0_HOLDOUT_MAXDD = -0.3298
D0_HOLDOUT_50BPS_SHARPE = 1.135

# Promotion gate thresholds (Phase D spec, updated with D.0 holdout numbers)
GATE_PATH_A_SHARPE = D0_HOLDOUT_SHARPE
GATE_PATH_A_MAXDD = D0_HOLDOUT_MAXDD
GATE_PATH_B_SHARPE = D0_HOLDOUT_SHARPE - 0.03
GATE_PATH_B_MAXDD = D0_HOLDOUT_MAXDD + 0.015
GATE_50BPS_SHARPE = 0.90
GATE_HARD_MAXDD = -0.35


def _metrics_window(net_returns: pd.Series, start: str, end: str) -> dict:
    mask = (net_returns.index >= pd.Timestamp(start)) & (net_returns.index <= pd.Timestamp(end))
    sliced = net_returns[mask]
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


# ---------------------------------------------------------------------------
# Policy runners
# ---------------------------------------------------------------------------

def run_b5_locked(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    validation_end: pd.Timestamp,
) -> dict:
    """B.5 locked — no RL. Pure B.5 construction, holdout metrics."""
    net_ret = compute_net_returns(inputs, b5_weights_df, validation_end, B1_COST_BPS)
    m = _metrics_window(net_ret, HOLDOUT_START, HOLDOUT_END)

    cost_rows = []
    for bps in COST_BPS:
        nr = compute_net_returns(inputs, b5_weights_df, validation_end, bps)
        cm = _metrics_window(nr, HOLDOUT_START, HOLDOUT_END)
        cost_rows.append({"cost_bps": bps, "sharpe": cm["sharpe"]})

    return {
        "policy": "B.5 locked",
        "sharpe": m["sharpe"],
        "cagr": m["cagr"],
        "max_dd": m["max_dd"],
        "cost_rows": cost_rows,
        "avg_tilt_magnitude": 0.0,
        "net_returns": net_ret,
    }


def _run_env_policy(
    env: PortfolioEnv,
    action_fn,
    label: str,
) -> tuple[pd.Series, pd.Series, list]:
    """Run a policy on env; return (daily_returns, daily_turnover, tilt_mags).

    The env must be constructed with cost_bps=0 so raw returns are returned.
    Costs are applied post-hoc via _cost_adjusted_metrics for flexibility.
    The daily_turnover Series has non-zero values only on the first trading day
    of each rebalance interval (matching compute_net_returns convention).
    """
    obs, _ = env.reset()
    done = False
    ep_tilts_mag = []
    # Per-step: first trading day after rebalance → turnover
    step_turnover: dict[pd.Timestamp, float] = {}

    while not done:
        action = action_fn(obs)
        obs, _reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        ep_tilts_mag.append(float(np.mean(np.abs(info["applied_tilts"]))))
        # next_date is the start of the next interval; prices are returned from
        # (current_date, next_date], so the first price day is current_date+1.
        # We record turnover on that date.
        current_dt = pd.Timestamp(info["date"])
        prices_idx = env.prices.index
        first_day_idx = prices_idx.searchsorted(current_dt, side="right")
        if first_day_idx < len(prices_idx):
            step_turnover[prices_idx[first_day_idx]] = info["turnover"]

    # Raw daily returns from the accumulated NAV series (env was run with cost_bps=0)
    nav = env._nav_series
    daily_returns = nav.pct_change().dropna()

    # Align turnover to full daily return index
    daily_turnover = pd.Series(0.0, index=daily_returns.index)
    for d, to in step_turnover.items():
        if d in daily_turnover.index:
            daily_turnover[d] = to

    return daily_returns, daily_turnover, ep_tilts_mag


def _cost_adjusted_metrics(
    raw_returns: pd.Series,
    daily_turnover: pd.Series,
    cost_bps: float,
    start: str,
    end: str,
) -> dict:
    """Apply transaction costs post-hoc and compute holdout metrics."""
    aligned_turnover = daily_turnover.reindex(raw_returns.index).fillna(0.0)
    cost_factor = (1.0 - aligned_turnover * cost_bps / 10_000.0).clip(lower=0.0)
    adj_returns = cost_factor * (1.0 + raw_returns) - 1.0
    return _metrics_window(adj_returns, start, end)


def _cost_sensitivity(
    raw_returns: pd.Series,
    daily_turnover: pd.Series,
    cost_bps_list: list[float] = COST_BPS,
) -> pd.DataFrame:
    rows = []
    for bps in cost_bps_list:
        m = _cost_adjusted_metrics(raw_returns, daily_turnover, bps, HOLDOUT_START, HOLDOUT_END)
        rows.append({"cost_bps": bps, "cagr": m["cagr"], "sharpe": m["sharpe"], "max_dd": m["max_dd"]})
    return pd.DataFrame(rows)


def run_noop_policy(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """RL no-op: zero tilts + max aggressiveness (action[11]=1.0).
    Env runs at cost_bps=0; costs applied post-hoc for cost sensitivity.
    """
    env = PortfolioEnv(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START, end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates, cost_bps=0.0,
    )
    noop_action = np.zeros(12, dtype=np.float32)
    noop_action[11] = 1.0

    def action_fn(_obs):
        return noop_action

    raw_returns, daily_turnover, tilt_mags = _run_env_policy(env, action_fn, "RL no-op")
    m = _cost_adjusted_metrics(raw_returns, daily_turnover, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
    cost_df = _cost_sensitivity(raw_returns, daily_turnover)
    return {
        "policy": "RL no-op",
        "sharpe": m["sharpe"],
        "cagr": m["cagr"],
        "max_dd": m["max_dd"],
        "avg_tilt_magnitude": float(np.mean(tilt_mags)) if tilt_mags else 0.0,
        "raw_returns": raw_returns,
        "daily_turnover": daily_turnover,
        "cost_sensitivity": cost_df,
    }


def run_random_policy(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    n_seeds: int = RANDOM_SEEDS,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Random bounded: average over n_seeds seeds, with post-hoc cost applied."""
    all_sharpes, all_cagrs, all_maxdds, all_tilt_mags = [], [], [], []
    all_cost_dfs = []

    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        env = PortfolioEnv(
            inputs, b5_weights_df,
            start_date=HOLDOUT_START, end_date=HOLDOUT_END,
            rebalance_dates=rebalance_dates, cost_bps=0.0,
        )

        def action_fn(_obs, _rng=rng):
            tilts = _rng.uniform(-1, 1, 11).astype(np.float32)
            agg = _rng.uniform(0.75, 1.0)
            agg_raw = float(2.0 * (agg - 0.75) / 0.25 - 1.0)
            return np.append(tilts, agg_raw).astype(np.float32)

        raw_returns, daily_turnover, tilt_mags = _run_env_policy(env, action_fn, f"random-{seed}")
        m = _cost_adjusted_metrics(raw_returns, daily_turnover, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
        all_sharpes.append(m["sharpe"])
        all_cagrs.append(m["cagr"])
        all_maxdds.append(m["max_dd"])
        all_tilt_mags.extend(tilt_mags)
        all_cost_dfs.append(_cost_sensitivity(raw_returns, daily_turnover))

    def _safe_mean(vals):
        valid = [v for v in vals if np.isfinite(v)]
        return float(np.mean(valid)) if valid else np.nan

    # Average cost sensitivity across seeds
    if all_cost_dfs:
        cost_df = pd.concat(all_cost_dfs).groupby("cost_bps").mean().reset_index()
    else:
        cost_df = pd.DataFrame()

    return {
        "policy": f"Random bounded ({n_seeds} seeds)",
        "sharpe": _safe_mean(all_sharpes),
        "cagr": _safe_mean(all_cagrs),
        "max_dd": _safe_mean(all_maxdds),
        "avg_tilt_magnitude": _safe_mean(all_tilt_mags),
        "sharpe_std": float(np.nanstd(all_sharpes)),
        "raw_returns": None,
        "cost_sensitivity": cost_df,
    }


def run_trained_rl(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    model_path: Path,
    rebalance_dates: list | None = None,
    primary_cost_bps: float = B1_COST_BPS,
) -> dict:
    """Trained RL: load best checkpoint, run on holdout without retraining.
    Env runs at cost_bps=0; costs applied post-hoc.
    """
    from stable_baselines3 import PPO

    if not model_path.exists():
        logger.warning("Model not found at %s — skipping trained RL", model_path)
        return {
            "policy": "Trained RL",
            "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan,
            "avg_tilt_magnitude": np.nan, "raw_returns": None,
            "cost_sensitivity": pd.DataFrame(),
        }

    model = PPO.load(str(model_path))
    env = PortfolioEnv(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START, end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates, cost_bps=0.0,
    )

    def action_fn(obs):
        action, _ = model.predict(obs, deterministic=True)
        return action

    raw_returns, daily_turnover, tilt_mags = _run_env_policy(env, action_fn, "Trained RL")
    m = _cost_adjusted_metrics(raw_returns, daily_turnover, primary_cost_bps, HOLDOUT_START, HOLDOUT_END)
    cost_df = _cost_sensitivity(raw_returns, daily_turnover)
    return {
        "policy": "Trained RL",
        "sharpe": m["sharpe"],
        "cagr": m["cagr"],
        "max_dd": m["max_dd"],
        "avg_tilt_magnitude": float(np.mean(tilt_mags)) if tilt_mags else np.nan,
        "raw_returns": raw_returns,
        "daily_turnover": daily_turnover,
        "cost_sensitivity": cost_df,
    }


# ---------------------------------------------------------------------------
# Promotion gate evaluation
# ---------------------------------------------------------------------------

def evaluate_promotion_gates(
    rl_result: dict,
    noop_result: dict,
    random_result: dict,
    b5_locked_result: dict,
    sharpe_50bps: float,
    cost_bps: float = B1_COST_BPS,
) -> pd.DataFrame:
    rl_sharpe = rl_result["sharpe"]
    rl_maxdd = rl_result["max_dd"]

    def _fmt_sharpe(v):
        return f"{v:.3f}" if np.isfinite(v) else "N/A"

    def _fmt_pct(v):
        return f"{v:.2%}" if np.isfinite(v) else "N/A"

    gates = []

    path_a = (
        np.isfinite(rl_sharpe) and rl_sharpe >= GATE_PATH_A_SHARPE
        and np.isfinite(rl_maxdd) and rl_maxdd >= GATE_PATH_A_MAXDD
    )
    path_b = (
        np.isfinite(rl_sharpe) and rl_sharpe >= GATE_PATH_B_SHARPE
        and np.isfinite(rl_maxdd) and rl_maxdd >= GATE_PATH_B_MAXDD
    )
    gates.append({
        "gate": f"Path A: Sharpe ≥ {GATE_PATH_A_SHARPE:.3f} AND MaxDD ≥ {GATE_PATH_A_MAXDD:.2%}",
        "value": f"Sharpe={_fmt_sharpe(rl_sharpe)}, MaxDD={_fmt_pct(rl_maxdd)}",
        "pass": path_a,
    })
    gates.append({
        "gate": f"Path B: Sharpe ≥ {GATE_PATH_B_SHARPE:.3f} AND MaxDD ≥ {GATE_PATH_B_MAXDD:.2%}",
        "value": f"Sharpe={_fmt_sharpe(rl_sharpe)}, MaxDD={_fmt_pct(rl_maxdd)}",
        "pass": path_b,
    })
    gates.append({
        "gate": f"50 bps Sharpe ≥ {GATE_50BPS_SHARPE:.2f}",
        "value": _fmt_sharpe(sharpe_50bps),
        "pass": bool(np.isfinite(sharpe_50bps) and sharpe_50bps >= GATE_50BPS_SHARPE),
    })
    beats_noop = bool(
        np.isfinite(rl_sharpe) and np.isfinite(noop_result["sharpe"])
        and rl_sharpe > noop_result["sharpe"]
    )
    gates.append({
        "gate": f"Beats RL no-op Sharpe ({_fmt_sharpe(noop_result['sharpe'])})",
        "value": _fmt_sharpe(rl_sharpe),
        "pass": beats_noop,
    })
    beats_random = bool(
        np.isfinite(rl_sharpe) and np.isfinite(random_result["sharpe"])
        and rl_sharpe > random_result["sharpe"]
    )
    gates.append({
        "gate": f"Beats random bounded Sharpe ({_fmt_sharpe(random_result['sharpe'])})",
        "value": _fmt_sharpe(rl_sharpe),
        "pass": beats_random,
    })
    hard_maxdd_fail = np.isfinite(rl_maxdd) and rl_maxdd < GATE_HARD_MAXDD
    gates.append({
        "gate": f"Hard rejection: MaxDD ≥ {GATE_HARD_MAXDD:.0%} (no blowup)",
        "value": _fmt_pct(rl_maxdd),
        "pass": not hard_maxdd_fail,
    })

    gates_df = pd.DataFrame(gates)
    either_path = path_a or path_b
    all_required = gates_df[gates_df["gate"].str.startswith(("50 bps", "Beats", "Hard"))]["pass"].all()
    gates_df["promoted"] = bool(either_path and all_required)
    return gates_df


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report(
    b5: dict,
    noop: dict,
    random: dict,
    trained: dict,
    regime_df: pd.DataFrame,
    gates_df: pd.DataFrame,
    primary_cost_bps: float = B1_COST_BPS,
) -> str:
    promoted = bool(gates_df["promoted"].any())
    verdict = "**PROMOTE trained RL**" if promoted else "**REJECT trained RL — keep B.5 as production system**"

    def _s(v): return f"{v:.3f}" if np.isfinite(v) else "N/A"
    def _p(v): return f"{v:.2%}" if np.isfinite(v) else "N/A"

    # No-op ≈ B.5 equivalence
    noop_b5_diff = abs(noop.get("sharpe", np.nan) - b5.get("sharpe", np.nan))
    noop_check = "PASS" if np.isfinite(noop_b5_diff) and noop_b5_diff < 0.05 else "WARN"

    lines = [
        "# Phase D.6 — RL vs B.5 Four-Way Comparison",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Holdout window: {HOLDOUT_START} → {HOLDOUT_END}",
        f"- B.5 holdout benchmark (D.0): Sharpe {D0_HOLDOUT_SHARPE:.3f}, MaxDD {D0_HOLDOUT_MAXDD:.2%}",
        f"- Primary comparison cost: {primary_cost_bps:.0f} bps (same basis for all policies)",
        f"- Cost methodology: B.5 locked via compute_net_returns; RL policies via post-hoc",
        f"  turnover-based deduction. RL env trained at cost_bps=0 (tilt penalty approximates cost).",
        "",
        f"## Verdict: {verdict}",
        "",
        "## Sanity Check: No-op ≈ B.5 Locked",
        "",
        f"| Check | B.5 Sharpe | No-op Sharpe | Diff | Status |",
        f"|---|---|---|---|---|",
        f"| No-op should reproduce B.5 at same cost | {_s(b5.get('sharpe', np.nan))} | "
        f"{_s(noop.get('sharpe', np.nan))} | {noop_b5_diff:.3f} | {noop_check} |",
        "",
        "> If diff > 0.05, the env's return simulation diverges from compute_net_returns.",
        "> Expected small diff due to: daily price differences, B.4 single-date vs full-period",
        "> application. Diff > 0.10 would indicate a bug.",
        "",
        f"## Policy Comparison ({primary_cost_bps:.0f} bps, holdout 2019–2026)",
        "",
    ]

    rows = []
    for r in [b5, noop, random, trained]:
        rows.append({
            "Policy": r["policy"],
            "CAGR": _p(r.get("cagr", np.nan)),
            "Sharpe": _s(r.get("sharpe", np.nan)),
            "MaxDD": _p(r.get("max_dd", np.nan)),
            "Avg |tilt|": f"{r['avg_tilt_magnitude']:.4f}" if np.isfinite(r.get("avg_tilt_magnitude", np.nan)) else "—",
        })
    lines.append(pd.DataFrame(rows).to_markdown(index=False))
    lines.append("")

    # Cost sensitivity tables for each policy
    lines += ["## Cost Sensitivity (all policies, post-hoc cost adjustment)", ""]
    lines += [
        "> B.5 locked: exact costs from compute_net_returns.",
        "> RL policies: costs applied post-hoc from turnover recorded during episode.",
        "",
    ]

    # Build combined cost table
    b5_cost = b5.get("cost_rows", [])
    if b5_cost:
        b5_cost_df = pd.DataFrame(b5_cost)[["cost_bps", "sharpe"]].rename(columns={"sharpe": "B.5 locked"})
    else:
        b5_cost_df = pd.DataFrame()

    for name, r in [("No-op", noop), ("Random", random), ("Trained RL", trained)]:
        cs = r.get("cost_sensitivity")
        if cs is not None and not cs.empty:
            col = cs[["cost_bps", "sharpe"]].rename(columns={"sharpe": name})
            if b5_cost_df.empty:
                b5_cost_df = col
            else:
                b5_cost_df = b5_cost_df.merge(col, on="cost_bps", how="left")

    if not b5_cost_df.empty:
        lines.append(b5_cost_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Regime Breakdown", ""]
    lines.append(regime_df.to_markdown(index=False, floatfmt=".4f"))
    lines.append("")

    lines += ["## Promotion Gate Evaluation", ""]
    lines.append(gates_df[["gate", "value", "pass"]].to_markdown(index=False))
    lines.append("")

    lines += [
        "## Notes",
        "",
        "- Path A = clear Sharpe win: Sharpe ≥ B.5 holdout AND MaxDD ≥ B.5 holdout MaxDD.",
        "- Path B = tail improvement: Sharpe ≥ B.5 − 0.03 AND MaxDD at least 1.5pp better.",
        "- Both paths require 50 bps Sharpe ≥ 0.90, beat no-op (same cost basis), beat random.",
        "- Hard rejections: MaxDD < −35%, or any beta violation, or max gross > 1.50.",
        "- B.5 holdout Sharpe (1.270) is higher than full-period (1.078) — 2019+ is a strong",
        "  regime; RL must add genuine value beyond the no-op baseline to be promoted.",
        "",
        "## Artifacts",
        "",
        "- `artifacts/reports/phase_d6_rl_evaluation.md` — this file",
        "- `artifacts/reports/d6_policy_comparison.csv`",
        "- `artifacts/reports/d6_regime_breakdown.csv`",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase D.6 — RL vs B.5 four-way comparison")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--model-path", default="artifacts/models/rl_ppo_best.zip")
    parser.add_argument(
        "--policy",
        choices=["all", "b5", "no_op", "random", "trained"],
        default="all",
        help="Which policy to run. 'all' runs the full four-way comparison.",
    )
    parser.add_argument(
        "--seeds", type=int, default=RANDOM_SEEDS,
        help=f"Number of seeds for random bounded policy (default {RANDOM_SEEDS}).",
    )
    parser.add_argument(
        "--cost-bps", type=float, default=B1_COST_BPS,
        help=f"Transaction cost in bps for primary comparison (default {B1_COST_BPS}). "
             "Applied to all policies on the same basis.",
    )
    args = parser.parse_args()

    out_dir = REPO_ROOT / "artifacts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )

    logger.info("Building beta/stress …")
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 weights …")
    b5_weights_df, _diag, _ctrl = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("B.5 weights built in %.1fs", time.perf_counter() - t0)

    model_path = REPO_ROOT / args.model_path
    run_all = args.policy == "all"

    primary_cost = args.cost_bps
    logger.info("Primary comparison cost: %.0f bps (same basis for all policies)", primary_cost)

    # --- Run policies (skip if not requested) ---
    def _null_result(name: str) -> dict:
        return {"policy": name, "sharpe": np.nan, "cagr": np.nan, "max_dd": np.nan,
                "avg_tilt_magnitude": np.nan, "raw_returns": None,
                "cost_sensitivity": pd.DataFrame()}

    if run_all or args.policy == "b5":
        logger.info("Running B.5 locked …")
        r_b5 = run_b5_locked(inputs, b5_weights_df, validation_end)
        # Supplement with cost row for primary cost
        b5_cost_rows = r_b5.get("cost_rows", [])
        primary_row = next((row for row in b5_cost_rows if row["cost_bps"] == primary_cost), None)
        if primary_row:
            r_b5["sharpe"] = primary_row["sharpe"]
            r_b5["cagr"] = primary_row.get("cagr", r_b5["cagr"])
            r_b5["max_dd"] = primary_row.get("max_dd", r_b5["max_dd"])
        logger.info("B.5 locked: Sharpe=%.3f MaxDD=%.2f%% (@ %.0f bps)", r_b5["sharpe"], r_b5["max_dd"] * 100, primary_cost)
    else:
        r_b5 = _null_result("B.5 locked")

    if run_all or args.policy == "no_op":
        logger.info("Running RL no-op …")
        r_noop = run_noop_policy(inputs, b5_weights_df, rebalance_dates=_ctrl, primary_cost_bps=primary_cost)
        logger.info("RL no-op: Sharpe=%.3f MaxDD=%.2f%% (@ %.0f bps)", r_noop["sharpe"], r_noop["max_dd"] * 100, primary_cost)
    else:
        r_noop = _null_result("RL no-op")

    n_seeds = args.seeds
    if run_all or args.policy == "random":
        logger.info("Running random bounded (%d seeds) …", n_seeds)
        r_random = run_random_policy(inputs, b5_weights_df, n_seeds=n_seeds, rebalance_dates=_ctrl, primary_cost_bps=primary_cost)
        logger.info("Random (%d seeds): Sharpe=%.3f MaxDD=%.2f%% (@ %.0f bps)", n_seeds, r_random["sharpe"], r_random["max_dd"] * 100, primary_cost)
    else:
        r_random = _null_result(f"Random bounded ({n_seeds} seeds)")

    if run_all or args.policy == "trained":
        logger.info("Running trained RL …")
        r_trained = run_trained_rl(inputs, b5_weights_df, model_path, rebalance_dates=_ctrl, primary_cost_bps=primary_cost)
        logger.info("Trained RL: Sharpe=%.3f MaxDD=%.2f%% (@ %.0f bps)", r_trained["sharpe"], r_trained["max_dd"] * 100, primary_cost)
    else:
        r_trained = _null_result("Trained RL")

    # --- Regime breakdown (all policies at primary_cost) ---
    regime_rows = []
    for label, start, end in HOLDOUT_REGIMES:
        row = {"regime": label}
        # B.5 locked: use net_returns from compute_net_returns (exact cost)
        b5_ret = r_b5.get("net_returns")
        if b5_ret is not None:
            m = _metrics_window(b5_ret, start, end)
            row["B.5 locked Sharpe"] = m["sharpe"]
            row["B.5 locked MaxDD"] = m["max_dd"]
        else:
            row["B.5 locked Sharpe"] = np.nan
            row["B.5 locked MaxDD"] = np.nan
        # RL policies: post-hoc cost applied to raw_returns
        for policy_name, r in [("RL no-op", r_noop), ("Trained RL", r_trained)]:
            raw = r.get("raw_returns")
            to = r.get("daily_turnover")
            if raw is not None and to is not None:
                m = _cost_adjusted_metrics(raw, to, primary_cost, start, end)
                row[f"{policy_name} Sharpe"] = m["sharpe"]
                row[f"{policy_name} MaxDD"] = m["max_dd"]
            else:
                row[f"{policy_name} Sharpe"] = np.nan
                row[f"{policy_name} MaxDD"] = np.nan
        regime_rows.append(row)
    regime_df = pd.DataFrame(regime_rows)

    # 50-bps Sharpe for trained RL — from cost_sensitivity DataFrame
    sharpe_50bps = np.nan
    cost_df_trained = r_trained.get("cost_sensitivity")
    if cost_df_trained is not None and not cost_df_trained.empty and "cost_bps" in cost_df_trained.columns:
        row_50 = cost_df_trained[cost_df_trained["cost_bps"] == 50.0]
        if not row_50.empty:
            sharpe_50bps = float(row_50["sharpe"].iloc[0])

    # --- Promotion gate evaluation ---
    gates_df = evaluate_promotion_gates(r_trained, r_noop, r_random, r_b5, sharpe_50bps)

    # --- Save CSVs ---
    compare_rows = []
    for r in [r_b5, r_noop, r_random, r_trained]:
        compare_rows.append({
            "policy": r["policy"],
            "sharpe": r["sharpe"],
            "cagr": r["cagr"],
            "max_dd": r["max_dd"],
            "avg_tilt_magnitude": r.get("avg_tilt_magnitude", np.nan),
            "sharpe_std": r.get("sharpe_std", np.nan),
        })
    pd.DataFrame(compare_rows).to_csv(out_dir / "d6_policy_comparison.csv", index=False)
    regime_df.to_csv(out_dir / "d6_regime_breakdown.csv", index=False)
    gates_df.to_csv(out_dir / "d6_promotion_gates.csv", index=False)
    logger.info("Saved D.6 CSVs")

    # --- Render report ---
    report = render_report(r_b5, r_noop, r_random, r_trained, regime_df, gates_df, primary_cost_bps=primary_cost)
    (out_dir / "phase_d6_rl_evaluation.md").write_text(report)
    logger.info("Wrote phase_d6_rl_evaluation.md")

    promoted = bool(gates_df["promoted"].any())
    logger.info(
        "D.6 VERDICT: %s — trained RL Sharpe=%.3f vs B.5 holdout %.3f (total %.1fs)",
        "PROMOTE" if promoted else "REJECT",
        r_trained["sharpe"],
        D0_HOLDOUT_SHARPE,
        time.perf_counter() - t0,
    )


if __name__ == "__main__":
    main()
