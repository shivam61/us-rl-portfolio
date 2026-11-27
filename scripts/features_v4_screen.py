"""Screen of the v4.1 feature set on the 14d grid and planted-signal power analysis (FH task 12). No RL.

Outputs (runs_fh/screen_v4_1/):
  univariate_primary.csv   : pre-registered family: target T1_mdd x 48 features. IC, block-permutation p (B=20000,
                             one permutation set shared by the family), analytic p, q_BH over the family, sign
                             consistency over regime blocks.
  univariate_secondary.csv : T2_vol and T5_signed, exploratory (not in the BH family).
  incremental_A2.csv       : delta IC over TR on IDENTICAL row masks for base and full model, block-permutation
                             null (B=2000, exploratory).
  power_curve.csv          : planted-signal power at BH q<0.10. v4 design (B=1000, m=159) vs v4.1 design
                             (B=20000, m=60), plus the analytic-p curve on a fine grid.
  screen_summary.json      : row counts, n_eff, minimum detectable delta IC at 80% power.

usage: python scripts/features_v4_screen.py [--reps 100] [--analytic_reps 2000] [--quick]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rl import features_risk_v4 as L  # noqa: E402
from src.rl import features_v4_screen as S  # noqa: E402
from src.rl.features_v4_manifest import BLOCKS  # noqa: E402

OUT = ROOT / "runs_fh" / "screen_v4_1"
TR = ["rv_u_21", "rv_u_63", "rv_s_21", "rv_s_63", "vix_level", "stress_b5"]
DELTAS = [0.02, 0.05, 0.10, 0.15]
FINE = np.round(np.arange(0.02, 0.301, 0.01), 3)
SEED = 20261127
PHI = 0.97  # set in main() to the median lag-1 rank autocorrelation of the features


def load_grid():
    G = pd.read_parquet(ROOT / "runs_fh" / "features_v4_1" / "grid_14d_v4.parquet").copy()
    G["prev_T1"] = G["T1_mdd"].shift(1)  # known at this decision: previous period's realised drawdown
    return G


def complete(G, cols):
    return G[G[cols].notna().all(axis=1)]


def sign_consistency(x, y, blk):
    obs = np.sign(S.spearman(x, y))
    same, nb = 0, 0
    for name, _a, _b in BLOCKS:
        m = blk == name
        if m.sum() >= 20:
            nb += 1
            same += int(np.sign(S.spearman(x[m], y[m])) == obs)
    return same, nb


def univariate(G, feats, target, sign, B, label):
    C = complete(G, feats + [target])
    y = sign * C[target].to_numpy(float)
    blk = C["block"].to_numpy()
    X = C[feats].to_numpy(float)
    Xr, yr = S.rank_cols(X), S.rank_cols(y)
    obs = S.obs_ic_vector(Xr, yr)
    null = S.null_matrix(Xr, yr, B=B, rng=np.random.default_rng(SEED))  # (B, m), one shared permutation set
    p_block = (np.sum(np.abs(null) >= np.abs(obs)[None, :], axis=0) + 1) / (B + 1)
    rows = []
    for j, f in enumerate(feats):
        neff = S.n_eff(X[:, j], y)
        same, nb = sign_consistency(X[:, j], y, blk)
        rows.append(dict(target=target, feature=f, n=len(C), IC=float(obs[j]), p_block=float(p_block[j]),
                         p_fisher=S.p_fisher(float(obs[j]), neff), n_eff=round(neff, 1),
                         sign_same_blocks=same, n_blocks=nb, label=label))
    df = pd.DataFrame(rows)
    df["q_BH"] = S.bh_q(df["p_block"].values)
    df["reject_BH_0.10"] = df["q_BH"] < 0.10
    return df


def incremental(G, feats, B):
    """delta IC of adding f to TR (LORO ridge, embargo 2). Base and full models use the SAME row mask."""
    cols = TR + ["prev_T1", "T1_mdd", "block"] + feats
    C = G[G[TR + ["prev_T1", "T1_mdd"] + feats].notna().all(axis=1)]
    y = -C["T1_mdd"].to_numpy(float)
    blk = C["block"].to_numpy()
    blocks = list(dict.fromkeys(blk))
    base_F = C[TR + ["prev_T1"]].to_numpy(float)
    rng = np.random.default_rng(SEED + 1)

    def model_ic(F, yy):
        p = S.loro_pred(F, yy, blk, blocks, embargo=2)
        m = np.isfinite(p)
        return S.spearman(p[m], yy[m]) if m.sum() >= 20 else np.nan

    base_ic = model_ic(base_F, y)
    rows = []
    for f in feats:
        if f in TR:
            continue
        F = np.column_stack([base_F, C[f].to_numpy(float)])
        d_obs = model_ic(F, y) - base_ic
        null = []
        for _ in range(B):
            perm = S.block_perm_indices(len(y), 1, S.BLOCK_LEN, rng)[0]
            yp = y[perm]
            null.append(model_ic(F, yp) - model_ic(base_F, yp))
        null = np.array([v for v in null if np.isfinite(v)])
        p = (np.sum(null >= d_obs) + 1) / (len(null) + 1)
        rows.append(dict(feature=f, n=len(C), base_IC=base_ic, delta_IC=d_obs, p_block_null=p, B=B))
    df = pd.DataFrame(rows)
    df["q_BH_inc"] = S.bh_q(df["p_block_null"].values)
    return df


def power_block(y, m, delta, reps, B, rng):
    """Block-permutation design: share of reps in which the planted feature is rejected at BH q<0.10 in a
    family of m tests (planted + m-1 iid noise features). One permutation set per rep, shared by the family."""
    n = len(y)
    yr = S.rank_cols(y)
    hits = 0
    for _ in range(reps):
        x = S.plant_feature_ar(y, delta, PHI, rng)
        X = np.column_stack([x, S.ar1_matrix(n, m - 1, PHI, rng)])
        Xr = S.rank_cols(X)
        obs = S.obs_ic_vector(Xr, yr)
        null = S.null_matrix(Xr, yr, B=B, rng=rng)
        p = (np.sum(np.abs(null) >= np.abs(obs)[None, :], axis=0) + 1) / (B + 1)
        hits += int(S.bh_reject(p, alpha=0.10)[0])
    return hits / reps


def power_analytic(y, m, delta, reps, rng):
    """Analytic design: Fisher-z p-values with n_eff of the planted pair (same n_eff for the noise columns)."""
    n = len(y)
    hits = 0
    for _ in range(reps):
        x = S.plant_feature_ar(y, delta, PHI, rng)
        X = np.column_stack([x, S.ar1_matrix(n, m - 1, PHI, rng)])
        Xr, yr = S.rank_cols(X), S.rank_cols(y)
        obs = S.obs_ic_vector(Xr, yr)
        neff = S.n_eff(x, y)
        p = np.array([S.p_fisher(float(v), neff) for v in obs])
        hits += int(S.bh_reject(p, alpha=0.10)[0])
    return hits / reps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100, help="reps for the block-permutation power curve")
    ap.add_argument("--analytic_reps", type=int, default=2000)
    ap.add_argument("--quick", action="store_true", help="small B and reps for a smoke test (not for the report)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    G = load_grid()
    feats = list(L.FEATURE_NAMES)
    B = 2000 if args.quick else S.B_SCREEN
    C = complete(G, feats + ["T1_mdd"])
    summary = {"family": "T1_mdd x features (pre-registered primary)", "n_features": len(feats),
               "n_rows_primary": int(len(C)), "first_row": str(C.index[0].date()),
               "last_row": str(C.index[-1].date()), "B_screen": B}

    prim = univariate(G, feats, "T1_mdd", -1.0, B, "primary")
    prim.to_csv(OUT / "univariate_primary.csv", index=False)
    sec = pd.concat([univariate(G, feats, "T2_vol", 1.0, 2000, "secondary"),
                     univariate(G, feats, "T5_signed", 1.0, 2000, "secondary")])
    sec.to_csv(OUT / "univariate_secondary.csv", index=False)

    inc = incremental(G, feats, B=100 if args.quick else 2000)
    inc.to_csv(OUT / "incremental_A2.csv", index=False)

    y = -C["T1_mdd"].to_numpy(float)  # IC>0 means larger drawdown; power uses the planted IC directly
    global PHI
    PHI = float(np.median([S.lag1_autocorr(S.rank_cols(C[f].to_numpy(float))) for f in feats]))
    summary["median_lag1_rank_autocorr_features"] = PHI
    summary["n_eff_T1_median_over_features"] = float(np.median(
        [S.n_eff(C[f].to_numpy(float), y) for f in feats]))
    rows = []
    rng = np.random.default_rng(SEED + 2)
    for delta in DELTAS:
        rows.append(dict(delta_IC=delta, design="v4.1 analytic p, m=60", power=power_analytic(
            y, 60, delta, args.analytic_reps, rng), reps=args.analytic_reps))
    for delta in DELTAS:
        rows.append(dict(delta_IC=delta, design="v4.1 block-perm B=%d, m=60" % B, power=power_block(
            y, 60, delta, args.reps, B, rng), reps=args.reps))
    for delta in DELTAS:
        rows.append(dict(delta_IC=delta, design="v4 design: block-perm B=1000, m=159", power=power_block(
            y, 159, delta, args.reps, 1000, rng), reps=args.reps))
    curve = pd.DataFrame(rows)
    curve.to_csv(OUT / "power_curve.csv", index=False)

    fine = pd.DataFrame([dict(delta_IC=d, power=power_analytic(y, 60, d, 500 if args.quick else 1500, rng))
                         for d in FINE])
    fine.to_csv(OUT / "power_curve_fine_analytic.csv", index=False)
    ok = fine[fine["power"] >= 0.80]
    summary["min_detectable_delta_IC_power80_analytic_m60"] = float(ok["delta_IC"].min()) if len(ok) else None
    summary["primary_rejections_BH_0.10"] = int(prim["reject_BH_0.10"].sum())
    summary["primary_min_q_BH"] = float(prim["q_BH"].min())
    summary["primary_min_p_block"] = float(prim["p_block"].min())
    with open(OUT / "screen_summary.json", "w") as f:
        json.dump(summary, f, indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))
    print(curve.to_string())
    print(fine.to_string())


if __name__ == "__main__":
    main()
