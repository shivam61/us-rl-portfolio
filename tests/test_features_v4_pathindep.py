"""M3 path independence, M4 causal normalisation and warm-up NaN policy, pre-inception masking (FH task 3)."""
import numpy as np
import pandas as pd
import pytest

from features_v4_helpers import load_history, truncate
from src.rl import features_risk_v4 as L
from src.rl.features_risk_v4 import FEATURE_NAMES, ORIGIN, build_panel, features_at
from src.rl.features_v4_env import V4FeatureStore, WarmupError, build_state_v4

NAV_DERIVED = ("dd_b", "dsp_b", "rec_b", "spd_b_5", "spd_b_21", "base_gross", "worst_dec_share",
               "corr_held_21", "corr_held_63", "disp_held_21")


@pytest.fixture(scope="module")
def H():
    return load_history()


@pytest.fixture(scope="module")
def full(H):
    return build_panel(H)


@pytest.fixture(scope="module")
def store(H):
    return V4FeatureStore(H)


def test_mid_history_start_is_rejected(H):
    """M3: an episode-local history (starting after ORIGIN) must be refused, not silently re-based."""
    late = {k: (v.loc["2010-01-01":] if hasattr(v, "loc") else v) for k, v in H.items()}
    with pytest.raises(ValueError):
        features_at(pd.Timestamp("2012-06-01"), late)
    with pytest.raises(ValueError):
        V4FeatureStore(late)


def test_path_independence_mid_history_start(H, full):
    """M3: features_at from ORIGIN equals the continuous panel at several dates, independent of call order."""
    dates = [pd.Timestamp(d) for d in ["2016-03-15", "2009-02-02", "2020-03-16"]]
    for d in dates[::-1]:  # reversed call order
        a = features_at(d, H).astype(float).values
        b = full.loc[d, FEATURE_NAMES].astype(float).values
        assert np.allclose(a, b, equal_nan=True, atol=1e-12), d


def test_no_episode_local_state(store, full):
    """M3/M10: a store read at date d does not depend on which dates were read before it."""
    rng = np.random.default_rng(3)
    dates = [pd.Timestamp(d) for d in ["2008-10-10", "2012-06-01", "2020-03-16", "2024-05-01"]]
    order = list(rng.permutation(len(dates)))
    for i in order:
        d = dates[i]
        assert np.allclose(store.row(d), full.loc[d, FEATURE_NAMES].astype(float).values, equal_nan=True,
                           atol=1e-12)


def test_pre_inception_nav_features_are_nan(full):
    """FH task 3: NAV-derived features are NaN before the baseline book exists (no fillna(0) rows)."""
    pre = full.index[full.index < pd.Timestamp("2008-01-07")]
    assert len(pre) > 100
    raw = full.attrs["raw"]
    for k in NAV_DERIVED:
        assert raw.loc[pre, k].isna().all(), f"{k} has values before inception"
    # z-scores of these features are NaN pre-inception as well
    assert full.loc[pre, list(NAV_DERIVED)].isna().all().all()


def test_pre_inception_not_in_zscore_baseline(full):
    """FH task 3: the expanding baseline of dd_b uses only post-inception rows (count = raw non-NaN rows)."""
    raw = full.attrs["raw"]["dd_b"]
    assert raw.loc[raw.index < pd.Timestamp("2008-01-07")].isna().all()  # no pre-inception zeros
    z_first = full["dd_b"].first_valid_index()
    n_raw = int(raw.loc[:z_first].notna().sum())
    assert n_raw >= L.Z_MIN, f"z-score fired with {n_raw} < {L.Z_MIN} baseline observations"
    # and the z-score at its first valid date is computed from exactly the post-inception raw values
    x = raw.loc[:z_first].dropna()
    manual = float(np.clip((x.iloc[-1] - x.mean()) / x.std(), -3, 3))  # expanding window includes t
    assert abs(manual - full.loc[z_first, "dd_b"]) < 1e-9


def test_causal_normalisation(H):
    """M4: the z-score of a feature at t uses only the mean/std of its raw values dated <= t, clipped to +-3."""
    P = build_panel(H)
    raw = P.attrs["raw"]
    for k in ("rv_u_21", "vix_level", "dd_s"):
        x = raw[k].astype(float)
        if L.FEATURES[k][1] == "log":
            x = np.log(x.clip(lower=1e-6))
        for d in [pd.Timestamp("2011-05-03"), pd.Timestamp("2020-03-16"), pd.Timestamp("2024-02-01")]:
            hist = x.loc[:d].dropna()
            if len(hist) < L.Z_MIN:
                continue
            m, s = hist.mean(), hist.std()
            manual = float(np.clip((x.loc[d] - m) / s, -3, 3))
            assert abs(manual - P.loc[d, k]) < 1e-9, (k, d.date(), manual, P.loc[d, k])


def test_warmup_nan_policy(store, full):
    """M4: no zero-filling. Inside warm-up the store has NaN and build_state_v4 raises WarmupError; from the
    first full date onward the observation is finite."""
    first_full = store.first_full_date()
    assert first_full > pd.Timestamp("2008-01-02")
    before = pd.Timestamp("2008-01-02")
    assert not store.valid(before)
    with pytest.raises(WarmupError):
        build_state_v4(before, store, {"equity_share": 0.5})
    obs = build_state_v4(first_full, store, {"equity_share": 0.5})
    assert np.isfinite(obs).all() and obs.shape == (len(FEATURE_NAMES) + 1,)


def test_no_clip_pinning_last_30_days(full):
    """FH task 1 (tail fix): no feature sits at a clip bound (+-3) on most of the last 30 valid days. The
    v4 build pinned rv_u_5 at -3 after the H1 cache end because unit returns were zero-filled."""
    tail = full.loc[: pd.Timestamp("2026-04-24")].tail(30)
    for k in FEATURE_NAMES:
        s = tail[k].dropna()
        pinned = int(((s.abs() - 3.0).abs() < 1e-12).sum())
        assert pinned < 20, f"{k} pinned at a clip bound on {pinned} of the last {len(s)} days"


def test_unit_returns_not_zero_filled_after_data_end(H):
    """FH task 1: the canonical unit return is NaN (not zero) wherever a held name has no return."""
    u = H["unit_ret"]
    held = H["unit_w"].shift(1).fillna(0.0)
    held_no_ret = ((held != 0) & H["stocks"].pct_change(fill_method=None).isna()).any(axis=1)
    assert u[held_no_ret].isna().all()
    assert (u.loc[: pd.Timestamp("2008-01-07")].isna()).all()
