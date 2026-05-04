"""Phase G.2 — Append-only audit trail for production allocation decisions.

Each allocation run appends one record to data/audit/decisions.parquet.
Records are never modified in-place — this is a write-once log.

Schema (one row per run)
------------------------
as_of_date          : datetime64[ns]
run_timestamp       : datetime64[ns] (UTC)
mode                : str  ("rl_e7" | "b5_only")
is_rebalance        : bool
equity_frac         : float64
trend_frac          : float64
cash_frac           : float64
stress_score        : float64
spy_trend_positive  : bool
nav                 : float64
model_id            : str
rl_action_0         : float64  (raw_action[0] or NaN)
rl_action_1         : float64
rl_action_2         : float64
state_0 … state_41  : float64  (42 RL state features)
stock_weights_json  : str  (JSON-encoded dict)
trend_weights_json  : str
override_flag       : bool  (True if any constraint was manually overridden)
override_note       : str
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

REPO_ROOT   = Path(__file__).resolve().parents[2]
AUDIT_DIR   = REPO_ROOT / "data" / "audit"
AUDIT_FILE  = AUDIT_DIR / "decisions.parquet"

_STATE_COLS = [f"state_{i}" for i in range(42)]


def append_decision(allocation: dict, override_flag: bool = False, override_note: str = "") -> None:
    """Append one allocation decision record to the audit log.

    Args:
        allocation: Output dict from compute_allocation in run_prod_signal.py.
        override_flag: True if any constraint was manually overridden this run.
        override_note: Human-readable description of any override.
    """
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    rl_action = allocation.get("rl_raw_action") or [np.nan, np.nan, np.nan]
    rl_state  = allocation.get("rl_state_vector", [np.nan] * 42)

    row: dict = {
        "as_of_date":         pd.Timestamp(allocation["as_of_date"]),
        "run_timestamp":      pd.Timestamp(datetime.now(timezone.utc)),
        "mode":               allocation["mode"],
        "is_rebalance":       bool(allocation["is_rebalance"]),
        "equity_frac":        float(allocation["equity_frac"]),
        "trend_frac":         float(allocation["trend_frac"]),
        "cash_frac":          float(allocation["cash_frac"]),
        "stress_score":       float(allocation["stress_score"]),
        "spy_trend_positive": bool(allocation["spy_trend_positive"]),
        "nav":                float(allocation["nav"]),
        "model_id":           str(allocation.get("model_id", "")),
        "rl_action_0":        float(rl_action[0]) if rl_action[0] is not None else np.nan,
        "rl_action_1":        float(rl_action[1]) if rl_action[1] is not None else np.nan,
        "rl_action_2":        float(rl_action[2]) if rl_action[2] is not None else np.nan,
        "stock_weights_json": json.dumps(allocation.get("stock_weights", {})),
        "trend_weights_json": json.dumps(allocation.get("trend_weights", {})),
        "override_flag":      bool(override_flag),
        "override_note":      str(override_note),
    }

    for i, col in enumerate(_STATE_COLS):
        row[col] = float(rl_state[i]) if i < len(rl_state) else np.nan

    new_row = pd.DataFrame([row])

    if AUDIT_FILE.exists():
        existing = pd.read_parquet(AUDIT_FILE)
        combined = pd.concat([existing, new_row], ignore_index=True)
    else:
        combined = new_row

    combined.to_parquet(AUDIT_FILE, index=False)
    logger.info("Audit record appended: as_of=%s mode=%s is_rebalance=%s",
                allocation["as_of_date"], allocation["mode"], allocation["is_rebalance"])


def query_decisions(
    start: str | None = None,
    end: str | None = None,
    mode: str | None = None,
) -> pd.DataFrame:
    """Query the audit log by date range and/or mode.

    Args:
        start: ISO date string (inclusive). None = no lower bound.
        end:   ISO date string (inclusive). None = no upper bound.
        mode:  "rl_e7" | "b5_only" | None = all.

    Returns:
        DataFrame of matching records (columns: see module docstring).
    """
    if not AUDIT_FILE.exists():
        return pd.DataFrame()

    df = pd.read_parquet(AUDIT_FILE)
    if start:
        df = df[df["as_of_date"] >= pd.Timestamp(start)]
    if end:
        df = df[df["as_of_date"] <= pd.Timestamp(end)]
    if mode:
        df = df[df["mode"] == mode]
    return df.reset_index(drop=True)


def summarize_audit(n_recent: int = 10) -> None:
    """Print a summary of the most recent audit records."""
    df = query_decisions()
    if df.empty:
        print("Audit log is empty.")
        return
    print(f"Audit log: {len(df)} total records, {df['as_of_date'].min().date()} → {df['as_of_date'].max().date()}")
    display_cols = ["as_of_date", "mode", "is_rebalance", "equity_frac",
                    "trend_frac", "cash_frac", "stress_score", "nav"]
    print(df[display_cols].tail(n_recent).to_string(index=False))
