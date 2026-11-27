"""BD1: controls, oracle bounds and power for the BD2 pipeline (docs/phases/rl_bandit_plan.md section 6).

C3a planted signal: U(d,a) += delta * 1{VIX rank_d > 0.5} * (0.625 - a) (log units), applied to the
labels AND to the realised paths, so the pipeline (L2, L1, matched static) sees the same edge.
C3b planted noise: X0 replaced by i.i.d. N(0,1) contexts (same valid sample); false-positive rate of the
Gate-A-style test (z > 2 vs matched static) must be <= 5%.
Oracles: (i) hindsight best arm with one-step delay (and lag 0 for contrast); (ii) predictable-risk
oracle: in-fold monotone map on the realised next-period vol of the 100% book (not returns).
MDE: 2.8 x bootstrap SE (80% power, one-sided 5%) of the pooled paired difference, per grid.

Writes runs_bd/bd1_planted.csv, bd1_noise_fp.csv, bd1_oracles.csv, bd1_mde.csv, bd1_summary.json.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from rl import bd_core as C  # noqa: E402
from rl import bd_learners as L  # noqa: E402

ARMS = C.ARMS_PRIMARY
DELTAS = [0.0, 0.0025, 0.005, 0.01, 0.02]
B_PLANT = 500
B_NOISE = 300
NOISE_SEEDS = 100
MDE_MULT = 2.8


def vix_rank_raw(h):
    return h["vix"].rolling(252, min_periods=252).rank(pct=True)


def make_edge(g, vr, delta):
    def f(i, a):
        return delta * (1.0 if vr[i] > 0.5 else 0.0) * (0.625 - a)
    return f


def planted_E(g, vr, delta):
    E = np.zeros((g.n, len(ARMS)))
    for i in range(g.n):
        for k, a in enumerate(ARMS):
            E[i, k] = make_edge(g, vr, delta)(i, a)
    return E


def pipeline(g, Y, X, M, Xt, valid, edge_fn=None, B=B_PLANT, seed=7, with_l1=True):
    """L2 (and L1) walk-forward, matched static, paths with optional planted edge, bootstrap tests."""
    wf2 = L.run_walk_forward(g, Y, ARMS, "L2", valid, X=X, M=M, Xtr=Xt)
    idx = np.where(np.isfinite(wf2["chosen"]))[0]
    res = {}
    res["L2"] = C.run_shares(g, idx, wf2["chosen"][idx], p0=0.0, edge_fn=edge_fn)
    if with_l1:
        wf1 = L.run_walk_forward(g, Y, ARMS, "L1", valid, X=X, M=M, Xtr=Xt)
        i1 = np.where(np.isfinite(wf1["chosen"]))[0]
        res["L1"] = C.run_shares(g, i1, wf1["chosen"][i1], p0=0.0, edge_fn=edge_fn)
    s_star = float(np.mean(C.flatten(res["L2"])[2]))  # matched static at the L2 average equity
    res["L0"] = C.run_shares(g, idx, np.full(len(idx), s_star), p0=0.0, edge_fn=edge_fn)
    res["L0"]["label"] = "L0"
    out = {}
    out["L2"], out["L0"] = L.summarise(res["L2"]), L.summarise(res["L0"])
    if with_l1:
        out["L1"] = L.summarise(res["L1"])
    bt = L.paired_bootstrap(res["L2"], res["L0"], B=B, block=10, seed=seed)
    out["bt_L2_L0"] = bt
    if with_l1:
        out["bt_L2_L1"] = L.paired_bootstrap(res["L2"], res["L1"], B=B, block=10, seed=seed + 1)
    return out, res


def detect(bt):
    """Gate-style flags: z > 2 on Calmar or Sharpe; and z > 2 on mean U1."""
    return {
        "det_sharpe_or_calmar": bool(bt["dSharpe"]["z"] > 2 or bt["dCalmar"]["z"] > 2),
        "det_U1": bool(bt["dU1"]["z"] > 2),
        "z_dU1": float(bt["dU1"]["z"]),
        "z_dSharpe": float(bt["dSharpe"]["z"]),
        "z_dCalmar": float(bt["dCalmar"]["z"]),
    }


def hindsight_best(g, idx, bps=C.COST_BPS):
    """Greedy hindsight: at each decision choose the arm with the best realised net U1 given the
    previous choice (true realised outcomes, real costs)."""
    p = 0.0
    shares = []
    for i in idx:
        best_a, best_u = None, -np.inf
        for a in ARMS:
            r, _ = C.period_returns(g, i, a, p, bps)
            u = float(np.log1p(C.wealth_stats(r)["R"]))
            if u > best_u:
                best_a, best_u = a, u
        shares.append(best_a)
        p = best_a
    return np.asarray(shares)


def predictable_risk_oracle(g, valid, V):
    """Monotone map on the realised next-period vol (sees vol, not returns). In-fold map; test uses the
    realised vol of its own period, as the oracle does."""
    chosen = np.full(g.n, np.nan)
    for y, train, test in L.fold_sets(g, valid):
        cuts, Lv = L.fit_map(V[train], train, g, ARMS)
        chosen[test] = Lv[np.digitize(V[test], cuts)]
    return chosen


def main():
    t0 = time.time()
    h = C.load_history()
    x0 = C.x0_daily(h)
    dt = pd.read_parquet(C.INPUT_DIR / "daily_table.parquet")
    dt = dt.loc[dt.index <= C.TERMINAL]
    vr_series = vix_rank_raw(h)
    summary = {"deltas": DELTAS, "arms": list(ARMS)}
    planted_rows, noise_rows, oracle_rows, mde_rows = [], [], [], []
    for grid in ["14d", "8w"]:
        g = C.build_grid(grid, h)
        Yall = L.labels(g, C.ARMS_UNION)
        Y = Yall[:, [C.ARMS_UNION.index(a) for a in ARMS]]
        M, V = L.gross_risk(g)
        X = L.context_x0(g, x0)
        Xt = L.context_tr(g, dt)
        valid = L.common_mask(X, Xt, Y, M)
        vr = vr_series.reindex(g.dates).values
        # --- C3a planted signal recovery through the pipeline (delta 0 = BD2 sanity check)
        for dlt in DELTAS:
            E = planted_E(g, vr, dlt)
            Yp = Y + E
            ef = make_edge(g, vr, dlt) if dlt != 0 else None
            out, res = pipeline(g, Yp, X, M, Xt, valid, edge_fn=ef, B=B_PLANT, seed=11)
            d2 = detect(out["bt_L2_L0"])
            row = {"grid": grid, "delta": dlt, "n_decisions": len(res["L2"]["idx"]),
                   "L2_CAGR": out["L2"]["CAGR"], "L0_CAGR": out["L0"]["CAGR"],
                   "L2_Sharpe": out["L2"]["Sharpe"], "L0_Sharpe": out["L0"]["Sharpe"],
                   "L2_Calmar": out["L2"]["Calmar"], "L0_Calmar": out["L0"]["Calmar"],
                   "dU1": out["bt_L2_L0"]["dU1"]["point"], "dU1_se": out["bt_L2_L0"]["dU1"]["se"],
                   "dSharpe": out["bt_L2_L0"]["dSharpe"]["point"], "dSharpe_se": out["bt_L2_L0"]["dSharpe"]["se"],
                   "dCalmar": out["bt_L2_L0"]["dCalmar"]["point"], "dCalmar_se": out["bt_L2_L0"]["dCalmar"]["se"],
                   **d2}
            planted_rows.append(row)
            print(grid, "delta", dlt, "z_dU1 %.2f z_dSharpe %.2f" % (d2["z_dU1"], d2["z_dSharpe"]),
                  "t", round(time.time() - t0, 1), flush=True)
        base = planted_rows[-len(DELTAS)]  # delta 0 row for this grid
        se_u = base["dU1_se"]
        se_s = base["dSharpe_se"]
        se_c = base["dCalmar_se"]
        mde_rows.append({"grid": grid, "n_decisions": base["n_decisions"],
                         "MDE_dU1_per_decision": MDE_MULT * se_u,
                         "MDE_dSharpe": MDE_MULT * se_s, "MDE_dCalmar": MDE_MULT * se_c,
                         "SE_dU1": se_u, "SE_dSharpe": se_s, "SE_dCalmar": se_c,
                         "decisions_per_year": base["n_decisions"] / 13.3})
        # --- C3b planted noise: contexts i.i.d. N(0,1) (same valid sample), real labels
        fps = []
        rng = np.random.default_rng(2024)
        for sd in range(NOISE_SEEDS):
            Xn = rng.normal(size=X.shape)
            out_n, _ = pipeline(g, Y, Xn, M, Xt, valid, edge_fn=None, B=B_NOISE, seed=300 + sd, with_l1=False)
            dn = detect(out_n["bt_L2_L0"])
            fps.append(dn)
            noise_rows.append({"grid": grid, "seed": sd, **dn,
                               "L2_Calmar": out_n["L2"]["Calmar"], "L0_Calmar": out_n["L0"]["Calmar"]})
        fp = pd.DataFrame(fps)
        summary[f"noise_fp_{grid}"] = {"det_sharpe_or_calmar_rate": float(fp.det_sharpe_or_calmar.mean()),
                                       "det_U1_rate": float(fp.det_U1.mean()), "n": len(fp)}
        print(grid, "noise FP", summary[f"noise_fp_{grid}"], "t", round(time.time() - t0, 1), flush=True)
        # --- oracles on the same pooled decisions
        # static L0 at the L2 average equity from the unperturbed pipeline
        out0, res0 = pipeline(g, Y, X, M, Xt, valid, edge_fn=None, B=B_PLANT, seed=11)
        hb = hindsight_best(g, res0["L2"]["idx"])
        hb_res = C.run_shares(g, res0["L2"]["idx"], hb, p0=0.0)
        g0 = C.build_grid(grid, h, fill_lag=0)
        hb0 = hindsight_best(g0, res0["L2"]["idx"])
        hb0_res = C.run_shares(g0, res0["L2"]["idx"], hb0, p0=0.0)
        po = predictable_risk_oracle(g, valid, V)
        po_idx = np.where(np.isfinite(po))[0]
        po_res = C.run_shares(g, po_idx, po[po_idx], p0=0.0)
        for name, rr in [("hindsight_best_lag1", hb_res), ("hindsight_best_lag0", hb0_res),
                         ("predictable_risk_oracle_lag1", po_res)]:
            rr["label"] = name
            s = L.summarise(rr)
            bt = L.paired_bootstrap(rr, res0["L0"], B=B_PLANT, block=10, seed=5)
            oracle_rows.append({"grid": grid, "oracle": name, "n_decisions": len(rr["idx"]),
                                "CAGR": s["CAGR"], "MaxDD": s["MaxDD"], "Sharpe": s["Sharpe"],
                                "Calmar": s["Calmar"], "avg_equity": s["avg_equity"], "mean_U1": s["mean_U1"],
                                "dSharpe_vs_L0": bt["dSharpe"]["point"], "z_dSharpe_vs_L0": bt["dSharpe"]["z"],
                                "dCalmar_vs_L0": bt["dCalmar"]["point"], "z_dCalmar_vs_L0": bt["dCalmar"]["z"],
                                "dU1_vs_L0": bt["dU1"]["point"], "z_dU1_vs_L0": bt["dU1"]["z"]})
        s0 = L.summarise(res0["L0"])
        s2 = L.summarise(res0["L2"])
        oracle_rows.append({"grid": grid, "oracle": "reference_L0_static", "n_decisions": len(res0["L0"]["idx"]),
                            "CAGR": s0["CAGR"], "MaxDD": s0["MaxDD"], "Sharpe": s0["Sharpe"], "Calmar": s0["Calmar"],
                            "avg_equity": s0["avg_equity"], "mean_U1": s0["mean_U1"]})
        oracle_rows.append({"grid": grid, "oracle": "reference_L2", "n_decisions": len(res0["L2"]["idx"]),
                            "CAGR": s2["CAGR"], "MaxDD": s2["MaxDD"], "Sharpe": s2["Sharpe"], "Calmar": s2["Calmar"],
                            "avg_equity": s2["avg_equity"], "mean_U1": s2["mean_U1"]})
        print(grid, "oracles done t", round(time.time() - t0, 1), flush=True)
    pd.DataFrame(planted_rows).to_csv(C.OUT_DIR / "bd1_planted.csv", index=False)
    pd.DataFrame(noise_rows).to_csv(C.OUT_DIR / "bd1_noise_fp.csv", index=False)
    pd.DataFrame(oracle_rows).to_csv(C.OUT_DIR / "bd1_oracles.csv", index=False)
    pd.DataFrame(mde_rows).to_csv(C.OUT_DIR / "bd1_mde.csv", index=False)
    with open(C.OUT_DIR / "bd1_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("done", round(time.time() - t0, 1), flush=True)


if __name__ == "__main__":
    main()
