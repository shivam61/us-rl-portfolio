import numpy as np
import pandas as pd

from src.optimizer.portfolio_optimizer import PortfolioOptimizer


def test_optimizer_fallback_never_crashes_and_returns_valid_weights(monkeypatch):
    optimizer = PortfolioOptimizer(
        max_stock_weight=0.20,
        max_sector_weight=0.40,
        max_turnover=0.30,
        cash_min=0.0,
        cash_max=0.30,
    )
    alpha_scores = pd.Series(
        [5.0, 4.0, 3.0, 2.0, 1.0],
        index=["A", "B", "C", "D", "E"],
    )
    cov_matrix = pd.DataFrame(np.eye(5), index=alpha_scores.index, columns=alpha_scores.index)
    current_weights = pd.Series(0.0, index=alpha_scores.index)
    sector_mapping = {"A": "S1", "B": "S1", "C": "S2", "D": "S2", "E": "S3"}

    def always_fail(*args, **kwargs):
        return {
            "weights": None,
            "attempt_diag": {"status": "forced_failure"},
            "constraint_violations": {},
        }

    monkeypatch.setattr(optimizer, "_solve_once", always_fail)
    weights, diagnostics = optimizer.optimize(alpha_scores, cov_matrix, current_weights, sector_mapping)

    assert diagnostics["fallback_level"] == "equal_weight_top_n"
    assert not weights.empty
    assert (weights >= -1e-12).all()
    assert weights.sum() <= 1.0 + 1e-9
    assert weights.max() <= optimizer.max_stock_weight + 1e-9
    sector_weights = weights.groupby(weights.index.map(lambda t: sector_mapping.get(t, "_other"))).sum()
    assert (sector_weights <= optimizer.max_sector_weight + 1e-9).all()


def test_optimizer_real_solve_returns_valid_weights():
    optimizer = PortfolioOptimizer(
        max_stock_weight=0.35,
        max_sector_weight=0.70,
        max_turnover=0.50,
        cash_min=0.0,
        cash_max=0.30,
    )
    alpha_scores = pd.Series(
        [2.5, 1.0, -0.5, 0.2],
        index=["A", "B", "C", "D"],
    )
    cov_matrix = pd.DataFrame(
        [
            [0.05, 0.01, 0.00, 0.00],
            [0.01, 0.06, 0.01, 0.00],
            [0.00, 0.01, 0.04, 0.00],
            [0.00, 0.00, 0.00, 0.03],
        ],
        index=alpha_scores.index,
        columns=alpha_scores.index,
    )
    current_weights = pd.Series(0.0, index=alpha_scores.index)
    sector_mapping = {"A": "S1", "B": "S1", "C": "S2", "D": "S3"}

    weights, diagnostics = optimizer.optimize(alpha_scores, cov_matrix, current_weights, sector_mapping)

    assert diagnostics["fallback_level"] in {"full_optimizer", "relaxed_constraints", "equal_weight_top_n"}
    assert not weights.empty
    assert (weights >= -1e-12).all()
    assert weights.sum() <= 1.0 + 1e-9
    assert weights.max() <= optimizer.max_stock_weight + 1e-6
    sector_weights = weights.groupby(weights.index.map(lambda t: sector_mapping.get(t, "_other"))).sum()
    assert (sector_weights <= optimizer.max_sector_weight + 1e-6).all()
