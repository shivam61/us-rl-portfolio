"""Materialise the v4.1 feature set, decision grids, metadata and manifest (experiment FH).

Deterministic: single-threaded BLAS, PYTHONHASHSEED=0 (re-exec when run as a script), KMeans pinned in the library.
Inputs : runs_fh/features_v4_1/history_v41.pkl (built by scripts/features_v4_history_build.py)
Outputs (runs_fh/features_v4_1/): daily_v4.parquet, grid_14d_v4.parquet, grid_8w_v4.parquet,
          feature_meta.csv, distribution_by_block.csv, mask_holdings_census.csv, manifest.json,
          canonical_checksums.json

usage: python scripts/features_v4_materialize.py [--out DIR] [--hist PATH]
"""
import os
import sys

if __name__ == "__main__" and os.environ.get("PYTHONHASHSEED") != "0":  # hash seed must be set at interpreter start
    _env = dict(os.environ, PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    os.execve(sys.executable, [sys.executable] + sys.argv, _env)

import argparse  # noqa: E402
import json  # noqa: E402
import pickle  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rl import features_risk_v4 as L  # noqa: E402
from src.rl import features_v4_targets as T  # noqa: E402
from src.rl import features_v4_meta as MD  # noqa: E402
from src.rl.features_v4_manifest import BLOCKS, block_of, canonical_checksum, sha256_file  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "runs_fh" / "features_v4_1"))
    ap.add_argument("--hist", default=str(ROOT / "runs_fh" / "features_v4_1" / "history_v41.pkl"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with open(args.hist, "rb") as f:
        H = pickle.load(f)
    meta_h = H.pop("_meta")
    absent = H.pop("universe_mask_absent")
    hist_side = json.load(open(Path(args.hist).with_suffix(".json")))
    M = H["universe_mask"]

    P_full = L.build_panel(H)
    P = P_full.loc[T.START:T.END, L.FEATURE_NAMES].copy()
    P.attrs = {}  # DataFrame attrs (raw inputs, regime flags) are not parquet-serialisable
    daily_path = out / "daily_v4.parquet"
    P.to_parquet(daily_path)

    u = H["unit_ret"]
    grids = {}
    for name in ("14d", "8w"):
        dates = T.grid_dates(name, meta_h["control_dates"], H["spy"].index)
        tg = T.targets_for_grid(u, dates)
        G = P.reindex(tg.index).join(tg)
        G["block"] = block_of(G.index)
        G.index.name = "date"
        G.attrs = {}
        path = out / f"grid_{name}_v4.parquet"
        G.to_parquet(path)
        grids[name] = (path, G)

    # M7 distribution summary by regime block (regression snapshot for tests/test_features_v4_integrity.py)
    dist_rows = []
    for name, a, b in BLOCKS:
        sub = P.loc[a:b]
        for c in P.columns:
            s = sub[c].dropna()
            dist_rows.append(dict(block=name, feature=c, n=int(len(s)),
                                  min=float(s.min()) if len(s) else np.nan,
                                  q05=float(s.quantile(0.05)) if len(s) else np.nan,
                                  median=float(s.median()) if len(s) else np.nan,
                                  q95=float(s.quantile(0.95)) if len(s) else np.nan,
                                  max=float(s.max()) if len(s) else np.nan))
    dist_path = out / "distribution_by_block.csv"
    pd.DataFrame(dist_rows).to_csv(dist_path, index=False)

    # membership census: unit-book holdings outside the PIT mask at each decision date (M-item 7)
    W = H["unit_w"]
    census = []
    for name, (_, G) in grids.items():
        for d in G.index:
            held = W.loc[d][W.loc[d] > 0]
            out_m = [c for c in held.index if c in M.columns and not bool(M.loc[d, c])]
            census.append(dict(grid=name, date=d.date().isoformat(), n_held=int(len(held)),
                               n_outside_mask=int(len(out_m)),
                               weight_outside_mask=float(held[out_m].sum()) if out_m else 0.0,
                               mask_eligible_share=float(M.loc[d].mean())))
    census_path = out / "mask_holdings_census.csv"
    pd.DataFrame(census).to_csv(census_path, index=False)

    # feature metadata (definition, inputs, lag, warm-up, first valid date, group, rationale, reference)
    meta = MD.feature_meta_table(P_full.loc[T.START:T.END], absent)
    meta_path = out / "feature_meta.csv"
    meta.to_csv(meta_path, index=False)

    # M6 integrity: per-feature NaN/inf counts, constancy per block, duplicate pairs
    integ = {"nan_count": {c: int(P[c].isna().sum()) for c in P.columns},
             "inf_count": {c: int(np.isinf(P[c].astype(float)).sum()) for c in P.columns}}
    const_blocks = {}
    for name, a, b in BLOCKS:
        sub = P.loc[a:b]
        for c in P.columns:
            s = sub[c].dropna()
            if len(s) > 20 and float(s.std()) < 1e-12:
                const_blocks.setdefault(c, []).append(name)
    integ["constant_in_block"] = const_blocks
    corr = P.corr().abs()
    integ["duplicate_pairs_gt_0999"] = [(a, b, float(corr.loc[a, b])) for i, a in enumerate(P.columns)
                                        for b in P.columns[i + 1:] if corr.loc[a, b] > 0.999]
    integ["clipped_share_at_pm3"] = {c: float(((P[c].abs() - 3.0).abs() < 1e-12).sum() / max(1, P[c].notna().sum()))
                                     for c in P.columns}

    checks = {"canonical_checksum_daily": canonical_checksum(P)}
    for name, (path, G) in grids.items():
        checks[f"canonical_checksum_grid_{name}"] = canonical_checksum(G)

    manifest = {
        "version": "v4.1", "experiment": "FH",
        "window": [str(T.START.date()), str(T.END.date())],
        "library_sha256": sha256_file(ROOT / "src/rl/features_risk_v4.py"),
        "history_adapter_sha256": sha256_file(ROOT / "src/rl/features_v4_history.py"),
        "targets_sha256": sha256_file(ROOT / "src/rl/features_v4_targets.py"),
        "history_sha256": hist_side["history_sha256"], "history_inputs_sha256": hist_side["inputs_sha256"],
        "versions": {"python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__,
                     "sklearn": __import__("sklearn").__version__},
        "feature_names": L.FEATURE_NAMES, "n_features": len(L.FEATURE_NAMES),
        "removed_v41": L.REMOVED_V41,
        "universe_mask_absent": absent,
        "integrity": integ,
        "canonical_checksums": checks,
        "outputs": {},
    }
    for p in [daily_path, grids["14d"][0], grids["8w"][0], meta_path, dist_path, census_path]:
        rows_n = int(len(pd.read_parquet(p))) if p.suffix == ".parquet" else int(len(pd.read_csv(p)))
        manifest["outputs"][p.name] = {"sha256": sha256_file(p), "rows": rows_n}
    json.dump(manifest, open(out / "manifest.json", "w"), indent=1, default=str)
    json.dump(checks, open(out / "canonical_checksums.json", "w"), indent=1)
    print(json.dumps({k: manifest[k] for k in ("n_features", "canonical_checksums")}, indent=1))


if __name__ == "__main__":
    main()
