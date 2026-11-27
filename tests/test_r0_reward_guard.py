"""R0 reward reproducibility guard.

Checks that the coefficients a run uses are explicit (not silently inherited from a signature
default) and that the decomposition used by the R0 report equals compute_reward_v2.
"""
import inspect
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.rl import environment_v2 as envmod  # noqa: E402
from src.rl.reward_config import resolved_reward_config, signature_defaults  # noqa: E402
from src.rl.reward_v2 import compute_reward_v2  # noqa: E402

TRAIN_SRC = (REPO / "scripts" / "train_rl_v2.py").read_text()


def test_env_passes_lambdas_explicitly_to_reward():
    src = inspect.getsource(envmod.PortfolioEnvV2.step)
    for name in ("lambda_dd", "lambda_cash", "lambda_churn"):
        assert f"{name}=self.{name}" in src


def test_train_script_pins_lambdas_explicitly():
    for name in ("LAMBDA_DD_E7_EFFECTIVE", "LAMBDA_CASH_E7_EFFECTIVE", "LAMBDA_CHURN_E7_EFFECTIVE"):
        assert f"{name}" in TRAIN_SRC
    assert "lambda_dd=LAMBDA_DD_E7_EFFECTIVE" in TRAIN_SRC
    assert "lambda_cash=LAMBDA_CASH_E7_EFFECTIVE" in TRAIN_SRC


@pytest.mark.xfail(strict=True, reason="KNOWN DRIFT: compute_reward_v2 defaults (0.08/0.05) differ from "
                   "PortfolioEnvV2 defaults (0.15/0.03). Remove xfail once one source of truth is used.")
def test_signature_defaults_equal_env_defaults():
    env_sig = inspect.signature(envmod.PortfolioEnvV2.__init__).parameters
    env_defaults = {k: env_sig[k].default for k in ("lambda_dd", "lambda_cash", "lambda_churn")}
    assert signature_defaults() == env_defaults


def test_train_script_writes_manifest_with_resolved_reward_config():
    assert "run_manifest.json" in TRAIN_SRC
    assert "resolved_reward_config(val_env)" in TRAIN_SRC


def test_resolved_config_reports_runtime_not_signature_values():
    env = SimpleNamespace(lambda_dd=0.15, lambda_cash=0.03, lambda_churn=0.02)
    cfg = resolved_reward_config(env)
    assert (cfg["lambda_dd"], cfg["lambda_cash"], cfg["lambda_churn"]) == (0.15, 0.03, 0.02)
    assert cfg["reward_fn_signature_defaults"]["lambda_dd"] == 0.08


def test_decomposition_equals_compute_reward_v2():
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2010-01-01", periods=40)
    dr = pd.Series(rng.normal(0.0005, 0.01, len(idx)), index=idx)
    nav = (1 + dr).cumprod()
    nav = pd.concat([pd.Series([1.0], index=[idx[0] - pd.Timedelta(days=1)]), nav])
    kw = dict(lambda_dd=0.15, lambda_cash=0.03, lambda_churn=0.02)
    r = compute_reward_v2(daily_returns=dr, portfolio_nav=nav, equity_frac=0.8, prev_equity_frac=0.6,
                          cash_frac=0.2, spy_trend_positive=True, **kw)
    w = dr.iloc[-63:] if len(dr) >= 63 else dr
    sh = float(w.mean() / w.std(ddof=1) * np.sqrt(252))
    rn = nav.iloc[-63:] if len(nav) >= 63 else nav
    rec = 0.10 * max(0.0, (rn.iloc[-1] - rn.min()) / rn.min())
    peak = nav.expanding().max().iloc[-1]
    ddp = 0.15 * max(0.0, -(nav.iloc[-1] - peak) / peak)
    manual = sh + rec - ddp - 0.03 * 0.2 - 0.02 * abs(0.8 - 0.6)
    assert r == pytest.approx(manual, abs=1e-12)


def test_recorded_rollouts_reconstruct_env_reward():
    base = REPO / "runs_r0" / "main" / "rollouts"
    files = sorted(base.glob("*__steps.csv")) if base.exists() else []
    if not files:
        pytest.skip("no R0 rollouts recorded yet")
    worst = 0.0
    for f in files:
        df = pd.read_csv(f)
        worst = max(worst, float((df["reward_recon"] - df["reward_env"]).abs().max()))
    assert worst < 1e-9
