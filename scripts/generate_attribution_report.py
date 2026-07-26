"""Weekly attribution report for Phase H paper trading.

For each completed rebalance period, decomposes portfolio return into:
  - Equity sleeve contribution
  - Trend sleeve contribution (TLT/GLD/UUP)
  - Cash contribution
  - RL allocation decision effect (vs B.5 counterfactual)
  - Stock selection effect (equity basket vs SPY)

All returns use actual prices from data/raw/. Writes to
docs/attribution_report.md and prints a summary table.

Usage:
    .venv/bin/python scripts/generate_attribution_report.py
"""
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RAW_DIR = REPO_ROOT / "data" / "raw"
ALLOC_DIR = REPO_ROOT / "data" / "allocations"
OUT_PATH = REPO_ROOT / "docs" / "attribution_report.md"

EQUITY_TICKERS = [
    "AMD", "APH", "APP", "ARES", "AXON", "COHR", "COIN", "CVNA", "DDOG",
    "EL", "EPAM", "HOOD", "INTC", "LITE", "MU", "NCLH", "PLTR", "SMCI",
    "SNDK", "XYZ",
]
TREND_TICKERS = ["TLT", "GLD", "UUP"]
BENCHMARK = "SPY"


def _price(ticker: str, date_str: str) -> float | None:
    path = RAW_DIR / f"{ticker}.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    df.index = pd.to_datetime(df.index)
    dt = pd.to_datetime(date_str)
    available = df[df.index <= dt]
    if available.empty:
        return None
    return float(available.iloc[-1]["close"])


def _period_return(ticker: str, start: str, end: str) -> float | None:
    p0, p1 = _price(ticker, start), _price(ticker, end)
    if p0 and p1 and p0 > 0:
        return p1 / p0 - 1
    return None


def _b5_equity(stress: float) -> float:
    """Approximate B.5 equity fraction from stress score."""
    return max(0.25, min(0.65, 0.65 - 0.30 * stress))


def _load_alloc(date_str: str) -> dict:
    path = ALLOC_DIR / f"{date_str}.json"
    with open(path) as f:
        return json.load(f)


def compute_attribution(entry: str, exit_date: str, label: str) -> dict | None:
    """Compute full attribution for one hold period."""
    alloc = _load_alloc(entry)
    eq_frac = alloc["equity_frac"]
    tr_frac = alloc["trend_frac"]
    ca_frac = alloc["cash_frac"]
    stress = alloc["stress_score"]
    # trend_weights keys are the tickers held; values are portfolio-level weights
    # (not sleeve-level fractions). Normalize to sleeve fractions.
    raw_trend_weights = alloc.get("trend_weights", {"TLT": tr_frac})

    # ── Equity sleeve ──────────────────────────────────────────────────
    eq_returns = []
    eq_ticker_returns = {}
    for t in EQUITY_TICKERS:
        r = _period_return(t, entry, exit_date)
        if r is not None:
            eq_returns.append(r)
            eq_ticker_returns[t] = r
    eq_sleeve_return = sum(eq_returns) / len(eq_returns) if eq_returns else 0.0
    eq_contribution = eq_frac * eq_sleeve_return

    # ── Trend sleeve ───────────────────────────────────────────────────
    # Normalize raw_trend_weights (portfolio-level) to sleeve-level fractions
    total_raw = sum(raw_trend_weights.values()) if raw_trend_weights else tr_frac
    tr_sleeve_return = 0.0
    tr_ticker_returns = {}
    for t, w in raw_trend_weights.items():
        r = _period_return(t, entry, exit_date)
        if r is not None:
            sleeve_frac = w / total_raw if total_raw > 0 else 0
            tr_sleeve_return += sleeve_frac * r
            tr_ticker_returns[t] = r
    tr_contribution = tr_frac * tr_sleeve_return

    # ── Cash ───────────────────────────────────────────────────────────
    ca_contribution = 0.0  # paper account earns no interest

    # ── Total RL portfolio return ───────────────────────────────────────
    rl_total = eq_contribution + tr_contribution + ca_contribution

    # ── B.5 counterfactual ─────────────────────────────────────────────
    # Same stocks, same trend asset(s), but B.5 sleeve weights
    b5_eq = _b5_equity(stress)
    b5_tr = 1.0 - b5_eq          # B.5 holds no cash at low stress
    b5_ca = 0.0
    b5_total = b5_eq * eq_sleeve_return + b5_tr * tr_sleeve_return

    # RL allocation decision effect = RL total - B.5 total
    # (holding everything else constant)
    allocation_effect = rl_total - b5_total

    # ── Stock selection effect ─────────────────────────────────────────
    # How did the 20-stock basket do vs SPY?
    spy_return = _period_return(BENCHMARK, entry, exit_date) or 0.0
    stock_selection = eq_sleeve_return - spy_return
    # Weight by equity fraction to get portfolio-level contribution
    stock_selection_contribution = eq_frac * stock_selection

    # ── Best/worst performers ──────────────────────────────────────────
    sorted_eq = sorted(eq_ticker_returns.items(), key=lambda x: x[1])
    worst3 = sorted_eq[:3]
    best3 = sorted_eq[-3:][::-1]

    return {
        "label": label,
        "entry": entry,
        "exit": exit_date,
        "stress": stress,
        # Sleeve fractions
        "eq_frac": eq_frac,
        "tr_frac": tr_frac,
        "ca_frac": ca_frac,
        # Returns
        "eq_sleeve_return": eq_sleeve_return,
        "tr_sleeve_return": tr_sleeve_return,
        "spy_return": spy_return,
        # Contributions
        "eq_contribution": eq_contribution,
        "tr_contribution": tr_contribution,
        "ca_contribution": ca_contribution,
        "rl_total": rl_total,
        # Attribution
        "b5_total": b5_total,
        "b5_eq": b5_eq,
        "b5_tr": b5_tr,
        "allocation_effect": allocation_effect,
        "stock_selection": stock_selection,
        "stock_selection_contribution": stock_selection_contribution,
        # Detail
        "trend_ticker_returns": tr_ticker_returns,
        "best3": best3,
        "worst3": worst3,
    }


def format_pct(v: float, sign: bool = True) -> str:
    s = f"{v * 100:+.2f}%" if sign else f"{v * 100:.2f}%"
    return s


def render_period(a: dict) -> str:
    lines = []
    lines.append(f"\n### {a['label']} — {a['entry']} → {a['exit']}")
    lines.append("")
    lines.append(f"**Stress score at entry:** {a['stress']:.3f} | "
                 f"**Equity:** {a['eq_frac']*100:.1f}% | "
                 f"**Trend:** {a['tr_frac']*100:.1f}% | "
                 f"**Cash:** {a['ca_frac']*100:.1f}%")
    lines.append("")

    # Main attribution table
    lines.append("#### Return Attribution")
    lines.append("")
    lines.append("| Component | Return | Weight | Contribution |")
    lines.append("|-----------|--------|--------|--------------|")
    lines.append(f"| Equity sleeve ({len(EQUITY_TICKERS)} stocks, equal-wt) "
                 f"| {format_pct(a['eq_sleeve_return'])} "
                 f"| {a['eq_frac']*100:.1f}% "
                 f"| **{format_pct(a['eq_contribution'])}** |")

    # Trend breakdown
    tr_detail = ", ".join(
        f"{t}: {format_pct(r)}"
        for t, r in a["trend_ticker_returns"].items()
    )
    lines.append(f"| Trend sleeve ({tr_detail}) "
                 f"| {format_pct(a['tr_sleeve_return'])} "
                 f"| {a['tr_frac']*100:.1f}% "
                 f"| **{format_pct(a['tr_contribution'])}** |")
    lines.append(f"| Cash | +0.00% | {a['ca_frac']*100:.1f}% | **+0.00%** |")
    lines.append(f"| **Total portfolio return** | | | **{format_pct(a['rl_total'])}** |")
    lines.append(f"| SPY benchmark | {format_pct(a['spy_return'])} | — | — |")
    lines.append("")

    # Decision decomposition
    lines.append("#### Decision Decomposition")
    lines.append("")
    lines.append("| Effect | Value | Interpretation |")
    lines.append("|--------|-------|---------------|")
    alloc_sign = "✅" if a["allocation_effect"] >= 0 else "❌"
    sel_sign = "✅" if a["stock_selection_contribution"] >= 0 else "❌"
    lines.append(
        f"| RL allocation vs B.5 | {format_pct(a['allocation_effect'])} | {alloc_sign} "
        f"RL held {a['eq_frac']*100:.0f}% eq vs B.5 ~{a['b5_eq']*100:.0f}% eq |"
    )
    lines.append(
        f"| Stock selection vs SPY | {format_pct(a['stock_selection_contribution'])} | {sel_sign} "
        f"Basket {format_pct(a['eq_sleeve_return'])} vs SPY {format_pct(a['spy_return'])} |"
    )
    lines.append(
        f"| B.5 counterfactual return | {format_pct(a['b5_total'])} | "
        f"B.5 would: {a['b5_eq']*100:.0f}% eq / {a['b5_tr']*100:.0f}% trend |"
    )
    lines.append("")

    # Top/bottom performers
    lines.append("#### Equity Sleeve: Top & Bottom 3")
    lines.append("")
    lines.append("| Rank | Ticker | Return | Contribution to equity sleeve |")
    lines.append("|------|--------|--------|-------------------------------|")
    n = len(EQUITY_TICKERS)
    for t, r in a["best3"]:
        lines.append(f"| 🟢 Best | {t} | {format_pct(r)} | {format_pct(r/n)} |")
    for t, r in a["worst3"]:
        lines.append(f"| 🔴 Worst | {t} | {format_pct(r)} | {format_pct(r/n)} |")
    lines.append("")
    lines.append("---")
    return "\n".join(lines)


def main() -> None:
    rebalances = [
        ("R1", "2026-05-26", "2026-06-09"),
        ("R2", "2026-06-09", "2026-06-23"),
        ("R3", "2026-06-23", "2026-07-07"),
        ("R4", "2026-07-07", "2026-07-21"),
    ]

    results = []
    for label, entry, exit_date in rebalances:
        logger.info("Computing attribution for %s (%s → %s)", label, entry, exit_date)
        a = compute_attribution(entry, exit_date, label)
        if a:
            results.append(a)

    # Summary table
    summary_lines = [
        "## Attribution Summary — All Periods",
        "",
        "| Period | Eq contrib | Trend contrib | Cash | RL vs B.5 | Stock sel | Total | SPY |",
        "|--------|-----------|--------------|------|-----------|-----------|-------|-----|",
    ]
    for a in results:
        summary_lines.append(
            f"| {a['label']} {a['entry']}→{a['exit']} "
            f"| {format_pct(a['eq_contribution'])} "
            f"| {format_pct(a['tr_contribution'])} "
            f"| +0.00% "
            f"| {format_pct(a['allocation_effect'])} "
            f"| {format_pct(a['stock_selection_contribution'])} "
            f"| {format_pct(a['rl_total'])} "
            f"| {format_pct(a['spy_return'])} |"
        )
    summary_lines.append("")

    # Cumulative (T=0 bootstrap 2026-05-12 → R1 entry 2026-05-26, then each period)
    cum_rl = 1.0
    cum_spy = 1.0
    t0_alloc = _load_alloc("2026-05-12")
    t0_eq_f = t0_alloc["equity_frac"]
    t0_tr_f = t0_alloc["trend_frac"]
    t0_eq_rets = [_period_return(t, "2026-05-12", "2026-05-26") or 0 for t in EQUITY_TICKERS]
    t0_eq_ret = sum(t0_eq_rets) / len(t0_eq_rets)
    t0_tlt = _period_return("TLT", "2026-05-12", "2026-05-26") or 0
    t0_total = t0_eq_f * t0_eq_ret + t0_tr_f * t0_tlt
    cum_rl *= (1 + t0_total)
    cum_spy *= (1 + (_period_return(BENCHMARK, "2026-05-12", "2026-05-26") or 0))
    for a in results:
        cum_rl *= (1 + a["rl_total"])
        cum_spy *= (1 + a["spy_return"])

    summary_lines += [
        f"**Cumulative RL return (T=0 → R5 entry):** {format_pct(cum_rl - 1)}  ",
        f"**Cumulative SPY return:** {format_pct(cum_spy - 1)}  ",
        f"**Active return vs SPY:** {format_pct(cum_rl - cum_spy)}",
        "",
    ]

    # Render full report
    header = [
        "# Phase H — Weekly Attribution Report",
        "",
        "> Generated from real prices in `data/raw/`. Updated each time `generate_attribution_report.py` runs.",
        ">",
        "> **Framework:**",
        "> - **Equity contribution** = sleeve return × equity weight",
        "> - **Trend contribution** = weighted return of TLT/GLD/UUP × trend weight",
        "> - **RL allocation effect** = actual portfolio return − B.5 counterfactual return",
        ">   (same assets, B.5 sleeve weights at same stress level)",
        "> - **Stock selection effect** = (equity basket return − SPY) × equity weight",
        ">   (basket is fixed 20-name equal-weight universe; measures quality of the universe pick, not rebalance decisions)",
        "",
        "---",
        "",
    ]

    body = "\n".join(header) + "\n".join(summary_lines)
    for a in results:
        body += render_period(a)

    OUT_PATH.write_text(body)
    logger.info("Attribution report written to %s", OUT_PATH)

    # Print summary to stdout
    print("\n" + "=" * 70)
    print("ATTRIBUTION SUMMARY")
    print("=" * 70)
    print(f"{'Period':<22} {'Eq':>7} {'Trend':>7} {'RL vs B5':>9} {'StockSel':>9} {'Total':>8} {'SPY':>8}")
    print("-" * 70)
    for a in results:
        print(
            f"{a['label']} {a['entry'][:10]}"
            f"  {format_pct(a['eq_contribution']):>7}"
            f"  {format_pct(a['tr_contribution']):>7}"
            f"  {format_pct(a['allocation_effect']):>9}"
            f"  {format_pct(a['stock_selection_contribution']):>9}"
            f"  {format_pct(a['rl_total']):>8}"
            f"  {format_pct(a['spy_return']):>8}"
        )
    print("-" * 70)
    print(f"{'Cumulative (incl T=0→R1)':<22}  {'':>7}  {'':>7}  {'':>9}  {'':>9}"
          f"  {format_pct(cum_rl - 1):>8}  {format_pct(cum_spy - 1):>8}")
    print("=" * 70)


if __name__ == "__main__":
    main()
