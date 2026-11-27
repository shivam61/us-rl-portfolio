"""Build the causal v4 history dict from data/ and the committed B.5 pipeline (experiment FH, v4.1).

Reads data/ only (read-only). Writes runs_fh/features_v4_1/history_v41.pkl and a sidecar json with
the input-file hashes. Root is derived from this file's location: no hard-coded worktree paths.

usage: python scripts/features_v4_history_build.py [--out PATH]
"""
import argparse
import hashlib
import json
import os
import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
os.chdir(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.rl.features_v4_history import history_from_inputs  # noqa: E402
from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs  # noqa: E402
from run_phase_b1_simulator_reproduction import recommended_end_for_universe  # noqa: E402
from run_phase_b3_exposure_control import rolling_beta_matrix  # noqa: E402
from run_phase_b4_risk_engine import build_stress_series  # noqa: E402
from run_phase_b5_final_gate import build_promoted_weights  # noqa: E402

INPUT_FILES = ["data/raw/SPY.parquet", "data/raw/^VIX.parquet", "data/artifacts/universe_mask_sp500.parquet",
               "config/base.yaml", "config/universes/sp500.yaml"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "runs_fh" / "features_v4_1" / "history_v41.pkl"))
    args = ap.parse_args()
    np.random.seed(0)

    inputs = load_inputs("config/base.yaml", "config/universes/sp500.yaml", TREND_ASSETS)
    prices = inputs["prices"]
    end = recommended_end_for_universe(inputs["universe_config"].name, prices.index.max())
    beta = rolling_beta_matrix(prices, inputs["universe_config"].benchmark)
    stress = build_stress_series(inputs)
    b5, _diag, ctrl = build_promoted_weights(inputs, end, beta, stress)

    spy_raw = pd.read_parquet(ROOT / "data/raw/SPY.parquet")
    vix = pd.read_parquet(ROOT / "data/raw/^VIX.parquet")["close"]
    mask = pd.read_parquet(ROOT / "data/artifacts/universe_mask_sp500.parquet")
    H = history_from_inputs(prices, b5, stress, vix, spy_raw["high"], spy_raw["low"], mask)
    H["_meta"] = {"end": str(end.date()), "n_control_dates": len(ctrl), "origin": str(prices.index.min().date()),
                  "control_dates": [str(pd.Timestamp(d).date()) for d in ctrl]}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        pickle.dump(H, f)
    side = {"history_sha256": sha256(out),
            "inputs_sha256": {p: sha256(ROOT / p) for p in INPUT_FILES},
            "b5_columns": int(b5.shape[1]), "unit_w_columns": int(H["unit_w"].shape[1]),
            "python": sys.version.split()[0], "pandas": pd.__version__, "numpy": np.__version__}
    with open(out.with_suffix(".json"), "w") as f:
        json.dump(side, f, indent=1)
    print(json.dumps(side, indent=1))


if __name__ == "__main__":
    main()
