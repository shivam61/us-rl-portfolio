"""Phase G.3 — Live Drift Monitoring Dashboard.

Reads the G.2 audit trail, computes 5 drift flags, and writes:
  - artifacts/reports/phase_g3_drift_report.md   Human-readable dashboard
  - data/drift/flags.parquet                     Machine-readable flag history

Usage
-----
# Normal daily run (requires populated audit trail):
    .venv/bin/python scripts/run_drift_monitor_g3.py

# Gate validation — inject synthetic stress+cash-trap breach:
    .venv/bin/python scripts/run_drift_monitor_g3.py --simulate-breach

# Override B.5 reference metrics:
    .venv/bin/python scripts/run_drift_monitor_g3.py \\
        --b5-sharpe-ref 1.296 --b5-maxdd-ref -0.2448

# Compute but do not write files:
    .venv/bin/python scripts/run_drift_monitor_g3.py --dry-run --simulate-breach
"""
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.rl.audit_trail import query_decisions, AUDIT_FILE
from src.rl.drift_monitor import DriftReport, FlagResult, run_drift_check

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DRIFT_DIR   = REPO_ROOT / "data" / "drift"
FLAGS_FILE  = DRIFT_DIR / "flags.parquet"
REPORT_FILE = REPO_ROOT / "artifacts" / "reports" / "phase_g3_drift_report.md"


# ── Simulation helpers ────────────────────────────────────────────────────────

def _build_simulated_breach_df() -> pd.DataFrame:
    """20 synthetic audit records triggering stress_breach + cash_trap.

    stress_breach: records 5-19 have stress_score=0.75 → 15 consecutive > 0.70 (≥5 needed)
    cash_trap:     records 2-19 have equity_frac=0.20   → 18 consecutive < 0.25 (≥10 needed)
    """
    rng = np.random.default_rng(42)
    base = pd.Timestamp("2026-04-01")
    rows = []
    nav = 1.0
    for i in range(20):
        dt = base + pd.Timedelta(days=i)
        stress  = 0.75 if i >= 5 else 0.40
        eq_frac = 0.20 if i >= 2 else 0.40
        nav    *= 1.0 + float(rng.normal(0.0, 0.008))
        rec: dict = {
            "as_of_date":         dt,
            "run_timestamp":      dt,
            "mode":               "rl_e7",
            "is_rebalance":       True,
            "equity_frac":        eq_frac,
            "trend_frac":         0.50,
            "cash_frac":          round(1.0 - eq_frac - 0.50, 6),
            "stress_score":       stress,
            "spy_trend_positive": True,
            "nav":                round(nav, 6),
            "model_id":           "rl_e7_clean_promoted",
            "rl_action_0":        0.0,
            "rl_action_1":        0.5,
            "rl_action_2":        0.5,
            "stock_weights_json": "{}",
            "trend_weights_json": "{}",
            "override_flag":      False,
            "override_note":      "",
        }
        for j in range(42):
            rec[f"state_{j}"] = 0.0
        rec["state_0"]  = float(rng.uniform(0.7, 1.0))   # high VIX percentile
        rec["state_4"]  = float(rng.uniform(0.25, 0.35))  # elevated vol
        rec["state_13"] = stress                           # stress_score mirror
        rows.append(rec)
    return pd.DataFrame(rows)


# ── Report builder ────────────────────────────────────────────────────────────

def _flag_row(name: str, result: FlagResult) -> str:
    icon = "🔴" if result.active else "🟢"
    val  = f"{result.value:.4f}" if not (isinstance(result.value, float) and np.isnan(result.value)) else "N/A"
    thr  = f"{result.threshold:.4f}"
    # Escape pipe characters in message so the markdown table doesn't break
    msg  = result.message.replace("|", "\\|")
    return f"| {icon} | `{name}` | {val} | {thr} | {msg} |"


def build_report(report: DriftReport, mode: str = "live") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    active_count = sum(1 for r in report.flags.values() if r.active)

    header = [
        "# Phase G.3 — Drift Monitor Report",
        "",
        f"**As-of:** {report.as_of_date}  ",
        f"**Generated:** {ts}  ",
        f"**Mode:** {mode}  ",
        "",
    ]

    if report.alert_active:
        status_block = [
            "## ⚠️ ALERT ACTIVE",
            "",
            f"> {report.alert_message}",
            "",
        ]
    else:
        status_block = [
            "## ✅ No Alert",
            "",
            "> All drift flags within normal bounds — RL policy operating in-distribution.",
            "",
        ]

    flag_table = [
        "## Flag Summary",
        "",
        f"**Active flags:** {active_count} / {len(report.flags)}",
        "",
        "| Status | Flag | Value | Threshold | Detail |",
        "|--------|------|-------|-----------|--------|",
    ]
    for name, result in report.flags.items():
        flag_table.append(_flag_row(name, result))

    definitions = [
        "",
        "---",
        "",
        "## Alert Rule",
        "",
        "Alert fires when **any 2 flags co-occur within 5 trading days**.  ",
        "Action: escalate to manual review; consider switching to `b5_only` mode (G.4).",
        "",
        "## Flag Definitions",
        "",
        "| Flag | Metric | Threshold | Window |",
        "|------|--------|-----------|--------|",
        "| `sharpe_degradation` | Rolling 63d live Sharpe < B.5 ref − 0.05 | sustained ≥ 21d | 63d |",
        "| `drawdown_excess` | Live MaxDD exceeds B.5 MaxDD | by > 5pp | expanding |",
        "| `cash_trap` | equity_frac < 0.25 | ≥ 10 consecutive rebalances | — |",
        "| `feature_psi` | PSI on VIX/vol/stress state features | PSI > 0.20 | baseline vs rolling 63d |",
        "| `stress_breach` | stress_score > 0.70 | ≥ 5 consecutive days | — |",
    ]

    return "\n".join(header + status_block + flag_table + definitions) + "\n"


# ── Flag history persistence ──────────────────────────────────────────────────

def append_flags_history(report: DriftReport, mode: str) -> None:
    DRIFT_DIR.mkdir(parents=True, exist_ok=True)
    row: dict = {
        "as_of_date":    pd.Timestamp(report.as_of_date) if report.as_of_date != "N/A" else pd.NaT,
        "run_timestamp": pd.Timestamp(datetime.now(timezone.utc)),
        "mode":          mode,
        "alert_active":  report.alert_active,
        "alert_flags":   json.dumps(report.alert_flags),
    }
    for name, result in report.flags.items():
        row[f"flag_{name}"] = result.active
        row[f"val_{name}"]  = result.value

    new_row = pd.DataFrame([row])
    if FLAGS_FILE.exists():
        existing = pd.read_parquet(FLAGS_FILE)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row
    combined.to_parquet(FLAGS_FILE, index=False)
    logger.info("Flags history appended to %s", FLAGS_FILE)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Phase G.3 — Live Drift Monitor")
    parser.add_argument(
        "--simulate-breach", action="store_true",
        help="Inject synthetic data with stress+cash-trap breach for gate validation",
    )
    parser.add_argument(
        "--b5-sharpe-ref", type=float, default=1.296,
        help="B.5 reference Sharpe ratio (default: 1.296 from Phase F.2)",
    )
    parser.add_argument(
        "--b5-maxdd-ref", type=float, default=-0.2448,
        help="B.5 reference MaxDD as a negative fraction (default: -0.2448 from Phase F.2)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Compute but do not write any files",
    )
    args = parser.parse_args()

    mode = "simulate_breach" if args.simulate_breach else "live"

    # ── Load data ──────────────────────────────────────────────────────────────
    if args.simulate_breach:
        logger.info("SIMULATION MODE — injecting synthetic breach data")
        audit_df = _build_simulated_breach_df()
    else:
        logger.info("Loading audit trail from %s", AUDIT_FILE)
        audit_df = query_decisions()
        if audit_df.empty:
            logger.warning(
                "Audit trail is empty — run run_prod_signal.py to populate it, "
                "or use --simulate-breach for gate validation"
            )
            print("Audit trail is empty.  Use --simulate-breach to run the gate test.")
            return 1

    date_min = audit_df["as_of_date"].min().date() if not audit_df.empty else "N/A"
    date_max = audit_df["as_of_date"].max().date() if not audit_df.empty else "N/A"
    logger.info(
        "Running drift check on %d records (%s → %s)",
        len(audit_df), date_min, date_max,
    )

    # ── Run all flags ──────────────────────────────────────────────────────────
    report = run_drift_check(
        audit_df,
        b5_sharpe_ref=args.b5_sharpe_ref,
        b5_maxdd_ref=args.b5_maxdd_ref,
    )

    # ── Log results ───────────────────────────────────────────────────────────
    active_names = [n for n, r in report.flags.items() if r.active]
    logger.info(
        "Drift check complete: %d/%d flags active (%s)",
        len(active_names), len(report.flags),
        ", ".join(active_names) if active_names else "none",
    )
    for name, result in report.flags.items():
        tag = "ACTIVE" if result.active else "OK    "
        logger.info("  [%s] %-22s %s", tag, name, result.message)

    if report.alert_active:
        logger.warning("⚠️  ALERT: %s", report.alert_message)
    else:
        logger.info("✅  No alert — all flags within normal bounds")

    report_text = build_report(report, mode=mode)

    if args.dry_run:
        print(report_text)
        if args.simulate_breach:
            ok = report.alert_active
            print(f"\n{'✅' if ok else '❌'} G.3 GATE (dry-run): "
                  f"{'PASS' if ok else 'FAIL'} — alert {'fired' if ok else 'did NOT fire'} "
                  f"on simulated breach")
        return 0

    # ── Write outputs ──────────────────────────────────────────────────────────
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report_text)
    logger.info("Dashboard report written to %s", REPORT_FILE)

    append_flags_history(report, mode)

    # ── Gate validation verdict ────────────────────────────────────────────────
    if args.simulate_breach:
        if report.alert_active:
            print(
                f"\n✅ G.3 GATE: PASS — Alert fired on simulated breach "
                f"(co-firing: {', '.join(report.alert_flags)})"
            )
            return 0
        else:
            print("\n❌ G.3 GATE: FAIL — Alert did NOT fire on simulated breach")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
