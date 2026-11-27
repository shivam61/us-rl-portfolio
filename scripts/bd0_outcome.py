"""BD0: outcome table R(d,a,p) for the 8w and 14d grids (docs/phases/rl_bandit_plan.md section 2).

Writes runs_bd/outcome_8w.parquet and runs_bd/outcome_14d.parquet, plus runs_bd/bd0_summary.csv.
Fill at close t+1 (FILL_LAG = 1), 10 bps per unit turnover, terminal period included.
Also asserts that finalize_equity_only gives stock weights summing to the arm (no hidden floor).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rl import bd_core as C  # noqa: E402
from src.rl.exposure_mix import finalize_equity_only  # noqa: E402


def main():
    h = C.load_history()
    summary = []
    for name in ["8w", "14d"]:
        g = C.build_grid(name, h)
        assert g.n >= 2
        # weights invariant: stock sum == arm for every arm, every decision
        for a in C.ARMS_UNION:
            for i in range(g.n):
                w = pd.Series(g.book[i], index=g.cols)
                fw = finalize_equity_only(w * a, a)
                assert abs(float(fw.abs().sum()) - a) < 1e-9, (name, a, i)
        tbl = C.outcome_table(g)
        out = C.OUT_DIR / f"outcome_{name}.parquet"
        tbl.to_parquet(out, index=False)
        first, last = g.dates[0].date(), g.dates[-1].date()
        last_period = (g.q_dates[-1][0].date(), g.q_dates[-1][-1].date())
        sub = tbl[(tbl.prev_share == tbl.arm)]
        for a in C.ARMS_PRIMARY:
            x = sub[sub.arm == a]
            summary.append({
                "grid": name, "arm": a, "n_decisions": g.n, "first_decision": str(first),
                "last_decision": str(last), "last_period": f"{last_period[0]}..{last_period[1]}",
                "mean_U1": x.U1.mean(), "mean_R": x.R_net.mean(), "mean_MaxDD": x.MaxDD.mean(),
                "mean_vol": x.vol.mean(), "mean_turnover_at_p_eq_a": x.turnover.mean(),
                "n_rows_table": len(tbl), "path": str(out),
            })
        print(name, "decisions", g.n, first, last, "last period", last_period, "rows", len(tbl), flush=True)
    pd.DataFrame(summary).to_csv(C.OUT_DIR / "bd0_summary.csv", index=False)
    print("saved", C.OUT_DIR)


if __name__ == "__main__":
    main()
