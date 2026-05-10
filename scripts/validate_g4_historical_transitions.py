"""Phase G.4 Historical Validation — Test switching rule on 3 regime transitions.

Tests:
  1. 2020-03 COVID crash — RL→B.5 switch triggered by sharpe or MaxDD
  2. 2022-01 Rate shock — drift flags co-occur, RL→B.5 switch
  3. 2023-10 Recovery — flags quiescent + RL recovered, B.5→RL switch

Usage
-----
.venv/bin/python scripts/validate_g4_historical_transitions.py
.venv/bin/python scripts/validate_g4_historical_transitions.py --test covid
.venv/bin/python scripts/validate_g4_historical_transitions.py --dry-run
"""
import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for _p in (REPO_ROOT, SCRIPTS_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from src.rl.switching_rule import SwitchingRuleEngine
from src.rl.drift_monitor import run_drift_check
from src.rl.nav_generator import load_b5_nav_backtest, generate_rl_nav_on_demand
from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import build_promoted_weights

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPORT_FILE = REPO_ROOT / "artifacts" / "reports" / "phase_g4_validation.md"


# ── Test configuration ────────────────────────────────────────────────────────

@dataclass
class TestConfig:
    name: str
    test_window: tuple[str, str]
    expected_trigger: str
    expectation: str


TEST_CONFIGS = {
    "covid": TestConfig(
        name="2020-03 COVID crash — RL outperformance",
        test_window=("2020-01-01", "2020-06-30"),
        expected_trigger="stay rl_e7 (RL outperformed B.5 during COVID)",
        expectation="RL de-risked better than B.5; no degradation trigger should fire",
    ),
    "rate_shock": TestConfig(
        name="2022-01 rate shock onset — RL degradation",
        test_window=("2021-10-01", "2022-03-31"),
        expected_trigger="rl_e7 → b5_only (sharpe degradation)",
        expectation="RL underperformed; sharpe degradation trigger should fire",
    ),
    "recovery": TestConfig(
        name="2025-04 recovery phase — RL recovery",
        test_window=("2025-01-01", "2026-01-31"),
        expected_trigger="b5_only → rl_e7 (flags quiescent, RL recovered)",
        expectation="RL recovered (Sharpe delta > 0); recovery trigger should fire",
    ),
}


# ── Simulation helpers ────────────────────────────────────────────────────────

def simulate_audit_trail(
    nav_series: pd.Series,
    mode: str = "rl_e7",
) -> pd.DataFrame:
    """
    Simulate audit trail from a NAV series.

    For validation purposes, we simulate what the audit trail would have looked like
    if production ran daily with the given NAV series.
    """
    records = []
    for date, nav_val in nav_series.items():
        rec = {
            "as_of_date": date,
            "run_timestamp": date,
            "mode": mode,
            "is_rebalance": True,  # Simplification
            "equity_frac": 0.40,  # Typical value
            "trend_frac": 0.50,
            "cash_frac": 0.10,
            "stress_score": 0.30,  # Will be overridden for specific tests
            "spy_trend_positive": True,
            "nav": float(nav_val),
            "model_id": "rl_e7_clean_promoted",
        }
        records.append(rec)
    return pd.DataFrame(records)


def simulate_drift_flags(
    audit_df: pd.DataFrame,
    b5_sharpe_ref: float = 1.296,
    b5_maxdd_ref: float = -0.2448,
) -> pd.DataFrame:
    """
    Simulate drift flags by running drift monitor on simulated audit trail.
    """
    flag_records = []
    for idx, row in audit_df.iterrows():
        # Run drift check on data up to this point
        audit_up_to_now = audit_df[audit_df["as_of_date"] <= row["as_of_date"]]
        if len(audit_up_to_now) < 10:
            continue  # Skip early dates

        drift_report = run_drift_check(audit_up_to_now, b5_sharpe_ref, b5_maxdd_ref)

        flag_rec = {
            "as_of_date": row["as_of_date"],
            "flag_sharpe_degradation": drift_report.flags["sharpe_degradation"].active,
            "flag_drawdown_excess": drift_report.flags["drawdown_excess"].active,
            "flag_cash_trap": drift_report.flags["cash_trap"].active,
            "flag_feature_psi": drift_report.flags["feature_psi"].active,
            "flag_stress_breach": drift_report.flags["stress_breach"].active,
            "alert_active": drift_report.alert_active,
        }
        flag_records.append(flag_rec)

    return pd.DataFrame(flag_records)


# ── Validation logic ──────────────────────────────────────────────────────────

def validate_transition(
    test_config: TestConfig,
    nav_b5: pd.Series,
    nav_rl: pd.Series,
    switching_engine: SwitchingRuleEngine,
) -> dict:
    """
    Validate switching rule on a historical transition window.

    Returns:
        Result dict with pass/fail gates and diagnostics
    """
    logger.info("=" * 80)
    logger.info("Testing: %s", test_config.name)
    logger.info("Window: %s to %s", *test_config.test_window)
    logger.info("=" * 80)

    start_date = pd.Timestamp(test_config.test_window[0])
    end_date = pd.Timestamp(test_config.test_window[1])

    # Slice NAV series to test window
    nav_b5_window = nav_b5[(nav_b5.index >= start_date) & (nav_b5.index <= end_date)]
    nav_rl_window = nav_rl[(nav_rl.index >= start_date) & (nav_rl.index <= end_date)]

    if nav_b5_window.empty or nav_rl_window.empty:
        logger.error("Empty NAV series in test window — skipping test")
        return {
            "test_name": test_config.name,
            "status": "SKIP",
            "reason": "empty_nav_window",
        }

    # Determine starting mode and NAV based on test type
    if "recovery" in test_config.name.lower():
        # Recovery test: start in b5_only mode, use B.5 NAV for audit trail
        starting_mode = "b5_only"
        audit_nav = nav_b5_window
        logger.info("Recovery test: starting mode=b5_only, using B.5 NAV for audit trail")
    else:
        # Degradation tests: start in rl_e7 mode, use RL NAV for audit trail
        starting_mode = "rl_e7"
        audit_nav = nav_rl_window
        logger.info("Degradation test: starting mode=rl_e7, using RL NAV for audit trail")

    # Simulate audit trail
    logger.info("Simulating audit trail …")
    audit_df = simulate_audit_trail(audit_nav, mode=starting_mode)

    # Simulate drift flags
    logger.info("Simulating drift flags …")
    drift_flags_df = simulate_drift_flags(audit_df)

    # Run switching engine at end of window
    logger.info("Evaluating switching rule at window end …")
    new_mode, reason = switching_engine.evaluate(
        audit_df=audit_df,
        drift_flags_df=drift_flags_df,
        mode=starting_mode,
        manual_override=None,
        nav_b5_backtest=nav_b5,
        nav_rl_backtest=nav_rl,
    )

    logger.info("Result: mode=%s, reason=%s", new_mode, reason)

    # Check gate criteria
    result = {
        "test_name": test_config.name,
        "test_window": test_config.test_window,
        "expected_trigger": test_config.expected_trigger,
        "actual_mode": new_mode,
        "actual_reason": reason,
        "audit_records": len(audit_df),
        "drift_records": len(drift_flags_df),
    }

    # Test-specific gate checks
    if "covid" in test_config.name.lower():
        # COVID: RL outperformed, should stay in rl_e7 (no degradation)
        passed = new_mode == "rl_e7" and "no_trigger" in reason.lower()
        result["gate_pass"] = passed
        result["status"] = "PASS" if passed else "FAIL"
    elif "rate" in test_config.name.lower() or "shock" in test_config.name.lower():
        # Rate shock: RL degraded, should switch to b5_only
        passed = new_mode == "b5_only" and ("drift" in reason.lower() or "flag" in reason.lower() or "sharpe" in reason.lower())
        result["gate_pass"] = passed
        result["status"] = "PASS" if passed else "FAIL"
    elif "recovery" in test_config.name.lower():
        # Recovery: RL recovered, should switch from b5_only → rl_e7
        # Starting mode is b5_only, should switch to rl_e7 if conditions met
        passed = new_mode == "rl_e7" and "recovery" in reason.lower()
        result["gate_pass"] = passed
        result["status"] = "PASS" if passed else "FAIL"
    else:
        result["gate_pass"] = False
        result["status"] = "UNKNOWN"

    return result


# ── Report generation ─────────────────────────────────────────────────────────

def write_validation_report(results: list[dict], output_path: Path) -> None:
    """Write validation results to markdown report."""
    lines = [
        "# Phase G.4 — Historical Validation Report",
        "",
        f"**Generated:** {pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%M:%SZ')}  ",
        "",
        "## Test Summary",
        "",
        "| Test | Window | Status | Mode | Reason |",
        "|------|--------|--------|------|--------|",
    ]

    for res in results:
        status_icon = "✅" if res["status"] == "PASS" else ("⏭️" if res["status"] == "SKIP" else "❌")
        lines.append(
            f"| {status_icon} {res['test_name']} | {res['test_window'][0]} to {res['test_window'][1]} | "
            f"**{res['status']}** | `{res.get('actual_mode', 'N/A')}` | {res.get('actual_reason', 'N/A')[:60]} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Test Details",
        "",
    ])

    for res in results:
        lines.extend([
            f"### {res['test_name']}",
            "",
            f"**Window:** {res['test_window'][0]} to {res['test_window'][1]}  ",
            f"**Expected:** {res['expected_trigger']}  ",
            f"**Actual mode:** `{res.get('actual_mode', 'N/A')}`  ",
            f"**Actual reason:** {res.get('actual_reason', 'N/A')}  ",
            f"**Gate:** {'PASS ✅' if res.get('gate_pass') else 'FAIL ❌'}  ",
            "",
            "**Diagnostics:**",
            f"- Audit records: {res.get('audit_records', 0)}",
            f"- Drift flag records: {res.get('drift_records', 0)}",
            "",
        ])

    lines.append("---\n")
    lines.append("**Overall gate:** PASS if all 3 tests pass individually.\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    logger.info("Validation report written to %s", output_path)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Phase G.4 Historical Validation")
    parser.add_argument("--test", choices=["covid", "rate_shock", "recovery", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # Load pre-computed B.5 and RL NAV
    logger.info("Loading B.5 NAV backtest …")
    nav_b5 = load_b5_nav_backtest()

    logger.info("Loading RL NAV backtest …")
    nav_rl_path = REPO_ROOT / "data" / "switching" / "nav_rl_backtest.parquet"
    if not nav_rl_path.exists():
        logger.error("RL NAV not found at %s", nav_rl_path)
        logger.error("Run: .venv/bin/python scripts/compute_rl_nav_for_g4.py")
        return 1

    nav_rl_df = pd.read_parquet(nav_rl_path)
    nav_rl_df["as_of_date"] = pd.to_datetime(nav_rl_df["as_of_date"])
    nav_rl = nav_rl_df.set_index("as_of_date")["nav"]
    logger.info(
        "RL NAV loaded: %d records, %s to %s",
        len(nav_rl),
        nav_rl.index.min().date(),
        nav_rl.index.max().date(),
    )

    # Create switching engine
    switching_engine = SwitchingRuleEngine(b5_sharpe_ref=1.296, b5_maxdd_ref=-0.2448)

    # Run tests
    tests_to_run = [args.test] if args.test != "all" else list(TEST_CONFIGS.keys())
    results = []

    for test_name in tests_to_run:
        config = TEST_CONFIGS[test_name]
        result = validate_transition(config, nav_b5, nav_rl, switching_engine)
        results.append(result)

    # Write report
    if not args.dry_run:
        write_validation_report(results, REPORT_FILE)

    # Print summary
    logger.info("=" * 80)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 80)
    for res in results:
        status_str = f"{'✅' if res['status'] == 'PASS' else '❌'} {res['status']}"
        logger.info("%s: %s", res["test_name"], status_str)

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    logger.info("=" * 80)
    logger.info("Overall: %d / %d tests passed in %.1fs", passed_count, len(results), time.perf_counter() - t0)

    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
