"""Phase G.0 — Feature Parity Check.

Verifies that the 42-dim RL state vector computed by a standalone call to
`build_state_v2` (simulating the live production pipeline) reproduces the
exact same values as the state captured during a backtest episode.

Gate: max absolute deviation < 1e-6 across all 42 features for the last 30
rebalance dates in the holdout window.

Usage:
    .venv/bin/python scripts/check_feature_parity_g0.py
    .venv/bin/python scripts/check_feature_parity_g0.py --last-n 30
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

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import build_promoted_weights
from src.rl.environment_v2 import PortfolioEnvV2
from src.rl.state_builder_v2 import OBS_DIM, SECTOR_ORDER_V2, build_state_v2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HOLDOUT_START = "2019-01-01"
HOLDOUT_END   = "2026-04-24"
PARITY_GATE   = 1e-6

# Feature names matching obs layout (state_builder_v2.py docstring)
_FEATURE_NAMES = [
    "vix_percentile_1y",
    "spy_drawdown_from_peak",
    "spy_ret_3m",
    "spy_ret_6m",
    "realized_market_vol_63d",
    "iwm_spy_spread_63d",
    "qqq_spy_spread_63d",
    "tlt_ret_3m",
    "tlt_ret_6m",
    "gld_ret_3m",
    "gld_ret_6m",
    "uup_ret_3m",
    "uup_ret_6m",
    "stress_score",
] + [f"sector_mom_vs_spy_{s}" for s in SECTOR_ORDER_V2] \
  + [f"sector_vol_63d_{s}" for s in SECTOR_ORDER_V2] \
  + [
    "current_equity_frac",
    "current_trend_frac",
    "current_cash_frac",
    "portfolio_drawdown",
    "portfolio_vol_63d",
    "portfolio_ret_21d_zscore",
]

# Expected bounds for range validation (loose — just catches wild values)
_BOUNDS = {
    "vix_percentile_1y":       (0.0,  1.0),
    "spy_drawdown_from_peak":  (-1.0, 0.0),
    "spy_ret_3m":              (-1.0, 2.0),
    "spy_ret_6m":              (-1.0, 2.0),
    "realized_market_vol_63d": (0.0,  2.0),
    "iwm_spy_spread_63d":      (-0.5, 0.5),
    "qqq_spy_spread_63d":      (-0.5, 0.5),
    "tlt_ret_3m":              (-0.5, 0.5),
    "tlt_ret_6m":              (-0.5, 0.5),
    "gld_ret_3m":              (-0.5, 0.5),
    "gld_ret_6m":              (-0.5, 0.5),
    "uup_ret_3m":              (-0.5, 0.5),
    "uup_ret_6m":              (-0.5, 0.5),
    "stress_score":            (0.0,  1.0),
    "current_equity_frac":     (0.0,  1.0),
    "current_trend_frac":      (0.0,  1.0),
    "current_cash_frac":       (0.0,  0.5),
    "portfolio_drawdown":      (-1.0, 0.0),
    "portfolio_vol_63d":       (0.0,  2.0),
    "portfolio_ret_21d_zscore":(-3.0, 3.0),
}
for _s in SECTOR_ORDER_V2:
    _BOUNDS[f"sector_mom_vs_spy_{_s}"] = (-0.5, 0.5)
    _BOUNDS[f"sector_vol_63d_{_s}"]    = (0.0,  0.10)


def run_episode_capture(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    rebalance_dates: list,
    last_n: int,
) -> list[dict]:
    """Run a no-op episode on the holdout window; capture state + portfolio state at each step.

    Returns list of dicts with keys: date, backtest_obs, equity_frac, trend_frac,
    cash_frac, nav_series.
    """
    env = PortfolioEnvV2(
        inputs, b5_weights_df,
        start_date=HOLDOUT_START,
        end_date=HOLDOUT_END,
        rebalance_dates=rebalance_dates,
        cost_bps=0.0,
        sector_features_df=sector_features_df,
    )

    noop_action = np.array([1.0, -1.0, -1.0], dtype=np.float32)
    obs, _ = env.reset()
    done = False

    captures = []
    step = 0

    # Capture initial obs (before first step)
    captures.append({
        "step":         step,
        "date":         env.rebalance_dates[0],
        "backtest_obs": obs.copy(),
        "equity_frac":  env._current_equity_frac,
        "trend_frac":   env._current_trend_frac,
        "cash_frac":    env._current_cash_frac,
        "nav_series":   env._nav_series.copy(),
    })

    while not done:
        obs, _reward, terminated, truncated, info = env.step(noop_action)
        done = terminated or truncated
        step += 1
        date_idx = min(env._step_idx, len(env.rebalance_dates) - 1)
        captures.append({
            "step":         step,
            "date":         env.rebalance_dates[date_idx],
            "backtest_obs": obs.copy(),
            "equity_frac":  env._current_equity_frac,
            "trend_frac":   env._current_trend_frac,
            "cash_frac":    env._current_cash_frac,
            "nav_series":   env._nav_series.copy(),
        })

    # Return last_n captures for the gate check
    return captures[-last_n:]


def compute_live_obs(
    inputs: dict,
    b5_weights_df: pd.DataFrame,
    sector_features_df: pd.DataFrame,
    stress_series: pd.Series,
    capture: dict,
) -> np.ndarray:
    """Call build_state_v2 fresh with the portfolio state from a captured step.

    This simulates the nightly production pipeline calling build_state_v2 with
    the current tracked portfolio state.
    """
    return build_state_v2(
        inputs=inputs,
        b5_weights=b5_weights_df,
        nav_series=capture["nav_series"],
        date=capture["date"],
        stress_series=stress_series,
        current_equity_frac=capture["equity_frac"],
        current_trend_frac=capture["trend_frac"],
        current_cash_frac=capture["cash_frac"],
        sector_features_df=sector_features_df,
    )


def check_ranges(obs: np.ndarray, date: pd.Timestamp) -> list[str]:
    """Return list of range violations for a given obs vector."""
    violations = []
    for i, name in enumerate(_FEATURE_NAMES):
        if name not in _BOUNDS:
            continue
        lo, hi = _BOUNDS[name]
        v = float(obs[i])
        if not (lo - 1e-9 <= v <= hi + 1e-9):
            violations.append(f"[{i}] {name}={v:.6f} out of [{lo}, {hi}] on {date.date()}")
    return violations


def main():
    parser = argparse.ArgumentParser(description="Phase G.0 — Feature Parity Check")
    parser.add_argument("--config",   default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--last-n",   type=int, default=30,
                        help="Number of most-recent rebalance steps to check (default 30)")
    args = parser.parse_args()

    reports_dir = REPO_ROOT / "artifacts" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )

    logger.info("Building beta / stress series …")
    beta_frame    = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 weights …")
    b5_weights_df, _diag, rebalance_dates = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("B.5 built in %.1fs", time.perf_counter() - t0)

    logger.info("Loading sector features …")
    sector_features_df = pd.read_parquet(REPO_ROOT / "data" / "features" / "sector_features.parquet")

    # ── Run episode and capture states ────────────────────────────────────
    logger.info("Running no-op episode on holdout window (capturing states) …")
    captures = run_episode_capture(
        inputs, b5_weights_df, sector_features_df, rebalance_dates, args.last_n
    )
    logger.info("Captured %d rebalance steps", len(captures))

    # ── Compare backtest obs vs standalone live obs ───────────────────────
    rows = []
    all_violations = []
    max_global_dev = 0.0
    nan_count = 0

    for cap in captures:
        live_obs = compute_live_obs(inputs, b5_weights_df, sector_features_df, stress_series, cap)
        backtest_obs = cap["backtest_obs"]

        # NaN check
        n_nan_live     = int(np.sum(~np.isfinite(live_obs)))
        n_nan_backtest = int(np.sum(~np.isfinite(backtest_obs)))
        nan_count += n_nan_live + n_nan_backtest

        # Deviation
        dev = np.abs(live_obs.astype(float) - backtest_obs.astype(float))
        max_dev = float(dev.max())
        worst_idx = int(dev.argmax())
        max_global_dev = max(max_global_dev, max_dev)

        gate_pass = max_dev < PARITY_GATE

        rows.append({
            "date":        cap["date"].date(),
            "step":        cap["step"],
            "max_dev":     max_dev,
            "worst_feat":  _FEATURE_NAMES[worst_idx],
            "worst_idx":   worst_idx,
            "nan_live":    n_nan_live,
            "nan_bt":      n_nan_backtest,
            "gate_pass":   gate_pass,
        })

        # Range checks
        violations = check_ranges(live_obs, cap["date"])
        all_violations.extend(violations)

    results_df = pd.DataFrame(rows)
    gate_pass_all  = bool((results_df["max_dev"] < PARITY_GATE).all())
    gate_pass_nan  = nan_count == 0
    gate_pass_full = gate_pass_all and gate_pass_nan

    # ── Per-feature max deviation summary ────────────────────────────────
    all_devs = np.zeros((len(captures), OBS_DIM))
    for i, cap in enumerate(captures):
        live_obs = compute_live_obs(inputs, b5_weights_df, sector_features_df, stress_series, cap)
        all_devs[i] = np.abs(live_obs.astype(float) - cap["backtest_obs"].astype(float))

    feat_max_dev = all_devs.max(axis=0)
    feat_df = pd.DataFrame({
        "idx":     range(OBS_DIM),
        "feature": _FEATURE_NAMES,
        "max_dev": feat_max_dev,
    })

    # ── Print summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Phase G.0 — Feature Parity Check")
    print("=" * 70)
    print(f"\nDates checked : {len(captures)} (last {args.last_n} rebalance steps in holdout)")
    print(f"Max global dev: {max_global_dev:.2e}  (gate < {PARITY_GATE:.0e})")
    print(f"Total NaN     : {nan_count}")
    print(f"Range violat. : {len(all_violations)}")
    print(f"\nGate result   : {'PASS ✓' if gate_pass_full else 'FAIL ✗'}")

    if not gate_pass_all:
        print("\n[FAIL] Steps with max_dev >= 1e-6:")
        fails = results_df[~results_df["gate_pass"]]
        print(fails[["date", "max_dev", "worst_feat"]].to_string(index=False))

    if all_violations:
        print(f"\n[WARN] Range violations ({len(all_violations)}):")
        for v in all_violations[:20]:
            print(f"  {v}")

    print("\n--- Per-date deviation summary (last 10 shown) ---")
    print(results_df[["date", "max_dev", "worst_feat", "gate_pass"]].tail(10).to_string(index=False))

    # ── Save report ───────────────────────────────────────────────────────
    out_path = reports_dir / "phase_g0_feature_parity.md"
    _write_report(out_path, results_df, feat_df, all_violations, max_global_dev,
                  nan_count, gate_pass_full, args)
    logger.info("Report saved to %s", out_path)

    # Save CSV for future G.3 drift comparison
    feat_df.to_csv(reports_dir / "g0_feature_max_dev.csv", index=False)
    results_df.to_csv(reports_dir / "g0_per_step_deviation.csv", index=False)

    return 0 if gate_pass_full else 1


def _write_report(
    out_path: Path,
    results_df: pd.DataFrame,
    feat_df: pd.DataFrame,
    violations: list[str],
    max_global_dev: float,
    nan_count: int,
    gate_pass: bool,
    args,
) -> None:
    verdict = "**PASS**" if gate_pass else "**FAIL**"
    lines = [
        "# Phase G.0 — Feature Parity Check",
        "",
        f"- Run date: {pd.Timestamp.now('UTC').strftime('%Y-%m-%d %H:%M:%S %Z')}",
        f"- Universe: {args.universe}",
        f"- Holdout window: {HOLDOUT_START} → {HOLDOUT_END}",
        f"- Steps checked: {len(results_df)} (last {args.last_n} rebalance steps)",
        f"- Gate: max absolute deviation < {PARITY_GATE:.0e} for all 42 features",
        "",
        f"## Verdict: {verdict}",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Max global deviation | `{max_global_dev:.2e}` |",
        f"| Total NaN values | {nan_count} |",
        f"| Range violations | {len(violations)} |",
        f"| Steps passing gate | {(results_df['gate_pass']).sum()} / {len(results_df)} |",
        "",
        "## Per-Step Deviation",
        "",
        results_df[["date", "step", "max_dev", "worst_feat", "gate_pass"]].to_markdown(index=False),
        "",
        "## Per-Feature Maximum Deviation (across all checked steps)",
        "",
        feat_df[feat_df["max_dev"] > 0].to_markdown(index=False) if (feat_df["max_dev"] > 0).any()
        else "_All deviations exactly zero._",
        "",
    ]

    if violations:
        lines += ["## Range Violations", ""]
        for v in violations:
            lines.append(f"- {v}")
        lines.append("")
    else:
        lines += ["## Range Violations", "", "_None._", ""]

    lines += [
        "## Methodology",
        "",
        "**Backtest path:** Run `PortfolioEnvV2` (no-op policy) on the holdout window.",
        "The env's `_build_obs()` calls `build_state_v2` at each rebalance step and",
        "returns the obs vector. This is the ground-truth reference.",
        "",
        "**Live sim path:** After the episode, call `build_state_v2` standalone with the",
        "portfolio state (equity_frac, trend_frac, cash_frac, nav_series) captured from",
        "the corresponding episode step. This simulates what the nightly production",
        "pipeline will do when it calls `build_state_v2` with tracked portfolio state.",
        "",
        "**Gate:** max|backtest_obs − live_obs| < 1e-6 for each of the last 30 steps.",
        "A deviation of exactly 0.0 is expected since both paths call the same function",
        "with identical arguments; the 1e-6 tolerance guards against float32/float64 cast",
        "differences.",
        "",
        "## Artifacts",
        "",
        "- `artifacts/reports/phase_g0_feature_parity.md` — this file",
        "- `artifacts/reports/g0_feature_max_dev.csv` — per-feature deviation (for G.3 baseline)",
        "- `artifacts/reports/g0_per_step_deviation.csv` — per-step deviation detail",
    ]

    out_path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
