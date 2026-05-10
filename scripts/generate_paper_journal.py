"""Phase H — Generate human-readable paper trading journal.

Reads all daily data artifacts and writes/updates:
  docs/paper_trading_journal.md

One dated section per run day. Sections are prepended (newest first).
Safe to re-run — existing sections for the same date are replaced.

Usage
-----
    .venv/bin/python scripts/generate_paper_journal.py
    .venv/bin/python scripts/generate_paper_journal.py --date 2026-05-10
"""
import argparse
import json
import logging
import sys
from datetime import date as date_type
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PT_DIR = REPO_ROOT / "data" / "paper_trading"
ALLOC_DIR = REPO_ROOT / "data" / "allocations"
JOURNAL_PATH = REPO_ROOT / "docs" / "paper_trading_journal.md"
DATED_DIR = REPO_ROOT / "docs" / "paper_trading"  # per-date files: YYYY-MM-DD.md


def _flag(val: bool) -> str:
    return "🚨 YES" if val else "✅ no"


def _pct(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{float(v)*100:.2f}%"


def _bps(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"{float(v):.1f} bps"


def _usd(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return f"${float(v):,.2f}"


def build_day_section(run_date: str) -> str:
    lines: list[str] = []
    lines.append(f"## {run_date}")
    lines.append("")

    # --- Ops log (last entry for this date) ---
    ops_entry = None
    ops_log_path = PT_DIR / "daily_ops_log.jsonl"
    if ops_log_path.exists():
        entries = [json.loads(l) for l in ops_log_path.read_text().strip().splitlines() if l.strip()]
        day_entries = [e for e in entries if e.get("date") == run_date]
        # use last entry (final successful run)
        clean = [e for e in day_entries if not e.get("pipeline_errors")]
        ops_entry = clean[-1] if clean else (day_entries[-1] if day_entries else None)

    if ops_entry:
        mode = ops_entry.get("mode", "unknown")
        is_rebal = ops_entry.get("is_rebalance", False)
        signal_ok = ops_entry.get("signal_ok", False)
        drift_flags = ops_entry.get("drift_flags_active", 0)
        errors = ops_entry.get("pipeline_errors", [])

        lines.append("### Pipeline")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| Mode | `{mode}` |")
        lines.append(f"| Rebalance day | {'✅ YES' if is_rebal else 'no'} |")
        lines.append(f"| Signal | {'✅ OK' if signal_ok else '🚨 FAILED'} |")
        lines.append(f"| Drift flags active | {_flag(drift_flags >= 2)} ({drift_flags}) |")
        lines.append(f"| Pipeline errors | {'none' if not errors else str(len(errors))} |")
        if errors:
            for e in errors:
                lines.append(f"> ⚠️ {e}")
        lines.append("")

    # --- Allocation fractions ---
    alloc_path = ALLOC_DIR / f"{run_date}.json"
    alloc = None
    if alloc_path.exists():
        with open(alloc_path) as f:
            alloc = json.load(f)
        lines.append("### Allocation")
        lines.append("| Sleeve | Weight |")
        lines.append("|--------|--------|")
        lines.append(f"| Equity | {_pct(alloc.get('equity_frac'))} |")
        lines.append(f"| Trend | {_pct(alloc.get('trend_frac'))} |")
        lines.append(f"| Cash | {_pct(alloc.get('cash_frac'))} |")
        tw = alloc.get("trend_weights", {})
        if tw:
            lines.append("")
            lines.append("**Trend breakdown:**")
            for ticker, w in tw.items():
                if w > 0:
                    lines.append(f"- {ticker}: {_pct(w)}")
        lines.append("")

    # --- Positions ---
    pos_path = PT_DIR / f"positions_{(pd.Timestamp(run_date) + pd.offsets.BDay(1)).strftime('%Y-%m-%d')}.parquet"
    if not pos_path.exists():
        pos_path = PT_DIR / "positions_latest.parquet"

    if pos_path.exists():
        pos_all = pd.read_parquet(pos_path)
        cash_row = pos_all[pos_all["ticker"] == "__CASH__"]
        pos = pos_all[pos_all["ticker"] != "__CASH__"].sort_values("market_value", ascending=False)
        total_invested = pos["market_value"].sum()
        cash_mv = float(cash_row["market_value"].iloc[0]) if not cash_row.empty else 0.0
        total_nav = total_invested + cash_mv
        max_drift = pos["weight_drift_pp"].abs().max() if not pos.empty else 0.0
        lines.append("### Portfolio Snapshot")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Holdings | {len(pos)} positions + cash |")
        lines.append(f"| Invested | {_usd(total_invested)} ({total_invested/total_nav*100:.1f}% of NAV) |")
        lines.append(f"| Cash | {_usd(cash_mv)} ({cash_mv/total_nav*100:.1f}% of NAV) |")
        lines.append(f"| Total NAV | {_usd(total_nav)} |")
        lines.append(f"| Max weight drift | {max_drift:.2f} pp (H-4 gate: 5.0 pp) |")
        lines.append("")
        lines.append("| Ticker | Sleeve | Shares | Price | Mkt Value | Port Wt | Target Wt | Drift pp |")
        lines.append("|--------|--------|--------|-------|-----------|---------|-----------|----------|")
        for _, r in pos.iterrows():
            drift_flag = " 🚨" if abs(r["weight_drift_pp"]) > 5.0 else ""
            lines.append(
                f"| {r['ticker']} | {r['sleeve']} | {r['shares_held']:.4f} | "
                f"${r['current_price']:.2f} | {_usd(r['market_value'])} | "
                f"{r['portfolio_weight']*100:.2f}% | {r['target_weight']*100:.2f}% | "
                f"{r['weight_drift_pp']:+.3f}{drift_flag} |"
            )
        lines.append(f"| __CASH__ | cash | — | — | {_usd(cash_mv)} | {cash_mv/total_nav*100:.2f}% | {cash_mv/total_nav*100:.2f}% | +0.000 |")
        lines.append("")

    # --- Orders ---
    orders_path = PT_DIR / f"orders_{run_date}.csv"
    if orders_path.exists():
        orders = pd.read_csv(orders_path)
        active = orders[orders["action"] != "hold"]
        if not active.empty:
            total_notional = active["notional_usd"].sum()
            lines.append("### Orders")
            lines.append(f"| Metric | Value |")
            lines.append(f"|--------|-------|")
            lines.append(f"| Total orders | {len(active)} ({(orders['action']=='buy').sum()} buys, {(orders['action']=='sell').sum()} sells) |")
            lines.append(f"| Total notional | {_usd(total_notional)} |")
            lines.append(f"| Estimated turnover | {total_notional/50000*100:.1f}% |")
            lines.append("")
            lines.append("| Ticker | Action | Delta Shares | Est Price | Notional |")
            lines.append("|--------|--------|-------------|-----------|----------|")
            for _, r in active.iterrows():
                lines.append(
                    f"| {r['ticker']} | {r['action']} | {r['delta_shares']:+.4f} | "
                    f"${r['est_fill_price']:.2f} | {_usd(r['notional_usd'])} |"
                )
            lines.append("")

    # --- Fills & slippage ---
    fills_path = PT_DIR / f"fills_{run_date}.csv"
    if fills_path.exists():
        fills = pd.read_csv(fills_path)
        if not fills.empty:
            avg_slip = fills["actual_slippage_bps"].abs().mean()
            flagged = int(fills["slippage_flagged"].sum())
            lines.append("### Fills & Slippage")
            lines.append(f"| Metric | Value | H-2 Gate (< 20 bps avg) |")
            lines.append(f"|--------|-------|------------------------|")
            lines.append(f"| Trades filled | {len(fills)} | — |")
            lines.append(f"| Avg slippage | {avg_slip:.1f} bps | {'✅ PASS' if avg_slip < 20 else '⚠️ above target'} |")
            lines.append(f"| Flagged trades (> 30 bps) | {flagged} / {len(fills)} | — |")
            lines.append("")
            lines.append("| Ticker | Action | Fill Price | Signal Close | Slippage bps | Flagged |")
            lines.append("|--------|--------|-----------|-------------|-------------|---------|")
            for _, r in fills.iterrows():
                flag_icon = "🚨" if r["slippage_flagged"] else "✅"
                lines.append(
                    f"| {r['ticker']} | {r['action']} | ${r['fill_price']:.2f} | "
                    f"${r['signal_close_price']:.2f} | {r['actual_slippage_bps']:+.1f} | {flag_icon} |"
                )
            lines.append("")

    # --- Gate status summary ---
    lines.append("### H-Gate Status (running)")
    lines.append("| Gate | Metric | Status |")
    lines.append("|------|--------|--------|")
    if ops_entry:
        lines.append(f"| H-1 Pipeline reliability | Errors today: {len(ops_entry.get('pipeline_errors',[]))} | {'✅' if not ops_entry.get('pipeline_errors') else '⚠️'} |")
    if fills_path.exists() and not fills.empty:
        lines.append(f"| H-2 Fill slippage | {avg_slip:.1f} bps avg | {'✅' if avg_slip < 20 else '⚠️ T=0 artifact'} |")
    if pos_path.exists() and not pos.empty:
        lines.append(f"| H-4 Weight drift | {max_drift:.2f} pp max | {'✅' if max_drift < 5.0 else '🚨'} |")
    if ops_entry:
        lines.append(f"| H-5 RL mode | {ops_entry.get('mode','?')} | {'✅' if ops_entry.get('mode') == 'rl_e7' else '⚠️'} |")
        lines.append(f"| H-7 Drift flags | {ops_entry.get('drift_flags_active', 0)} active | {'✅' if ops_entry.get('drift_flags_active', 0) < 2 else '🚨'} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def load_existing_journal() -> tuple[str, dict[str, tuple[int, int]]]:
    """Return (full text, {date: (start_line, end_line)}) for existing dated sections."""
    if not JOURNAL_PATH.exists():
        return "", {}
    text = JOURNAL_PATH.read_text()
    sections: dict[str, tuple[int, int]] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("## 20"):
            section_date = lines[i][3:].strip()
            start = i
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## 20"):
                j += 1
            sections[section_date] = (start, j)
            i = j
        else:
            i += 1
    return text, sections


def update_journal(run_date: str, section_text: str) -> None:
    text, sections = load_existing_journal()
    lines = text.splitlines() if text else []

    if run_date in sections:
        # replace existing section
        start, end = sections[run_date]
        new_section_lines = section_text.rstrip().splitlines()
        lines = lines[:start] + new_section_lines + [""] + lines[end:]
        logger.info("Replaced existing journal section for %s", run_date)
    else:
        # prepend after header (insert before first ## 20xx section, or after header block)
        new_section_lines = section_text.rstrip().splitlines()
        first_section = next((i for i, l in enumerate(lines) if l.startswith("## 20")), len(lines))
        lines = lines[:first_section] + new_section_lines + [""] + lines[first_section:]
        logger.info("Prepended new journal section for %s", run_date)

    JOURNAL_PATH.write_text("\n".join(lines) + "\n")


def ensure_header() -> None:
    if JOURNAL_PATH.exists():
        return
    JOURNAL_PATH.write_text(
        "# Phase H — Paper Trading Journal\n\n"
        "> **Portfolio:** $50,000 NAV | Broker: Alpaca paper | Config: v H.0.0\n"
        "> **Rebalance cadence:** every 14 days | **Mode:** rl_e7 (dual-mode switching active)\n"
        "> **Gates:** H-1 pipeline · H-2 slippage <20 bps · H-3 turnover <35% · "
        "H-4 drift <5pp · H-5 RL mode · H-6 Sharpe · H-7 data parity · H-8 audit trail\n\n"
        "Newest entries at the top. Updated automatically by `scripts/generate_paper_journal.py`.\n\n"
        "---\n\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paper trading journal")
    parser.add_argument("--date", default=None, help="Date to generate entry for (default: all available dates)")
    args = parser.parse_args()

    ensure_header()

    if args.date:
        dates = [args.date]
    else:
        # discover all dates from ops log
        ops_log_path = PT_DIR / "daily_ops_log.jsonl"
        if not ops_log_path.exists():
            logger.error("No ops log found at %s", ops_log_path)
            sys.exit(1)
        entries = [json.loads(l) for l in ops_log_path.read_text().strip().splitlines() if l.strip()]
        # deduplicate, keep unique dates, sort ascending so prepend results in newest-first
        seen = set()
        dates = []
        for e in entries:
            d = e.get("date")
            if d and d not in seen:
                seen.add(d)
                dates.append(d)
        dates.sort()

    DATED_DIR.mkdir(parents=True, exist_ok=True)

    for d in dates:
        section = build_day_section(d)
        update_journal(d, section)

        # Write standalone dated file: docs/paper_trading/YYYY-MM-DD.md
        dated_path = DATED_DIR / f"{d}.md"
        dated_path.write_text(
            f"# Paper Trading — {d}\n\n"
            f"> [Back to full journal](../paper_trading_journal.md)\n\n"
            + section
        )
        logger.info("Dated file written: %s", dated_path)

    logger.info("Journal written to %s", JOURNAL_PATH)


if __name__ == "__main__":
    main()
