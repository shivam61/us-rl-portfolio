"""A0 helper: build the B.5 book, inputs and control dates once and pickle them under runs_a0/cache.

Mirrors the setup in scripts/train_rl_v2.py main() (load_inputs -> recommended_end -> beta/stress ->
build_promoted_weights). Read-only with respect to data/.

Usage (from worktree root): .venv/bin/python scripts/a0_build_cache.py
"""
import pickle
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for p in (REPO_ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs  # noqa: E402
from run_phase_b1_simulator_reproduction import recommended_end_for_universe  # noqa: E402
from run_phase_b3_exposure_control import rolling_beta_matrix  # noqa: E402
from run_phase_b4_risk_engine import build_stress_series  # noqa: E402
from run_phase_b5_final_gate import build_promoted_weights  # noqa: E402

OUT = REPO_ROOT / "runs_a0" / "cache"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    inputs = load_inputs("config/base.yaml", "config/universes/sp500.yaml", TREND_ASSETS)
    ve = recommended_end_for_universe(inputs["universe_config"].name, inputs["prices"].index.max())
    beta = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress = build_stress_series(inputs)
    b5, diag, ctrl = build_promoted_weights(inputs, ve, beta, stress)
    print(f"b5 shape={b5.shape} ctrl={len(ctrl)} first={ctrl[0]} last={ctrl[-1]} secs={time.time()-t0:.1f}")
    with open(OUT / "a0_cache.pkl", "wb") as fh:
        pickle.dump({"inputs": inputs, "b5": b5, "ctrl": list(ctrl), "stress": stress, "beta": beta,
                     "validation_end": ve}, fh)
    print("wrote", OUT / "a0_cache.pkl")


if __name__ == "__main__":
    main()
