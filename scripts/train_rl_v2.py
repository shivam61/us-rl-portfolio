"""Phase E.5 / F.2 — PPO training for RL Regime Controller v2 on 2008–2016 with early stopping.

Usage:
    # Full training (sp500, 2008–2016):
    .venv/bin/python scripts/train_rl_v2.py

    # Smoke test (verify env + PPO plumbing, finishes in ~2 min):
    .venv/bin/python scripts/train_rl_v2.py --total-timesteps 2000 --eval-freq 500 --universe config/universes/sp100.yaml

Outputs:
    artifacts/models/rl_e_ppo_best.zip      — best checkpoint by validation Sharpe
    artifacts/models/rl_e_ppo_final.zip     — final checkpoint (regardless of best)
    artifacts/reports/phase_e5_training_log.csv

Lambda note (F.2 investigation):
    reward_v2.py function signature has lambda_dd=0.08, lambda_cash=0.05 (E.7 intent).
    BUT PortfolioEnvV2.__init__ has lambda_dd=0.15, lambda_cash=0.03 as defaults, and passes
    self.lambda_dd/self.lambda_cash to compute_reward_v2 — overriding the function defaults.
    Because train_rl_v2.py did not explicitly pass lambda_dd/lambda_cash to PortfolioEnvV2,
    E.7 was effectively trained with lambda_dd=0.15, lambda_cash=0.03 (env defaults).
    F.2 reproduces that behaviour exactly; the E.7-intended values are pinned below as
    LAMBDA_DD_E7_EFFECTIVE / LAMBDA_CASH_E7_EFFECTIVE for clarity and to avoid silent drift.
"""
import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs
from run_phase_b1_simulator_reproduction import recommended_end_for_universe
from run_phase_b3_exposure_control import rolling_beta_matrix
from run_phase_b4_risk_engine import build_stress_series
from run_phase_b5_final_gate import build_promoted_weights
from src.reporting.metrics import calculate_metrics
from src.rl.environment_v2 import PortfolioEnvV2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Training / validation split — same as Phase D
TRAIN_START = "2008-01-01"
TRAIN_END = "2016-12-31"
VAL_START = "2017-01-01"
VAL_END = "2018-12-31"

# PPO hyperparameters
POLICY = "MlpPolicy"
NET_ARCH = [128, 128]   # wider than Phase D [64, 64] to handle 42-dim state
SEED = 42
N_STEPS = 512
BATCH_SIZE = 64
N_EPOCHS = 10
LEARNING_RATE = 3e-4

# Training loop
MAX_EPISODES = 1000
PATIENCE = 50
CHECKPOINT_EVERY = 100
STEPS_PER_EPISODE = 512

# E.7 effective reward lambdas — these are what the env actually uses during training
# (env.__init__ defaults, not reward_v2.py function defaults; see module docstring for context)
LAMBDA_DD_E7_EFFECTIVE    = 0.15   # env default; reward_v2.py function default is 0.08
LAMBDA_CASH_E7_EFFECTIVE  = 0.03   # env default; reward_v2.py function default is 0.05
LAMBDA_CHURN_E7_EFFECTIVE = 0.02   # unchanged across E.4 / E.7


def _sharpe_from_env_rollout(env: PortfolioEnvV2, model: PPO) -> float:
    """Run a full episode on env using model; return annualised Sharpe from daily NAV."""
    obs, _ = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _reward, terminated, truncated, _info = env.step(action)
        done = terminated or truncated
    daily_nav = env._nav_series
    if len(daily_nav) < 22:
        return np.nan
    m = calculate_metrics(daily_nav)
    return float(m.get("Sharpe", np.nan))


def make_env_fn(inputs, b5_weights_df, start_date, end_date, rebalance_dates, sector_features_df):
    """Factory for DummyVecEnv — preloads sector_features_df to avoid repeated disk reads.

    Lambda values are pinned explicitly so future env default changes do not silently alter
    training behaviour. Values match what E.7 was effectively trained with (see module docstring).
    """
    def _make():
        return PortfolioEnvV2(
            inputs, b5_weights_df,
            start_date=start_date, end_date=end_date,
            rebalance_dates=rebalance_dates,
            sector_features_df=sector_features_df,
            lambda_dd=LAMBDA_DD_E7_EFFECTIVE,
            lambda_cash=LAMBDA_CASH_E7_EFFECTIVE,
            lambda_churn=LAMBDA_CHURN_E7_EFFECTIVE,
        )
    return _make


def main():
    parser = argparse.ArgumentParser(description="Phase E.5 — PPO RL training v2")
    parser.add_argument("--config", default="config/base.yaml")
    parser.add_argument("--universe", default="config/universes/sp500.yaml")
    parser.add_argument("--max-episodes", type=int, default=MAX_EPISODES)
    parser.add_argument("--patience", type=int, default=PATIENCE)
    parser.add_argument(
        "--total-timesteps", type=int, default=None,
        help="If set, train for exactly this many env steps (smoke test). Ignores --max-episodes.",
    )
    parser.add_argument(
        "--eval-freq", type=int, default=STEPS_PER_EPISODE,
        help="Validate every N env steps (used with --total-timesteps). Default: STEPS_PER_EPISODE.",
    )
    args = parser.parse_args()

    out_dir = REPO_ROOT / "artifacts"
    models_dir = out_dir / "models"
    reports_dir = out_dir / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    logger.info("Loading inputs …")
    inputs = load_inputs(args.config, args.universe, TREND_ASSETS)
    validation_end = recommended_end_for_universe(
        inputs["universe_config"].name, inputs["prices"].index.max()
    )
    logger.info("validation_end=%s", validation_end.date())

    logger.info("Building beta/stress …")
    beta_frame = rolling_beta_matrix(inputs["prices"], inputs["universe_config"].benchmark)
    stress_series = build_stress_series(inputs)

    logger.info("Building B.5 constrained weights (full period) …")
    b5_weights_df, _diag, _ctrl = build_promoted_weights(
        inputs, validation_end, beta_frame, stress_series
    )
    logger.info("B.5 weights shape: %s, time %.1fs", b5_weights_df.shape, time.perf_counter() - t0)

    # Preload sector features once — shared across all envs
    logger.info("Loading sector features …")
    sector_features_df = pd.read_parquet(REPO_ROOT / "data" / "features" / "sector_features.parquet")
    logger.info("Sector features loaded: %s", sector_features_df.shape)

    train_ctrl = [d for d in _ctrl if pd.Timestamp(TRAIN_START) <= d <= pd.Timestamp(TRAIN_END)]
    val_ctrl   = [d for d in _ctrl if pd.Timestamp(VAL_START)   <= d <= pd.Timestamp(VAL_END)]
    logger.info("Rebalance dates — train: %d, val: %d", len(train_ctrl), len(val_ctrl))
    if len(train_ctrl) < 5:
        raise ValueError(f"Too few training rebalance dates ({len(train_ctrl)})")
    if len(val_ctrl) < 2:
        raise ValueError(f"Too few validation rebalance dates ({len(val_ctrl)})")

    logger.info("Building training environment (PortfolioEnvV2) …")
    train_vec_env = DummyVecEnv([
        make_env_fn(inputs, b5_weights_df, TRAIN_START, TRAIN_END, _ctrl, sector_features_df)
    ])

    val_env = PortfolioEnvV2(
        inputs, b5_weights_df, start_date=VAL_START, end_date=VAL_END,
        rebalance_dates=_ctrl, sector_features_df=sector_features_df,
        lambda_dd=LAMBDA_DD_E7_EFFECTIVE,
        lambda_cash=LAMBDA_CASH_E7_EFFECTIVE,
        lambda_churn=LAMBDA_CHURN_E7_EFFECTIVE,
    )

    model = PPO(
        POLICY,
        train_vec_env,
        learning_rate=LEARNING_RATE,
        n_steps=N_STEPS,
        batch_size=BATCH_SIZE,
        n_epochs=N_EPOCHS,
        policy_kwargs={"net_arch": NET_ARCH},
        seed=SEED,
        verbose=0,
    )

    best_val_sharpe = -np.inf
    patience_counter = 0
    log_rows = []

    def _run_eval_step(step_label: str, step_t: float) -> float:
        nonlocal best_val_sharpe, patience_counter
        v_sharpe = _sharpe_from_env_rollout(val_env, model)
        train_sharpe = np.nan
        if hasattr(model, "ep_info_buffer") and model.ep_info_buffer:
            rewards = [ep["r"] for ep in model.ep_info_buffer if "r" in ep]
            if rewards:
                train_sharpe = float(np.mean(rewards[-10:]))
        log_rows.append({
            "step_label": step_label,
            "train_sharpe_approx": train_sharpe,
            "val_sharpe": v_sharpe,
            "best_val_sharpe": best_val_sharpe,
            "patience_counter": patience_counter,
        })
        if np.isfinite(v_sharpe) and v_sharpe > best_val_sharpe:
            best_val_sharpe = v_sharpe
            model.save(str(models_dir / "rl_e_ppo_best"))
            patience_counter = 0
            logger.info(
                "%s: val_sharpe=%.4f NEW BEST — checkpoint saved (%.1fs)",
                step_label, v_sharpe, time.perf_counter() - step_t,
            )
        else:
            patience_counter += 1
            logger.info(
                "%s: val_sharpe=%.4f best=%.4f patience=%d (%.1fs)",
                step_label, v_sharpe, best_val_sharpe, patience_counter,
                time.perf_counter() - step_t,
            )
        return v_sharpe

    if args.total_timesteps is not None:
        eval_freq = args.eval_freq
        total = args.total_timesteps
        steps_done = 0
        logger.info("Timestep-budget mode: total_timesteps=%d, eval_freq=%d", total, eval_freq)
        while steps_done < total:
            chunk = min(eval_freq, total - steps_done)
            model.learn(total_timesteps=chunk, reset_num_timesteps=False)
            steps_done += chunk
            _run_eval_step(f"step={steps_done}", time.perf_counter())
    else:
        logger.info(
            "Episode mode: max_episodes=%d, patience=%d, steps_per_episode=%d",
            args.max_episodes, args.patience, STEPS_PER_EPISODE,
        )
        for episode in range(1, args.max_episodes + 1):
            t_ep = time.perf_counter()
            model.learn(total_timesteps=STEPS_PER_EPISODE, reset_num_timesteps=False)
            _run_eval_step(f"ep={episode}", t_ep)

            if episode % CHECKPOINT_EVERY == 0:
                ckpt_path = models_dir / f"rl_e_ppo_ep{episode:04d}"
                model.save(str(ckpt_path))
                logger.info("Checkpoint saved: %s", ckpt_path)

            if patience_counter >= args.patience:
                logger.info("Early stopping at episode %d (patience=%d)", episode, args.patience)
                break

    final_path = models_dir / "rl_e_ppo_final"
    model.save(str(final_path))
    logger.info("Final model saved: %s", final_path)

    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(reports_dir / "phase_e5_training_log.csv", index=False)
    logger.info("Training log saved: %d rows", len(log_df))
    logger.info(
        "Training complete: best_val_sharpe=%.4f, total_time=%.1fs",
        best_val_sharpe, time.perf_counter() - t0,
    )


if __name__ == "__main__":
    main()
