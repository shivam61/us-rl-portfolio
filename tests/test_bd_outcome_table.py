"""BD0 tests: outcome table (docs/phases/rl_bandit_plan.md section 9).

- weights: finalize_equity_only gives stock weights summing to the arm (no hidden floor).
- fill delay: decision at close t, first earned return is close(t+2)/close(t+1) at FILL_LAG = 1.
- env parity: with fill at close t (lag 0), the repo PortfolioEnvV2 (equity-only, 10 bps) reproduces
  the outcome engine's daily net returns to 1e-6 on a sampled window (arm mapping overridden in-process
  as in FM, since the env's own 2-dim map cannot reach shares below 0.5).
- no look-ahead in X0: truncation and future corruption leave earlier contexts unchanged.
- sealed cut: no period extends beyond TERMINAL; the terminal period is present.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from rl import bd_core as C  # noqa: E402

# BD inputs (runs_bd/inputs) are materialised copies of the FH feature outputs and are not committed.
pytestmark = pytest.mark.skipif(not (C.INPUT_DIR / "history_v41.pkl").exists(),
                                reason="runs_bd/inputs not built (see docs/phases/rl_bandit_plan.md)")
from src.rl.exposure_mix import finalize_equity_only  # noqa: E402


@pytest.fixture(scope="module")
def h():
    return C.load_history()


@pytest.fixture(scope="module")
def g14(h):
    return C.build_grid("14d", h)


@pytest.fixture(scope="module")
def g8(h):
    return C.build_grid("8w", h)


def test_weights_sum_to_arm_no_floor(g14):
    for a in C.ARMS_UNION:
        for i in range(0, g14.n, 37):
            w = pd.Series(g14.book[i], index=g14.cols) * a
            fw = finalize_equity_only(w, a)
            assert abs(float(fw.abs().sum()) - a) < 1e-9
            assert set(fw.index).isdisjoint({"SPY", "TLT", "GLD", "UUP"})
    # low arms are representable exactly (no 0.5 floor inside the outcome engine)
    r, _ = C.period_returns(g14, 100, 0.25, 0.0)
    assert len(r) > 0


def test_control_dates_equal_8w_grid_file(h, g8):
    grid8 = pd.DatetimeIndex(pd.read_parquet(C.INPUT_DIR / "grid_8w_v4.parquet").index)
    grid8 = grid8[(grid8 >= C.FIRST_SNAPSHOT) & (grid8 <= C.TERMINAL)]
    assert list(g8.dates) == list(grid8)


def test_book_is_fully_invested_at_decisions(g14, g8):
    for g in (g14, g8):
        s = g.book.sum(axis=1)
        assert np.allclose(s, 1.0, atol=1e-9)
        assert g.dates[0] >= C.FIRST_SNAPSHOT  # D1: no empty-book decision


def test_fill_delay_one_day(h):
    g0 = C.build_grid("14d", h, fill_lag=0)
    g1 = C.build_grid("14d", h, fill_lag=1)
    cal = pd.DatetimeIndex(h["unit_ret"].index)
    i = 50
    assert g0.dates[i] == g1.dates[i]
    # lag 0 earns close(t+1)/close(t) first; lag 1 earns close(t+2)/close(t+1) first
    assert g0.q_dates[i][0] == cal[g0.dpos[i] + 1]
    assert g1.q_dates[i][0] == cal[g1.dpos[i] + 2]
    assert g1.dpos[i] == g0.dpos[i]
    # the day-1 return of lag 1 is the day-2 return of lag 0 (same book, same stocks)
    r0 = C.period_returns(g0, i, 1.0, 1.0, 0.0)[0]
    r1 = C.period_returns(g1, i, 1.0, 1.0, 0.0)[0]
    assert np.allclose(r1[0], r0[1], atol=1e-14)


def test_periods_contiguous_and_terminal_included(g14, g8):
    for g in (g14, g8):
        for i in range(g.n - 1):
            assert g.end_pos[i] == g.fill_pos[i + 1]
            assert g.q_dates[i][-1] < g.q_dates[i + 1][0] + pd.Timedelta(days=1)
        assert g.q_dates[-1][-1] == C.TERMINAL  # terminal period simulated (D3)
        assert all(q[-1] <= C.TERMINAL for q in g.q_dates)


def test_outcome_rows_respect_cut(h):
    tbl = C.outcome_table(C.build_grid("8w", h), arms=(0.25, 1.0), prevs=(0.0, 1.0))
    assert tbl.period_end.max() <= C.TERMINAL
    assert (tbl.n_days > 0).all()
    assert len(tbl) == 120 * 2 * 2


def test_cost_only_on_turnover(g14):
    r_nocost, t0 = C.period_returns(g14, 60, 0.625, 0.625, 10.0)
    r_gross, _ = C.period_returns(g14, 60, 0.625, 0.625, 0.0)
    assert t0 == pytest.approx(np.abs(0.625 * g14.book[60] - 0.625 * g14.book[59]).sum())
    # same share and same book: turnover only from the book change at the previous decision
    if t0 == 0:
        assert np.allclose(r_nocost, r_gross)
    r_first, t_first = C.period_returns(g14, 60, 0.625, 0.0, 10.0)
    assert t_first == pytest.approx(0.625)
    assert r_first[0] == pytest.approx((1 - 10e-4 * 0.625) * (1 + C.period_returns(g14, 60, 0.625, 0.0, 0.0)[0][0]) - 1)


def _x_truncated(h, t):
    out = dict(h)
    for k in ["unit_ret", "base_ret", "spy", "vix", "stress"]:
        out[k] = h[k].loc[h[k].index <= t]
    return out


def test_x0_no_lookahead_truncation_and_corruption(h):
    full = C.x0_daily(h)
    rng = np.random.default_rng(0)
    for t in [pd.Timestamp("2011-06-15"), pd.Timestamp("2016-03-01"), pd.Timestamp("2021-10-29")]:
        tr = C.x0_daily(_x_truncated(h, t))
        a = full.loc[full.index <= t, C.X0_COLS]
        b = tr.loc[tr.index <= t, C.X0_COLS]
        assert np.allclose(a.values, b.values, equal_nan=True, atol=1e-12)
        # future corruption: replace every observation after t with noise
        cor = dict(h)
        for k in ["unit_ret", "base_ret", "spy", "vix", "stress"]:
            s = h[k].copy()
            m = s.index > t
            if k in ("unit_ret", "base_ret"):
                s.loc[m] = rng.normal(size=int(m.sum())) * 0.05  # returns: large but finite
            else:
                s.loc[m] = 10.0 + rng.normal(size=int(m.sum()))  # levels / stress
            cor[k] = s
        c = C.x0_daily(cor)
        cc = c.loc[c.index <= t, C.X0_COLS]
        assert np.allclose(a.values, cc.values, equal_nan=True, atol=1e-12)


def _direct_mix(b5_weights, trend_tickers, raw_action):
    """Test-only: map the 2-dim env action straight to a share (env 2-dim map floors at 0.5)."""
    eq = float(np.asarray(raw_action, dtype=float)[0])
    trend_set = set(trend_tickers)
    stock = b5_weights[[t for t in b5_weights.index if t not in trend_set]]
    tot = float(stock.abs().sum())
    res = pd.Series(0.0, index=b5_weights.index)
    if tot > 1e-12:
        res[stock.index] = stock * (eq / tot)
    return res, {"equity_frac": eq, "trend_frac": 0.0, "cash_frac": 1.0 - eq, "gross": float(res.abs().sum())}


def test_outcome_matches_repo_env(h):
    """Fill at close t (lag 0), 10 bps: env NAV daily returns equal the engine within 1e-6."""
    import src.rl.environment_v2 as env_mod
    from run_phase_a7_trend_overlay import TREND_ASSETS, load_inputs  # noqa: WPS433

    inputs = load_inputs("config/base.yaml", "config/universes/sp500.yaml", TREND_ASSETS)
    sector = pd.read_parquet(ROOT / "data/features/sector_features.parquet")
    g0 = C.build_grid("14d", h, fill_lag=0)
    lo, hi = 60, 90  # sampled window of decisions (2010-2011)
    idx = list(range(lo, hi))
    dates = list(g0.dates[lo:hi])
    b5 = h["unit_w"].loc[h["unit_w"].index <= dates[-1]]
    saved_mix, saved_dim = env_mod.apply_exposure_mix, env_mod.DEFAULT_ACTION_DIM
    env_mod.apply_exposure_mix = _direct_mix
    env_mod.DEFAULT_ACTION_DIM = 2
    try:
        for share in [1.0, 0.625, 0.8125]:
            env = env_mod.PortfolioEnvV2(
                inputs, b5, start_date=str(dates[0].date()), end_date=str(dates[-1].date()),
                rebalance_dates=dates, cost_bps=10.0, sector_features_df=sector,
            )
            env.reset()
            env._current_weights = None  # env pre-start row would be a 100% book; the engine starts empty
            done = False
            while not done:
                _, _, term, trunc, _ = env.step(np.asarray([share, 0.0], dtype=np.float32))
                done = term or trunc
            nav = env._nav_series
            env_daily = nav.pct_change().dropna()
            # engine: constant share over the same decisions, last decision's period excluded (env skips it)
            res = C.run_shares(g0, idx[:-1], [share] * (len(idx) - 1))
            daily, eng_dates, _ = C.flatten(res)
            eng = pd.Series(daily, index=eng_dates)
            common = env_daily.index.intersection(eng.index)
            assert len(common) > 100
            dev = float((env_daily.reindex(common) - eng.reindex(common)).abs().max())
            assert dev < 1e-6, (share, dev)
    finally:
        env_mod.apply_exposure_mix = saved_mix
        env_mod.DEFAULT_ACTION_DIM = saved_dim
