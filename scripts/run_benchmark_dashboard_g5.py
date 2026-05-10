"""Phase G.5 — Benchmark Dashboard.

Reads pre-computed NAV series (B.5, RL), SPY, TLT prices, and the G.2 audit
trail, then writes a daily Markdown performance dashboard.

Usage
-----
# Normal daily run:
    .venv/bin/python scripts/run_benchmark_dashboard_g5.py

# Print report without writing:
    .venv/bin/python scripts/run_benchmark_dashboard_g5.py --dry-run

# Restrict chart window:
    .venv/bin/python scripts/run_benchmark_dashboard_g5.py --start-date 2022-01-01
"""
import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.rl.audit_trail import query_decisions
from src.rl.nav_generator import load_b5_nav_backtest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPORT_FILE   = REPO_ROOT / "artifacts" / "reports" / "phase_g5_benchmark_dashboard.md"
RL_NAV_FILE   = REPO_ROOT / "data" / "switching" / "nav_rl_backtest.parquet"
FLAGS_FILE    = REPO_ROOT / "data" / "drift" / "flags.parquet"
RAW_DIR       = REPO_ROOT / "data" / "raw"

ROLLING_WINDOW = 63
ANN_FACTOR     = 252


# ── Data loaders ──────────────────────────────────────────────────────────────

def _load_price_series(ticker: str) -> pd.Series:
    path = RAW_DIR / f"{ticker}.parquet"
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    return df["adj_close"].rename(ticker)


def _load_rl_nav() -> pd.Series:
    df = pd.read_parquet(RL_NAV_FILE)
    df["as_of_date"] = pd.to_datetime(df["as_of_date"])
    nav = df.set_index("as_of_date")["nav"]
    logger.info("RL NAV loaded: %d records, %s → %s",
                len(nav), nav.index.min().date(), nav.index.max().date())
    return nav


def _build_nav_from_prices(price: pd.Series, name: str) -> pd.Series:
    """Normalize a price series to NAV starting at 1.0."""
    ret = price.pct_change().fillna(0.0)
    nav = (1.0 + ret).cumprod()
    nav.iloc[0] = 1.0
    return nav.rename(name)


def _build_6040_nav(spy_prices: pd.Series, tlt_prices: pd.Series) -> pd.Series:
    """60/40 portfolio: daily-rebalanced blend of SPY and TLT."""
    common = spy_prices.index.intersection(tlt_prices.index)
    spy = spy_prices.loc[common]
    tlt = tlt_prices.loc[common]
    ret = 0.60 * spy.pct_change().fillna(0.0) + 0.40 * tlt.pct_change().fillna(0.0)
    nav = (1.0 + ret).cumprod()
    nav.iloc[0] = 1.0
    return nav.rename("60/40")


def _splice_live_rl_nav(backtest_nav: pd.Series, audit_df: pd.DataFrame) -> pd.Series:
    """Append live audit NAV records after the backtest end date."""
    if audit_df.empty:
        return backtest_nav
    live = audit_df.set_index("as_of_date")["nav"].sort_index()
    live = live[live.index > backtest_nav.index.max()]
    if live.empty:
        return backtest_nav
    # Scale live NAV to continue from the backtest endpoint
    scale = backtest_nav.iloc[-1] / live.iloc[0]
    live = live * scale
    combined = pd.concat([backtest_nav, live])
    combined = combined[~combined.index.duplicated(keep="last")].sort_index()
    logger.info("Spliced %d live RL NAV records after backtest end", len(live))
    return combined


# ── Rolling metrics ───────────────────────────────────────────────────────────

def _rolling_sharpe(nav: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    ret = nav.pct_change()
    roll_mean = ret.rolling(window).mean() * ANN_FACTOR
    roll_std  = ret.rolling(window).std() * np.sqrt(ANN_FACTOR)
    return (roll_mean / roll_std.replace(0, np.nan)).rename(f"sharpe_{nav.name}")


def _rolling_maxdd(nav: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    def _mdd(x):
        peak = np.maximum.accumulate(x)
        dd = (x - peak) / peak
        return dd.min()
    return nav.rolling(window).apply(_mdd, raw=True).rename(f"maxdd_{nav.name}")


def _full_period_metrics(nav: pd.Series) -> dict:
    ret = nav.pct_change().dropna()
    total_ret   = nav.iloc[-1] / nav.iloc[0] - 1.0
    n_years     = len(ret) / ANN_FACTOR
    ann_ret     = (1.0 + total_ret) ** (1.0 / n_years) - 1.0 if n_years > 0 else np.nan
    ann_vol     = ret.std() * np.sqrt(ANN_FACTOR)
    sharpe      = ann_ret / ann_vol if ann_vol > 0 else np.nan
    running_max = nav.cummax()
    mdd         = ((nav - running_max) / running_max).min()
    return {
        "total_ret": total_ret,
        "ann_ret":   ann_ret,
        "ann_vol":   ann_vol,
        "sharpe":    sharpe,
        "mdd":       mdd,
    }


# ── Report builder ────────────────────────────────────────────────────────────

def _fmt_pct(v) -> str:
    return f"{v * 100:.1f}%" if not (isinstance(v, float) and np.isnan(v)) else "N/A"


def _fmt_f(v, decimals=3) -> str:
    return f"{v:.{decimals}f}" if not (isinstance(v, float) and np.isnan(v)) else "N/A"


def build_report(
    navs: dict[str, pd.Series],
    roll_sharpe: dict[str, pd.Series],
    roll_maxdd: dict[str, pd.Series],
    audit_df: pd.DataFrame,
    flags_df: pd.DataFrame,
    start_date: str,
) -> str:
    ts       = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    as_of    = max(nav.index.max() for nav in navs.values()).date()
    series   = list(navs.keys())

    lines = [
        "# Phase G.5 — Benchmark Dashboard",
        "",
        f"**As-of:** {as_of}  ",
        f"**Generated:** {ts}  ",
        f"**Chart window:** {start_date} →  ",
        "",
        "---",
        "",
        "## Performance Summary (Full Period)",
        "",
        "| Series | Start | End | Total Return | Ann. Return | Ann. Vol | Sharpe | Max DD |",
        "|--------|-------|-----|-------------|------------|---------|--------|--------|",
    ]
    for name in series:
        nav  = navs[name]
        m    = _full_period_metrics(nav)
        start = nav.index.min().date()
        end   = nav.index.max().date()
        lines.append(
            f"| {name} | {start} | {end} | {_fmt_pct(m['total_ret'])} | "
            f"{_fmt_pct(m['ann_ret'])} | {_fmt_pct(m['ann_vol'])} | "
            f"{_fmt_f(m['sharpe'])} | {_fmt_pct(m['mdd'])} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Rolling 63-Day Metrics (Most Recent)",
        "",
        "| Series | Rolling Sharpe | Rolling MaxDD |",
        "|--------|---------------|--------------|",
    ]
    for name in series:
        rs = roll_sharpe.get(f"sharpe_{name}")
        rm = roll_maxdd.get(f"maxdd_{name}")
        rs_val = _fmt_f(rs.dropna().iloc[-1]) if rs is not None and not rs.dropna().empty else "N/A"
        rm_val = _fmt_pct(rm.dropna().iloc[-1]) if rm is not None and not rm.dropna().empty else "N/A"
        lines.append(f"| {name} | {rs_val} | {rm_val} |")

    # ── Regime posture from audit trail ───────────────────────────────────────
    lines += [
        "",
        "---",
        "",
        "## Regime Posture (Last 10 Records)",
        "",
    ]
    if audit_df.empty:
        lines.append("_No audit trail records — run `run_prod_signal.py` to populate._")
    else:
        cols = ["as_of_date", "mode", "equity_frac", "trend_frac", "cash_frac", "stress_score", "nav"]
        recent = audit_df[cols].tail(10)
        lines += [
            "| Date | Mode | Equity | Trend | Cash | Stress | NAV |",
            "|------|------|--------|-------|------|--------|-----|",
        ]
        for _, row in recent.iterrows():
            lines.append(
                f"| {row['as_of_date'].date()} | `{row['mode']}` | "
                f"{_fmt_pct(row['equity_frac'])} | {_fmt_pct(row['trend_frac'])} | "
                f"{_fmt_pct(row['cash_frac'])} | {_fmt_f(row['stress_score'], 3)} | "
                f"{_fmt_f(row['nav'], 4)} |"
            )

    # ── Drift flags ───────────────────────────────────────────────────────────
    lines += [
        "",
        "---",
        "",
        "## Active Drift Flags (G.3 — Latest Run)",
        "",
    ]
    flag_names = ["sharpe_degradation", "drawdown_excess", "cash_trap", "feature_psi", "stress_breach"]
    if flags_df.empty:
        lines.append("_No flag history — run `run_drift_monitor_g3.py` to populate._")
    else:
        latest = flags_df.iloc[-1]
        alert  = bool(latest.get("alert_active", False))
        as_of_flag = latest.get("as_of_date", "N/A")
        alert_icon = "⚠️ **ALERT ACTIVE**" if alert else "✅ No Alert"
        lines += [
            f"**As-of:** {as_of_flag}  ",
            f"**Status:** {alert_icon}",
            "",
            "| Status | Flag | Value |",
            "|--------|------|-------|",
        ]
        for flag in flag_names:
            active = bool(latest.get(f"flag_{flag}", False))
            val    = latest.get(f"val_{flag}", float("nan"))
            icon   = "🔴" if active else "🟢"
            val_s  = f"{val:.4f}" if isinstance(val, float) and not np.isnan(val) else "N/A"
            lines.append(f"| {icon} | `{flag}` | {val_s} |")

    lines += ["", "---", ""]
    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Phase G.5 — Benchmark Dashboard")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print report to stdout; do not write files")
    parser.add_argument("--start-date", default="2020-01-01",
                        help="Chart window start date (default: 2020-01-01)")
    args = parser.parse_args()

    start = pd.Timestamp(args.start_date)

    # ── Load NAV series ───────────────────────────────────────────────────────
    logger.info("Loading B.5 NAV backtest …")
    b5_nav = load_b5_nav_backtest()

    logger.info("Loading RL NAV backtest …")
    rl_nav_bt = _load_rl_nav()

    logger.info("Loading audit trail …")
    audit_df = query_decisions()
    if not audit_df.empty:
        audit_df = audit_df.sort_values("as_of_date").reset_index(drop=True)

    rl_nav = _splice_live_rl_nav(rl_nav_bt, audit_df)

    logger.info("Loading SPY and TLT prices …")
    spy_prices = _load_price_series("SPY")
    tlt_prices = _load_price_series("TLT")

    spy_nav  = _build_nav_from_prices(spy_prices, "SPY")
    nav_6040 = _build_6040_nav(spy_prices, tlt_prices)

    # ── Align to common window ────────────────────────────────────────────────
    common_start = max(start,
                       b5_nav.index.min(),
                       rl_nav.index.min(),
                       spy_nav.index.min(),
                       nav_6040.index.min())
    common_end   = min(b5_nav.index.max(),
                       rl_nav.index.max(),
                       spy_nav.index.max(),
                       nav_6040.index.max())

    def _trim(s: pd.Series) -> pd.Series:
        s = s.loc[common_start:common_end]
        return s / s.iloc[0]  # rebase to 1.0 at common start

    navs = {
        "RL (E.7)": _trim(rl_nav),
        "B.5-only": _trim(b5_nav),
        "SPY":      _trim(spy_nav),
        "60/40":    _trim(nav_6040),
    }
    logger.info("Common window: %s → %s", common_start.date(), common_end.date())

    # ── Rolling metrics ───────────────────────────────────────────────────────
    roll_sharpe = {f"sharpe_{k}": _rolling_sharpe(v) for k, v in navs.items()}
    roll_maxdd  = {f"maxdd_{k}": _rolling_maxdd(v) for k, v in navs.items()}

    # ── Load drift flags ──────────────────────────────────────────────────────
    if FLAGS_FILE.exists():
        flags_df = pd.read_parquet(FLAGS_FILE).sort_values("run_timestamp").reset_index(drop=True)
    else:
        flags_df = pd.DataFrame()

    # ── Build and emit report ─────────────────────────────────────────────────
    report = build_report(navs, roll_sharpe, roll_maxdd, audit_df, flags_df, args.start_date)

    if args.dry_run:
        print(report)
        print("✅ G.5 GATE (dry-run): PASS — report generated successfully")
        return 0

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report)
    logger.info("Dashboard written to %s", REPORT_FILE)

    print(f"\n✅ G.5 GATE: PASS — Dashboard written to {REPORT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
