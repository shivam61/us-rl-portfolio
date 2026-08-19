"""Backfill Paper Trading Journey 2 from 2026-05-12 through today.

Runs the full daily ops orchestrator for every business day in the range,
skipping data refresh (market data is already current).

Usage
-----
    .venv/bin/python scripts/run_j2_backfill.py
    .venv/bin/python scripts/run_j2_backfill.py --end 2026-06-01
    .venv/bin/python scripts/run_j2_backfill.py --start 2026-07-01 --end 2026-08-19
"""
import argparse
import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
PYTHON = str(REPO_ROOT / ".venv" / "bin" / "python")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

START_DATE = "2026-05-12"


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill Journey 2 paper trading")
    parser.add_argument("--start", default=START_DATE, help=f"First date to process (default: {START_DATE})")
    parser.add_argument("--end", default=None, help="Last date to process (default: today)")
    parser.add_argument("--journey", default="j2", help="Journey ID (default: j2)")
    args = parser.parse_args()

    end_date = args.end or pd.Timestamp.today().strftime("%Y-%m-%d")
    trading_days = pd.bdate_range(args.start, end_date)
    logger.info("Backfilling %s: %d trading days from %s to %s",
                args.journey, len(trading_days), args.start, end_date)

    failed: list[str] = []
    for i, ts in enumerate(trading_days):
        date_str = ts.strftime("%Y-%m-%d")
        is_first = date_str == args.start

        cmd = [
            PYTHON, str(SCRIPTS_DIR / "run_daily_paper_ops.py"),
            "--date", date_str,
            "--journey", args.journey,
            "--skip-data-refresh",
        ]
        if is_first:
            cmd.append("--initial")

        logger.info("[%d/%d] %s%s", i + 1, len(trading_days), date_str, " (--initial)" if is_first else "")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            last_line = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "non-zero exit"
            logger.error("  FAILED: %s", last_line)
            failed.append(date_str)
        else:
            last_line = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "ok"
            logger.info("  OK: %s", last_line)

    if failed:
        logger.error("Backfill complete with %d failures: %s", len(failed), failed)
        sys.exit(1)
    else:
        logger.info("Backfill complete — all %d days succeeded.", len(trading_days))


if __name__ == "__main__":
    main()
