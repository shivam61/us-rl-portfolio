import pandas as pd
import numpy as np
import pytest
from src.features.stock_features import StockFeatureGenerator
from src.labels.targets import TargetGenerator
from src.config.loader import load_config
import os

@pytest.fixture
def dummy_data():
    dates = pd.date_range("2020-01-01", periods=100)
    dates.name = "date" # Missing index name caused the error
    df = pd.DataFrame({
        "open": np.random.randn(100) + 100,
        "high": np.random.randn(100) + 102,
        "low": np.random.randn(100) + 98,
        "close": np.random.randn(100) + 100,
        "volume": np.random.randint(1000, 10000, size=100),
    }, index=dates)
    df["adj_close"] = df["close"]
    return {"AAPL": df}

def test_stock_features_lag(dummy_data):
    """
    Test that features are strictly lagged.
    """
    gen = StockFeatureGenerator(dummy_data)
    features = gen.generate()
    
    aapl_feats = features.xs("AAPL", level="ticker")
    # Feature available at T should only rely on info up to T-1
    assert "ret_1m" in aapl_feats.columns
    assert "pct_pos_months_6m" in aapl_feats.columns
    assert "sector_rel_momentum_6m" in aapl_feats.columns
    
    # Manually calculate T-1 return
    close = dummy_data["AAPL"]["adj_close"]
    date_t = aapl_feats.index[25]
    date_t_minus_1 = aapl_feats.index[24]
    
    expected_ret_1m_at_t = close.loc[date_t_minus_1] / close.shift(21).loc[date_t_minus_1] - 1.0
    actual_ret_1m_at_t = aapl_feats.loc[date_t, "ret_1m"]
    
    assert np.isclose(expected_ret_1m_at_t, actual_ret_1m_at_t, equal_nan=True)

def test_target_generation_forward(dummy_data):
    """
    Test that targets look forward correctly.
    """
    tg = TargetGenerator(dummy_data, forward_horizon=5)
    targets = tg.generate()
    
    aapl_targets = targets.xs("AAPL", level="ticker")
    assert "target_fwd_ret" in aapl_targets.columns
    
    close = dummy_data["AAPL"]["adj_close"]
    expected = close.iloc[10] / close.iloc[5] - 1.0
    target_val = aapl_targets.iloc[5]["target_fwd_ret"]
    
    assert np.isclose(expected, target_val)

def test_simulator_execution_lag():
    from src.backtest.simulator import ExecutionSimulator
    
    config, _ = load_config("config/base.yaml", "config/universes/sp100.yaml")
    sim = ExecutionSimulator(config=config)
    
    # target weight signal
    target = pd.Series({"AAPL": 1.0})
    
    # execution date T+1 prices
    date = pd.Timestamp("2020-01-02")
    prices_open = pd.Series({"AAPL": 105.0})
    prices_close = pd.Series({"AAPL": 106.0})
    vol = pd.Series({"AAPL": 2e6})
    adv = pd.Series({"AAPL": 20000000.0}) # Make sure ADV > 10,000,000 (min_adv_dollar in config)
    
    sim.rebalance(target, date, prices_open, prices_close, vol, adv)
    
    trades = sim.get_trades()
    assert not trades.empty
    
    # Verify execution price is open (105) not close
    exec_price = trades.iloc[0]["price"]
    assert exec_price == 105.0


def test_intraperiod_overlay_uses_prior_close_signal():
    from src.backtest.walk_forward import WalkForwardEngine

    config, universe = load_config("config/base.yaml", "config/universes/sp100.yaml")
    config.intraperiod_risk.enabled = True
    config.intraperiod_risk.benchmark_return_window = 5
    config.intraperiod_risk.benchmark_return_trigger = -0.06
    config.intraperiod_risk.vix_change_window = 3
    config.intraperiod_risk.vix_change_trigger = 0.40
    config.intraperiod_risk.exposure_multiplier = 0.60

    dates = pd.bdate_range("2020-01-01", periods=8)
    adj_close = pd.DataFrame(
        {
            "SPY": [100.0, 100.0, 100.0, 100.0, 100.0, 93.0, 93.0, 93.0],
            "^VIX": [20.0] * 8,
            "AAPL": [50.0] * 8,
        },
        index=dates,
    )
    prices_dict = {
        "open": adj_close.copy(),
        "close": adj_close.copy(),
        "adj_close": adj_close.copy(),
        "volume": pd.DataFrame(1_000_000, index=dates, columns=adj_close.columns),
    }

    engine = WalkForwardEngine(
        config=config,
        universe_config=universe,
        stock_features=pd.DataFrame(),
        macro_features=pd.DataFrame(),
        targets=pd.DataFrame(),
        prices_dict=prices_dict,
    )

    signal_date = dates[5]
    execution_date = dates[6]
    assert bool(engine.intraperiod_signals.loc[signal_date, "active"])

    state = engine._intraperiod_overlay_state(execution_date)
    assert state["signal_date"] == str(signal_date.date())
    assert state["active"] is True
    assert state["target_multiplier"] == 0.60
