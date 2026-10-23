"""Where does the promoted E.7 RL policy rank inside the Phase E random-policy distribution?

Uses only tracked report CSVs (no market data needed):
  artifacts/reports/e7_random_distribution.csv   50 random bounded policies, holdout 2019-2026
  artifacts/reports/e7_policy_comparison.csv     B.5 / RL no-op / rule-based / trained RL

Usage:
    python3 scripts/analyze_rl_vs_random.py > artifacts/reports/rl_vs_random_significance.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPORTS = Path(__file__).resolve().parents[1] / "artifacts" / "reports"


def main() -> None:
    rnd = pd.read_csv(REPORTS / "e7_random_distribution.csv")
    cmp_ = pd.read_csv(REPORTS / "e7_policy_comparison.csv").set_index("policy")
    rl = cmp_.loc["Trained Phase E RL"]
    b5 = cmp_.loc["B.5 locked"]
    n = len(rnd)

    rows = [
        ("Random-policy Sharpe: mean / median / p75 / p90 / max",
         f"{rnd.sharpe.mean():.3f} / {rnd.sharpe.median():.3f} / {rnd.sharpe.quantile(.75):.3f} / "
         f"{rnd.sharpe.quantile(.90):.3f} / {rnd.sharpe.max():.3f}"),
        ("Random-policy Sharpe std across seeds", f"{rnd.sharpe.std():.3f}"),
        ("Trained RL Sharpe", f"{rl.sharpe:.3f}"),
        ("RL Sharpe percentile among random seeds", f"{(rnd.sharpe < rl.sharpe).mean():.0%}"),
        ("RL Sharpe z-score vs random distribution", f"{(rl.sharpe - rnd.sharpe.mean()) / rnd.sharpe.std():.2f}"),
        ("Random seeds with Sharpe >= trained RL", f"{(rnd.sharpe >= rl.sharpe).sum()}/{n}"),
        ("Random seeds with Sharpe >= B.5", f"{(rnd.sharpe >= b5.sharpe).sum()}/{n}"),
        ("Random seeds with better MaxDD than B.5", f"{(rnd.max_dd > b5.max_dd).sum()}/{n}"),
        ("Random seeds with better MaxDD than trained RL", f"{(rnd.max_dd > rl.max_dd).sum()}/{n}"),
        ("Random seeds with higher CAGR than trained RL", f"{(rnd.cagr > rl.cagr).sum()}/{n}"),
        ("Mean random MaxDD / CAGR", f"{rnd.max_dd.mean():.1%} / {rnd.cagr.mean():.1%}"),
        ("B.5 MaxDD / CAGR", f"{b5.max_dd:.1%} / {b5.cagr:.1%}"),
        ("Trained RL MaxDD / CAGR", f"{rl.max_dd:.1%} / {rl.cagr:.1%}"),
    ]
    print("# E.7 trained RL vs random bounded policies (holdout 2019 - 2026-04-24)\n")
    print("| Metric | Value |\n|---|---|")
    for k, v in rows:
        print(f"| {k} | {v} |")


if __name__ == "__main__":
    main()
