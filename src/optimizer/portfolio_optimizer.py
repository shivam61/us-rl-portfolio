import numpy as np
import pandas as pd
import cvxpy as cp
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    def __init__(self, 
                 max_stock_weight: float = 0.05,
                 max_sector_weight: float = 0.25,
                 max_turnover: float = 0.30,
                 cash_min: float = 0.00,
                 cash_max: float = 0.30):
        self.max_stock_weight = max_stock_weight
        self.max_sector_weight = max_sector_weight
        self.max_turnover = max_turnover
        self.cash_min = cash_min
        self.cash_max = cash_max
        
    def optimize(self,
                 alpha_scores: pd.Series,
                 cov_matrix: pd.DataFrame,
                 current_weights: pd.Series,
                 sector_mapping: Dict[str, str],
                 risk_aversion: float = 1.0,
                 turnover_penalty: float = 0.1) -> pd.Series:
        """
        Optimize portfolio weights using Mean-Variance formulation with turnover penalty.
        """
        tickers = list(alpha_scores.index)
        n = len(tickers)
        
        if n == 0:
            return pd.Series(dtype=float)
            
        # Align inputs
        mu = alpha_scores.values
        Sigma = cov_matrix.loc[tickers, tickers].values
        w_curr = np.array([current_weights.get(t, 0.0) for t in tickers])
        
        # Variables
        w = cp.Variable(n)
        cash = cp.Variable(1)
        
        # Objective: Maximize alpha - risk_aversion * risk - turnover_penalty * turnover
        ret = mu.T @ w
        risk = cp.quad_form(w, Sigma)
        turnover = cp.norm(w - w_curr, 1)
        
        objective = cp.Maximize(ret - risk_aversion * risk - turnover_penalty * turnover)
        
        # Constraints
        constraints = [
            w >= 0, # Long only
            cash >= self.cash_min,
            cash <= self.cash_max,
            cp.sum(w) + cash == 1.0,
            w <= self.max_stock_weight
        ]
        
        # Sector constraints
        sectors = set(sector_mapping.values())
        for sector in sectors:
            sector_idx = [i for i, t in enumerate(tickers) if sector_mapping.get(t) == sector]
            if sector_idx:
                constraints.append(cp.sum(w[sector_idx]) <= self.max_sector_weight)
                
        # Turnover constraint
        constraints.append(turnover <= self.max_turnover * 2) # max_turnover is one-way
        
        prob = cp.Problem(objective, constraints)
        
        try:
            prob.solve(solver=cp.OSQP)
            if prob.status not in ["optimal", "optimal_inaccurate"]:
                logger.warning(f"Optimizer status: {prob.status}. Using fallback.")
                return self._fallback_equal_weight(alpha_scores)
                
            weights = pd.Series(w.value, index=tickers)
            weights[weights < 1e-4] = 0.0
            return weights / weights.sum() * (1 - cash.value[0])
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}. Using fallback.")
            return self._fallback_equal_weight(alpha_scores)
            
    def _fallback_equal_weight(self, alpha_scores: pd.Series) -> pd.Series:
        # Sort and take top 20 or len/2
        top_n = max(10, len(alpha_scores) // 2)
        top_stocks = alpha_scores.nlargest(top_n).index
        w = pd.Series(0.0, index=alpha_scores.index)
        w[top_stocks] = 1.0 / len(top_stocks)
        return w
