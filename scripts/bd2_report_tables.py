"""Multiplicity (BH-FDR) and Gate A checks from the BD2 / BD1 outputs in runs_bd/.

Primary family: H1 (L2 vs matched static, Sharpe and Calmar, both grids; primary arm set, block 10).
Secondary family: every other paired comparison in bd2_bootstrap.csv (all metrics), BH-FDR at 10%.
Writes runs_bd/bd2_multiplicity.csv and runs_bd/gate_a.json.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs_bd"


def two_sided_p(z):
    return math.erfc(abs(z) / math.sqrt(2.0))


def bh(pvals):
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    q = np.empty(n)
    prev = 1.0
    for i in range(n - 1, -1, -1):
        val = ranked[i] * n / (i + 1)
        prev = min(prev, val)
        q[order[i]] = prev
    return q


def main():
    b = pd.read_csv(OUT / "bd2_bootstrap.csv")
    rows = []
    for _, r in b.iterrows():
        primary_pair = (r["a"] == "L2" and r["b"] == "L0_L2" and r["block"] == 10 and r["armset"] == "primary")
        for metric in ["dU1", "dSharpe", "dCalmar"]:
            rows.append({"grid": r["grid"], "armset": r["armset"], "a": r["a"], "b": r["b"],
                         "block": r["block"], "metric": metric, "point": r[f"{metric}_point"],
                         "z": r[f"{metric}_z"], "p_two_sided": two_sided_p(r[f"{metric}_z"]),
                         "family": "primary_H1" if (primary_pair and metric in ("dSharpe", "dCalmar")) else
                         ("sensitivity_block" if r["block"] != 10 else "secondary")})
    df = pd.DataFrame(rows)
    df["q_BH_all"] = bh(df.p_two_sided.values)
    sec = df.family == "secondary"
    df.loc[sec, "q_BH_secondary"] = bh(df.loc[sec, "p_two_sided"].values)
    df.to_csv(OUT / "bd2_multiplicity.csv", index=False)
    n_primary = int((df.family == "primary_H1").sum())
    n_sec = int(sec.sum())
    h1 = df[df.family == "primary_H1"]
    # Gate A components
    m = pd.read_csv(OUT / "bd2_metrics.csv")
    leg = pd.read_csv(OUT / "bd2_legacy.csv")
    fold = pd.read_csv(OUT / "bd2_folds.csv")
    summ = json.load(open(OUT / "bd2_summary.json"))
    c1 = pd.read_csv(OUT / "bd2_control_dist.csv")
    gate = {"tests_primary": n_primary, "tests_secondary": n_sec}
    gate["H1_met_both_grids"] = {}
    for grid in ["14d", "8w"]:
        d = h1[(h1.grid == grid)]
        gate["H1_met_both_grids"][grid] = {
            "dSharpe_z": float(d[d.metric == "dSharpe"].z.iloc[0]),
            "dCalmar_z": float(d[d.metric == "dCalmar"].z.iloc[0]),
            "met": bool(((d.z > 2) & (d.point > 0)).any()),
        }
    gate["H1_met"] = all(v["met"] for v in gate["H1_met_both_grids"].values())
    # not worse than matched static on the 3y windows
    w3 = {}
    for grid in ["14d", "8w"]:
        x = leg[(leg.grid == grid) & (leg.window.str.startswith("3y"))]
        l2 = x[x.label.str.startswith("L2")].iloc[0]
        l0 = x[x.label.str.startswith("L0 matched static (L2")].iloc[0]
        pool = summ[f"window3y_{grid}_primary"]
        w3[grid] = {"legacy_L2_Sharpe": float(l2.Sharpe), "legacy_L0_Sharpe": float(l0.Sharpe),
                    "legacy_L2_Calmar": float(l2.Calmar), "legacy_L0_Calmar": float(l0.Calmar),
                    "pooled_L2_Sharpe": pool["L2"]["Sharpe"], "pooled_L0_Sharpe": pool["L0_L2"]["Sharpe"],
                    "pooled_L2_Calmar": pool["L2"]["Calmar"], "pooled_L0_Calmar": pool["L0_L2"]["Calmar"]}
    gate["not_worse_3y"] = {g: bool(v["pooled_L2_Calmar"] >= v["pooled_L0_Calmar"] and
                                    v["pooled_L2_Sharpe"] >= v["pooled_L0_Sharpe"]) for g, v in w3.items()}
    gate["not_worse_3y_detail"] = w3
    # crash bar: 2020 and 2022 MaxDD at least 10 points shallower than matched static
    crash = {}
    for grid in ["14d", "8w"]:
        cr = summ[f"crash_{grid}_primary"]
        crash[grid] = {"2020_gain_pts": 100 * (cr["L2_mdd2020"] - cr["L0_mdd2020"]),
                       "2022_gain_pts": 100 * (cr["L2_mdd2022"] - cr["L0_mdd2022"])}
    gate["crash_bar_10pts"] = {g: bool(v["2020_gain_pts"] >= 10 and v["2022_gain_pts"] >= 10)
                               for g, v in crash.items()}
    gate["crash_detail_pts"] = crash
    # shuffled-context control degrades (L2 - C1 > 0 on both metrics, both grids: point and z>2 on U1)
    cd = {}
    for grid in ["14d", "8w"]:
        d = b[(b.grid == grid) & (b.armset == "primary") & (b.a == "L2") & (b.b == "C1") & (b.block == 10)].iloc[0]
        cd[grid] = {"dU1": float(d.dU1_point), "dU1_z": float(d.dU1_z), "dSharpe_point": float(d.dSharpe_point),
                    "dSharpe_z": float(d.dSharpe_z)}
    gate["shuffle_degrades"] = bool(all(v["dU1_z"] > 2 for v in cd.values()))
    gate["shuffle_detail"] = cd
    # equity std > 0.05 (decision-level std of L2 shares)
    eq = m[(m.armset == "primary") & (m.label.str.startswith("L2"))]
    gate["equity_std_ok"] = {g: float(eq[eq.grid == g].equity_std_decision.iloc[0]) for g in ["14d", "8w"]}
    gate["equity_std_pass"] = bool(all(v > 0.05 for v in gate["equity_std_ok"].values()))
    # fold sign: >= 9 of 14 non-negative on the primary metric (Sharpe difference L2 - L0)
    fs = {}
    for grid in ["14d", "8w"]:
        f = fold[(fold.grid == grid) & (fold.armset == "primary")]
        fs[grid] = {"folds": int(len(f)), "dSharpe_nonneg": int((f.dSharpe_L2_L0 >= 0).sum()),
                    "dU1_nonneg": int((f.dU1_L2_L0 >= 0).sum())}
    gate["fold_sign"] = fs
    gate["fold_sign_pass"] = bool(all(v["dSharpe_nonneg"] >= 9 for v in fs.values()))
    gate["survives_20bps_2d_delay"] = "NOT RUN (BD4)"
    gate["verdict"] = "NOT MET" if not (gate["H1_met"] and gate["shuffle_degrades"] and gate["crash_bar_10pts"]
                                        and gate["fold_sign_pass"]) else "PENDING BD4 (robustness)"
    with open(OUT / "gate_a.json", "w") as f:
        json.dump(gate, f, indent=2, default=str)
    print(json.dumps(gate, indent=2, default=str))
    print(h1[["grid", "metric", "point", "z", "p_two_sided", "q_BH_all"]].round(4).to_string())
    print("secondary BH q<0.10 count:", int((df.q_BH_secondary < 0.10).sum()), "of", n_sec)


if __name__ == "__main__":
    main()
