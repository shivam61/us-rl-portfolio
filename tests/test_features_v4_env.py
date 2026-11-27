"""M5 train/serve parity and M10 agent independence for the v4.1 plug-in (build_state_v4). Not wired into training."""
import ast
import os

import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import ROOT, load_daily, load_history
from src.rl.features_risk_v4 import FEATURE_NAMES, features_at
from src.rl.features_v4_env import OBS_NAMES, V4FeatureStore, build_state_v4

PARITY_DATES = ["2008-12-01", "2012-06-01", "2020-03-16"]  # GFC (first full date is 2008-10-31), mid-sample, 2020


@pytest.fixture(scope="module")
def H():
    return load_history()


@pytest.fixture(scope="module")
def store(H):
    return V4FeatureStore(H)


@pytest.mark.parametrize("date", PARITY_DATES)
def test_train_serve_parity_one_rebalance_date(H, store, date):
    """M5: the env-side observation (shared store), the prod-path observation (features_at on the causal
    history) and the materialised training table agree to 1e-9 on a historical rebalance date."""
    d = pd.Timestamp(date)
    agent = {"equity_share": 0.72}
    env_obs = build_state_v4(d, store, agent)
    prod_row = features_at(d, H).astype(float).to_numpy()
    table_row = load_daily().loc[d, FEATURE_NAMES].astype(float).to_numpy()
    assert np.allclose(env_obs[:-1], prod_row, rtol=0, atol=1e-9), "env vs prod path"
    assert np.allclose(env_obs[:-1], table_row, rtol=0, atol=1e-9), "env vs training table"
    assert env_obs[-1] == 0.72


def test_build_state_v4_takes_only_equity_share(store):
    """M10: the agent may contribute its equity share and nothing else."""
    d = pd.Timestamp("2015-06-01")
    with pytest.raises(KeyError):
        build_state_v4(d, store, {"equity_share": 0.5, "nav": 1.2})
    with pytest.raises(KeyError):
        build_state_v4(d, store, {"equity_share": 0.5, "position": 3})
    with pytest.raises(ValueError):
        build_state_v4(d, store, {"equity_share": 1.5})
    obs = build_state_v4(d, store, {"equity_share": 0.25})
    assert obs.shape == (len(OBS_NAMES),) and obs.dtype == np.float64 and OBS_NAMES[-1] == "equity_share"


def test_library_reads_no_agent_state():
    """M10: the feature library and the store never read agent quantities: the only history keys used are
    market and book inputs."""
    src = open(os.path.join(ROOT, "src", "rl", "features_risk_v4.py")).read()
    keys = {n.slice.value for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == "history"
            and isinstance(n.slice, ast.Constant)}
    assert not keys & {"nav", "positions", "actions", "equity_frac", "agent"}, keys
    env_src = open(os.path.join(ROOT, "src", "rl", "features_v4_env.py")).read()
    for banned in ("nav_series", "_current_weights", "_step_idx"):
        assert banned not in env_src, banned


def test_warmup_dates_are_refused(store):
    """M4: the store refuses (WarmupError) any date before the first full date."""
    from src.rl.features_v4_env import WarmupError
    with pytest.raises(WarmupError):
        build_state_v4(pd.Timestamp("2008-01-02"), store, {"equity_share": 1.0})
