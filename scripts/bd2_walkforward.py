"""BD2: walk-forward harness (docs/phases/rl_bandit_plan.md sections 4-5, 7).

Primary arm set (0.25 min share) and the 0.5-floor sensitivity arm set; grids 14d and 8w.
Learners: L0 (matched static at the learner's own average equity), L0b (best constant arm), L1 (TR
sizer), L2 (per-arm ridge on U1, cost-aware decode, X0), C1 (shuffled X0), C2 (random arm).
Writes runs_bd/bd2_*.csv and runs_bd/bd2_summary.json. Sealed window never touched (TERMINAL cut).
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

B_BOOT = 2000
BLOCK = 10
C1_SEEDS = 10
C2_SEEDS = 200
LEGACY_TRAIN_END = pd.Timestamp("2016-12-31")
LEGACY_VAL_END = pd.Timestamp("2018-12-31")
LEGACY_HOLD_START = pd.Timestamp("2019-01-01")
LEGACY_3Y = ("2023-04-25", "2026-04-24")
WF_LEARNERS = ["L2", "C1", "L1", "L0b", "C2"]


def prepare(name, h, x0, dt):
    g = C.build_grid(name, h)
    Yall = L.labels(g, C.ARMS_UNION)
    M, _ = L.gross_risk(g)
    X = L.context_x0(g, x0)
    Xt = L.context_tr(g, dt)
    return g, Yall, M, X, Xt


def arm_cols(arms):
    return [C.ARMS_UNION.index(a) for a in arms]


def run_armset(g, Yall, M, X, Xt, arms, seed=0):
    Y = Yall[:, arm_cols(arms)]
    valid = L.common_mask(X, Xt, Y, M)
    res, info = {}, {}
    for lrn in WF_LEARNERS:
        wf = L.run_walk_forward(g, Y, arms, lrn, valid, X=X, M=M, Xtr=Xt, seed=seed)
        res[lrn] = L.pooled_eval(g, wf["chosen"], lrn)
        info[lrn] = wf["info"]
    res["L0_L2"] = L.matched_static(g, res["L2"], "L0 matched to L2")
    res["L0_L1"] = L.matched_static(g, res["L1"], "L0 matched to L1")
    res["L0_L0b"] = L.matched_static(g, res["L0b"], "L0 matched to L0b")
    return res, info, valid, Y


def metrics_table(res: dict, names: dict) -> pd.DataFrame:
    rows = [L.summarise(res[k], label=v) for k, v in names.items()]
    return pd.DataFrame(rows)


def legacy_split(g, Yall, M, X, Xt, arms):
    """Legacy split: train 2008-2016 (periods ending <= 2016-12-31), validation 2017-2018 (alpha chosen
    on validation with the train-only model), refit on 2008-2018, holdout 2019-01-01..2026-04-24.
    Holdout paths start flat (p = 0) at the first holdout decision; no holdout information is used."""
    Y = Yall[:, arm_cols(arms)]
    valid = L.common_mask(X, Xt, Y, M)
    period_end = pd.DatetimeIndex([q[-1] for q in g.q_dates])
    dec = pd.DatetimeIndex(g.dates)
    tr1 = valid & (period_end <= LEGACY_TRAIN_END)
    va = valid & (dec > LEGACY_TRAIN_END) & (dec <= LEGACY_VAL_END)
    tr2 = valid & (period_end <= LEGACY_VAL_END)
    te = valid & (dec >= LEGACY_HOLD_START) & (dec <= C.TERMINAL)
    tr1i, vai, tr2i, tei = (np.where(m)[0] for m in (tr1, va, tr2, te))
    # alpha on validation (train-only model): mean realised U1 of the policy
    alpha_scores = {}
    for a in L.ALPHA_GRID:
        yhat = L.ridge_fit_predict(X[tr1i], Y[tr1i], X[vai], a)
        sh = L.decode(yhat, arms, 0.0)
        alpha_scores[a] = float(np.mean(C.run_shares(g, vai, sh, p0=0.0)["U1"]))
    alpha = max(alpha_scores, key=alpha_scores.get)
    rng = np.random.default_rng(0)
    out, val_out = {}, {}
    for lrn in WF_LEARNERS:
        sh_te, inf = L.fold_choice(lrn, g, tr2i, tei, arms, Y, X=X, M=M, Xtr=Xt, rng=rng, p0=0.0,
                                   alpha=alpha if lrn in ("L2", "C1") else None)
        out[lrn] = C.run_shares(g, tei, sh_te, p0=0.0)
        out[lrn]["label"] = lrn
        out[lrn]["years"] = np.asarray(g.dates[tei].year)
        sh_va, _ = L.fold_choice(lrn, g, tr1i, vai, arms, Y, X=X, M=M, Xtr=Xt, rng=rng, p0=0.0,
                                 alpha=alpha if lrn in ("L2", "C1") else None)
        val_out[lrn] = C.run_shares(g, vai, sh_va, p0=0.0)
    out["L0_L2"] = L.matched_static(g, out["L2"], "L0 matched to L2")
    out["L0_L1"] = L.matched_static(g, out["L1"], "L0 matched to L1")
    out["L0_L0b"] = L.matched_static(g, out["L0b"], "L0 matched to L0b")
    return out, val_out, alpha, alpha_scores


def main():
    t0 = time.time()
    h = C.load_history()
    x0 = C.x0_daily(h)
    dt = pd.read_parquet(C.INPUT_DIR / "daily_table.parquet")
    dt = dt.loc[dt.index <= C.TERMINAL]
    summary = {"terminal": str(C.TERMINAL.date()), "B_boot": B_BOOT, "block": BLOCK}
    fold_rows, boot_rows, metric_rows, legacy_rows, c_dist_rows = [], [], [], [], []
    names = {"L2": "L2 contextual bandit (X0, U1)", "L0_L2": "L0 matched static (at L2 avg equity)",
             "L0b": "L0b best constant arm (train)", "L1": "L1 TR sizer (FM)",
             "L0_L1": "L0 matched static (at L1 avg equity)", "C1": "C1 shuffled context",
             "C2": "C2 random arm (seed 0)"}
    for grid in ["14d", "8w"]:
        g, Yall, M, X, Xt = prepare(grid, h, x0, dt)
        for armset_name, arms in [("primary", C.ARMS_PRIMARY), ("floor05", C.ARMS_FLOOR05)]:
            res, info, valid, Y = run_armset(g, Yall, M, X, Xt, arms)
            n_pooled = len(res["L2"]["idx"])
            print(grid, armset_name, "pooled decisions", n_pooled, "t", round(time.time() - t0, 1), flush=True)
            tab = metrics_table(res, names)
            tab.insert(0, "grid", grid)
            tab.insert(1, "armset", armset_name)
            metric_rows.append(tab)
            # per-fold sign table
            pf2 = L.per_fold(res["L2"])
            pf0 = L.per_fold(res["L0_L2"])
            pf1 = L.per_fold(res["L1"])
            fd = pd.DataFrame({"year": pf2.year, "L2_Sharpe": pf2.Sharpe, "L0_Sharpe": pf0.Sharpe,
                               "L1_Sharpe": pf1.Sharpe, "L2_mdd": pf2.MaxDD, "L0_mdd": pf0.MaxDD,
                               "L2_mean_U1": pf2.mean_U1, "L0_mean_U1": pf0.mean_U1})
            fd["dSharpe_L2_L0"] = fd.L2_Sharpe - fd.L0_Sharpe
            fd["dU1_L2_L0"] = fd.L2_mean_U1 - fd.L0_mean_U1
            fd.insert(0, "grid", grid)
            fd.insert(1, "armset", armset_name)
            fold_rows.append(fd)
            # paired bootstrap
            pairs = [("L2", "L0_L2", BLOCK), ("L2", "L1", BLOCK), ("L2", "C1", BLOCK), ("L2", "C2", BLOCK),
                     ("L1", "L0_L1", BLOCK), ("L2", "L0b", BLOCK)]
            if armset_name == "primary":
                pairs += [("L2", "L0_L2", 8), ("L2", "L0_L2", 12)]
            for a, b, blk in pairs:
                bt = L.paired_bootstrap(res[a], res[b], B=B_BOOT, block=blk, seed=7)
                row = {"grid": grid, "armset": armset_name, "a": a, "b": b, "block": blk}
                for k, v in bt.items():
                    for kk, vv in v.items():
                        row[f"{k}_{kk}"] = vv
                boot_rows.append(row)
            # crash-fold MaxDD vs matched static
            crash = {"grid": grid, "armset": armset_name,
                     "L2_mdd2020": L.summarise(res["L2"])["mdd_2020"], "L0_mdd2020": L.summarise(res["L0_L2"])["mdd_2020"],
                     "L2_mdd2022": L.summarise(res["L2"])["mdd_2022"], "L0_mdd2022": L.summarise(res["L0_L2"])["mdd_2022"]}
            summary[f"crash_{grid}_{armset_name}"] = crash
            # 3-year window
            w3 = {k: L.summarise(L.dec_window(res[k], *LEGACY_3Y), label=k) for k in ["L2", "L0_L2", "L1", "L0_L1"]}
            summary[f"window3y_{grid}_{armset_name}"] = w3
            # controls: C1 and C2 seed distributions (L2 fold machinery, C2 random arms)
            if armset_name == "primary":
                c1 = []
                for sd in range(C1_SEEDS):
                    wf = L.run_walk_forward(g, Y, arms, "C1", valid, X=X, M=M, Xtr=Xt, seed=100 + sd)
                    rr = L.pooled_eval(g, wf["chosen"], "C1")
                    s = L.summarise(rr)
                    c1.append({"seed": sd, "Calmar": s["Calmar"], "Sharpe": s["Sharpe"], "mean_U1": s["mean_U1"]})
                c2 = []
                for sd in range(C2_SEEDS):
                    wf = L.run_walk_forward(g, Y, arms, "C2", valid, X=X, M=M, Xtr=Xt, seed=500 + sd)
                    rr = L.pooled_eval(g, wf["chosen"], "C2")
                    s = L.summarise(rr)
                    c2.append({"seed": sd, "Calmar": s["Calmar"], "Sharpe": s["Sharpe"], "mean_U1": s["mean_U1"]})
                for kind, rows in [("C1", c1), ("C2", c2)]:
                    d = pd.DataFrame(rows)
                    d.insert(0, "control", kind)
                    d.insert(0, "grid", grid)
                    c_dist_rows.append(d)
                print(grid, "controls done t", round(time.time() - t0, 1), flush=True)
            # decision-level output
            dec = pd.DataFrame({"date": g.dates[res["L2"]["idx"]], "L2_share": res["L2"]["shares"],
                                "L1_share": res["L1"]["shares"], "L0b_share": res["L0b"]["shares"],
                                "L2_U1": res["L2"]["U1"], "L1_U1": res["L1"]["U1"]})
            dec.to_csv(C.OUT_DIR / f"bd2_decisions_{grid}_{armset_name}.csv", index=False)
        # legacy split (primary arms)
        out, val_out, alpha, alpha_scores = legacy_split(g, Yall, M, X, Xt, C.ARMS_PRIMARY)
        summary[f"legacy_alpha_{grid}"] = {"alpha": alpha, "validation_mean_U1": {str(k): v for k, v in alpha_scores.items()}}
        names_leg = {"L2": "L2 contextual bandit", "L0_L2": "L0 matched static (L2 avg)", "L0b": "L0b best constant",
                     "L1": "L1 TR sizer", "L0_L1": "L0 matched static (L1 avg)", "C1": "C1 shuffled",
                     "C2": "C2 random arm"}
        for win_name, mask in [("holdout_2019_2026Apr", None), ("3y_2023-04-25_2026-04-24", LEGACY_3Y)]:
            for k, lab in names_leg.items():
                rr = out[k]
                rr = rr if mask is None else L.dec_window(rr, *mask)
                row = L.summarise(rr, label=lab)
                row.update({"grid": grid, "window": win_name})
                legacy_rows.append(row)
        bt = L.paired_bootstrap(out["L2"], out["L0_L2"], B=B_BOOT, block=BLOCK, seed=9)
        summary[f"legacy_boot_{grid}"] = {k: v for k, v in bt.items()}
        print(grid, "legacy done alpha", alpha, "t", round(time.time() - t0, 1), flush=True)

    metrics = pd.concat(metric_rows, ignore_index=True)
    metrics.to_csv(C.OUT_DIR / "bd2_metrics.csv", index=False)
    pd.concat(fold_rows, ignore_index=True).to_csv(C.OUT_DIR / "bd2_folds.csv", index=False)
    pd.DataFrame(boot_rows).to_csv(C.OUT_DIR / "bd2_bootstrap.csv", index=False)
    pd.DataFrame(legacy_rows).to_csv(C.OUT_DIR / "bd2_legacy.csv", index=False)
    pd.concat(c_dist_rows, ignore_index=True).to_csv(C.OUT_DIR / "bd2_control_dist.csv", index=False)
    summary["n_tests_note"] = "see REPORT.md"
    with open(C.OUT_DIR / "bd2_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("done", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main()
