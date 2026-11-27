"""Resolved reward configuration for a run (R0 reproducibility guard).

The reward coefficients that the environment USES at runtime are the ones written to a run's
manifest, not the signature defaults of compute_reward_v2 (which differ from the env defaults).
"""
import inspect

from src.rl.reward_v2 import compute_reward_v2

RECOVERY_COEF = 0.10   # hard-coded inside compute_reward_v2 (term 2)
SHARPE_WINDOW = 63     # hard-coded inside compute_reward_v2 (term 1)


def signature_defaults() -> dict:
    sig = inspect.signature(compute_reward_v2).parameters
    return {k: sig[k].default for k in ("lambda_dd", "lambda_cash", "lambda_churn")}


def resolved_reward_config(env) -> dict:
    """Runtime coefficients of a constructed PortfolioEnvV2 plus the function defaults for comparison."""
    return {
        "lambda_dd": float(env.lambda_dd),
        "lambda_cash": float(env.lambda_cash),
        "lambda_churn": float(env.lambda_churn),
        "recovery_coef": RECOVERY_COEF,
        "sharpe_window_days": SHARPE_WINDOW,
        "reward_fn": "compute_reward_v2",
        "reward_fn_signature_defaults": signature_defaults(),
    }
