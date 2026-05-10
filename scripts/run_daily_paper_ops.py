"""Phase H — Daily Paper Trading Operations Orchestrator.

Runs the full nightly paper trading loop in sequence:
  0. Data refresh               → data/raw/*.parquet + data/features/*.parquet (incremental)
  1. G.1 signal generation      → data/allocations/{date}.json
  2. G.3 drift monitoring       → data/drift/flags.parquet
  3. Order computation          → data/paper_trading/orders_{date}.csv
  4. [T+1] Fill simulation      → data/paper_trading/fills_{date}.csv + positions_latest.parquet
  5. G.5 benchmark dashboard    → artifacts/reports/benchmark_dashboard.html
  6. Journal update             → docs/paper_trading_journal.md (human-readable daily log)
  7. H.6 experience log         → data/paper_trading/experience_log.parquet (rebalance days only)

Structured ops log is appended to data/paper_trading/daily_ops_log.jsonl.

Ops log schema (one JSON line per run):
  {"date": str, "mode": str, "is_rebalance": bool, "signal_ok": bool,
   "orders_count": int, "drift_flags_active": int, "pipeline_errors": [str]}

Usage
-----
# Full daily run (after 16:05 ET):
    .venv/bin/python scripts/run_daily_paper_ops.py --date 2026-05-10

# Skip fill simulation (run it next morning manually):
    .venv/bin/python scripts/run_daily_paper_ops.py --date 2026-05-10 --skip-fills

# T=0 initial setup:
    .venv/bin/python scripts/run_daily_paper_ops.py --date 2026-05-10 --initial

# Dry run (signal + drift only, no orders or fills written):
    .venv/bin/python scripts/run_daily_paper_ops.py --date 2026-05-10 --dry-run
"""
import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PYTHON = str(REPO_ROOT / ".venv" / "bin" / "python")


def load_config() -> dict:
    path = REPO_ROOT / "config" / "paper_trading.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def run_step(name: str, cmd: list[str]) -> tuple[bool, str]:
    """Run a subprocess step. Returns (success, error_message)."""
    logger.info("[%s] starting", name)
    t0 = time.monotonic()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.monotonic() - t0
        if result.returncode == 0:
            logger.info("[%s] OK (%.1fs)", name, elapsed)
            return True, ""
        else:
            msg = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "non-zero exit"
            logger.error("[%s] FAILED (%.1fs): %s", name, elapsed, msg)
            return False, msg
    except subprocess.TimeoutExpired:
        msg = f"{name} timed out after 300s"
        logger.error(msg)
        return False, msg
    except Exception as e:
        logger.error("[%s] exception: %s", name, e)
        return False, str(e)


def count_drift_flags(cfg: dict) -> int:
    flags_path = REPO_ROOT / cfg["paths"]["drift_flags"]
    if not flags_path.exists():
        return 0
    try:
        df = pd.read_parquet(flags_path)
        flag_cols = [c for c in df.columns if c.startswith("flag_")]
        if df.empty or not flag_cols:
            return 0
        latest = df.iloc[-1][flag_cols]
        return int(latest.sum())
    except Exception:
        return 0


def load_allocation_summary(date: str, cfg: dict) -> dict:
    alloc_dir = REPO_ROOT / cfg["paths"]["allocations_dir"]
    for path in [alloc_dir / f"{date}.json", alloc_dir / "latest.json"]:
        if path.exists():
            with open(path) as f:
                alloc = json.load(f)
            return {"mode": alloc.get("mode", "unknown"),
                    "is_rebalance": alloc.get("is_rebalance", False)}
    return {"mode": "unknown", "is_rebalance": False}


def count_orders(date: str, cfg: dict) -> int:
    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    orders_path = pt_dir / f"orders_{date}.csv"
    if not orders_path.exists():
        return 0
    try:
        df = pd.read_csv(orders_path)
        return int((df["action"] != "hold").sum())
    except Exception:
        return 0


def append_ops_log(entry: dict, cfg: dict) -> None:
    pt_dir = REPO_ROOT / cfg["paths"]["paper_trading_dir"]
    pt_dir.mkdir(parents=True, exist_ok=True)
    log_path = pt_dir / "daily_ops_log.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def alert_on_drift_flags(flags_active: int, cfg: dict) -> None:
    threshold = cfg["monitoring"]["drift_flag_alert_count"]
    if flags_active >= threshold:
        logger.warning(
            "ALERT: %d drift flags active (threshold=%d). Manual review required. "
            "Check data/drift/flags.parquet and G.3 drift monitor output.",
            flags_active, threshold,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily paper trading operations")
    parser.add_argument("--date", required=True, help="Signal date YYYY-MM-DD")
    parser.add_argument("--initial", action="store_true", help="T=0: no existing positions")
    parser.add_argument("--skip-fills", action="store_true", help="Skip fill simulation (run next morning)")
    parser.add_argument("--dry-run", action="store_true", help="Signal + drift only; no orders/fills written")
    args = parser.parse_args()

    cfg = load_config()
    logger.info("=== Phase H Daily Paper Ops | date=%s | config=%s NAV=$%.0f ===",
                args.date, cfg["version"], cfg["capital"]["initial_nav"])

    errors: list[str] = []

    # Step 0: Incremental market data + feature refresh
    if not args.dry_run:
        data_cmd = [PYTHON, str(SCRIPTS_DIR / "refresh_market_data.py"), "--as-of", args.date]
        ok, err = run_step("data refresh", data_cmd)
        if not ok:
            errors.append(f"data refresh: {err}")
            logger.warning("Data refresh failed — signal will use existing (possibly stale) features")
    else:
        logger.info("[data refresh] skipped (--dry-run)")

    # Step 1: G.1 signal generation
    signal_cmd = [PYTHON, str(SCRIPTS_DIR / "run_prod_signal.py"), "--as-of", args.date]
    if args.initial:
        signal_cmd.append("--force-rebalance")  # T=0: RL must fire its action, not carry forward B.5 defaults
    if args.dry_run:
        signal_cmd.append("--dry-run")
    ok, err = run_step("G.1 signal", signal_cmd)
    signal_ok = ok
    if not ok:
        errors.append(f"G.1 signal: {err}")

    # Step 2: G.3 drift monitoring
    drift_cmd = [PYTHON, str(SCRIPTS_DIR / "run_drift_monitor_g3.py")]
    ok, err = run_step("G.3 drift", drift_cmd)
    if not ok:
        errors.append(f"G.3 drift: {err}")

    drift_flags = count_drift_flags(cfg)
    alert_on_drift_flags(drift_flags, cfg)

    # Step 3: Order computation (skip on dry run or non-rebalance if signal failed)
    if not args.dry_run and signal_ok:
        orders_cmd = [PYTHON, str(SCRIPTS_DIR / "compute_paper_orders.py"), "--date", args.date]
        if args.initial:
            orders_cmd.append("--initial")
        ok, err = run_step("compute orders", orders_cmd)
        if not ok:
            errors.append(f"orders: {err}")
    elif args.dry_run:
        logger.info("[compute orders] skipped (--dry-run)")
    else:
        logger.warning("[compute orders] skipped — signal step failed")

    # Step 4: Fill simulation
    if not args.skip_fills and not args.dry_run and signal_ok:
        fills_cmd = [PYTHON, str(SCRIPTS_DIR / "log_paper_fills.py"), "--signal-date", args.date]
        ok, err = run_step("log fills", fills_cmd)
        if not ok:
            errors.append(f"fills: {err}")
    else:
        reason = "--dry-run" if args.dry_run else ("--skip-fills" if args.skip_fills else "signal failed")
        logger.info("[log fills] skipped (%s)", reason)

    # Step 5: G.5 benchmark dashboard refresh
    dashboard_cmd = [PYTHON, str(SCRIPTS_DIR / "run_benchmark_dashboard_g5.py")]
    ok, err = run_step("G.5 dashboard", dashboard_cmd)
    if not ok:
        errors.append(f"G.5 dashboard: {err}")

    # Load allocation summary (needed by steps 6, 7 and ops log)
    alloc_summary = load_allocation_summary(args.date, cfg)
    orders_count = count_orders(args.date, cfg)

    # Step 6: Journal update — human-readable daily log
    journal_cmd = [PYTHON, str(SCRIPTS_DIR / "generate_paper_journal.py"), "--date", args.date]
    ok, err = run_step("journal", journal_cmd)
    if not ok:
        errors.append(f"journal: {err}")

    # Step 7: H.6 experience log — append T-row + backfill T+14 (rebalance days only)
    if alloc_summary["is_rebalance"] and not args.dry_run and signal_ok:
        exp_cmd = [PYTHON, str(SCRIPTS_DIR / "append_experience_log.py"), "--date", args.date]
        ok, err = run_step("H.6 experience log", exp_cmd)
        if not ok:
            errors.append(f"H.6 experience log: {err}")
    elif not args.dry_run:
        logger.info("[H.6 experience log] skipped (non-rebalance day)")

    # Write ops log entry  (alloc_summary + orders_count already loaded above)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "date": args.date,
        "mode": alloc_summary["mode"],
        "is_rebalance": alloc_summary["is_rebalance"],
        "signal_ok": signal_ok,
        "orders_count": orders_count,
        "drift_flags_active": drift_flags,
        "pipeline_errors": errors,
    }
    if not args.dry_run:
        append_ops_log(entry, cfg)

    # Summary
    status = "OK" if not errors else f"ERRORS ({len(errors)})"
    logger.info("=== Daily ops complete | status=%s | mode=%s | rebalance=%s | orders=%d | drift_flags=%d ===",
                status, alloc_summary["mode"], alloc_summary["is_rebalance"],
                orders_count, drift_flags)

    if errors:
        logger.error("Pipeline errors:")
        for e in errors:
            logger.error("  - %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
