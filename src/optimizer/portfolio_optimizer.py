import logging
from typing import Dict

import cvxpy as cp
import numpy as np
import pandas as pd

from src.optimizer.covariance import covariance_condition_number, clip_covariance_eigenvalues

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    def __init__(
        self,
        max_stock_weight: float = 0.05,
        max_sector_weight: float = 0.25,
        max_turnover: float = 0.30,
        cash_min: float = 0.00,
        cash_max: float = 0.30,
    ):
        self.max_stock_weight = max_stock_weight
        self.max_sector_weight = max_sector_weight
        self.max_turnover = max_turnover
        self.cash_min = cash_min
        self.cash_max = cash_max

    def optimize(
        self,
        alpha_scores: pd.Series,
        cov_matrix: pd.DataFrame,
        current_weights: pd.Series,
        sector_mapping: Dict[str, str],
        risk_aversion: float = 1.0,
        turnover_penalty: float = 0.1,
    ) -> tuple[pd.Series, dict]:
        """
        Optimize portfolio weights using a deterministic fallback hierarchy:
        A. full optimizer
        B. relaxed constraints
        C. equal-weight Top-N
        """
        tickers = list(alpha_scores.index)
        n = len(tickers)
        if n == 0:
            return pd.Series(dtype=float), {"fallback_level": "empty", "num_assets": 0}

        alpha_scores = self._normalize_alpha_scores(alpha_scores.reindex(tickers).fillna(0.0))
        cov_matrix = self._stabilize_covariance(cov_matrix.loc[tickers, tickers])
        w_curr = np.array([current_weights.get(t, 0.0) for t in tickers], dtype=float)

        diagnostics = {
            "num_assets": n,
            "cov_condition_number": float(covariance_condition_number(cov_matrix)),
            "sector_distribution": self._sector_distribution(tickers, sector_mapping),
            "alpha_clip_min": float(alpha_scores.min()),
            "alpha_clip_max": float(alpha_scores.max()),
            "solver_attempts": [],
            "fallback_level": None,
            "constraint_violations": {},
        }

        full_attempt = self._solve_once(
            tickers=tickers,
            alpha_scores=alpha_scores,
            cov_matrix=cov_matrix,
            current_weights=w_curr,
            sector_mapping=sector_mapping,
            risk_aversion=risk_aversion,
            turnover_penalty=turnover_penalty,
            turnover_limit=self.max_turnover * 2,
            sector_cap=self.max_sector_weight,
            relaxed=False,
        )
        diagnostics["solver_attempts"].append(full_attempt["attempt_diag"])
        if full_attempt["weights"] is not None:
            diagnostics["fallback_level"] = "full_optimizer"
            diagnostics["constraint_violations"] = full_attempt["constraint_violations"]
            return full_attempt["weights"], diagnostics

        logger.warning("Optimizer primary solve failed: %s", full_attempt["attempt_diag"])

        relaxed_attempt = self._solve_once(
            tickers=tickers,
            alpha_scores=alpha_scores,
            cov_matrix=cov_matrix,
            current_weights=w_curr,
            sector_mapping=sector_mapping,
            risk_aversion=risk_aversion,
            turnover_penalty=turnover_penalty,
            turnover_limit=max(self.max_turnover * 3, 0.75),
            sector_cap=min(self.max_sector_weight + 0.05, 0.50),
            relaxed=True,
        )
        diagnostics["solver_attempts"].append(relaxed_attempt["attempt_diag"])
        if relaxed_attempt["weights"] is not None:
            diagnostics["fallback_level"] = "relaxed_constraints"
            diagnostics["constraint_violations"] = relaxed_attempt["constraint_violations"]
            return relaxed_attempt["weights"], diagnostics

        logger.warning("Optimizer relaxed solve failed: %s", relaxed_attempt["attempt_diag"])
        fallback_weights = self._fallback_equal_weight(alpha_scores, sector_mapping)
        diagnostics["fallback_level"] = "equal_weight_top_n"
        diagnostics["constraint_violations"] = self._constraint_violations(
            fallback_weights,
            w_curr,
            sector_mapping,
            self.max_sector_weight,
            self.max_turnover * 2,
        )
        return fallback_weights, diagnostics

    def _stabilize_covariance(self, cov_matrix: pd.DataFrame) -> pd.DataFrame:
        cov = cov_matrix.fillna(0.0)
        cov = (cov + cov.T) / 2.0
        if not np.isfinite(covariance_condition_number(cov)):
            cov = clip_covariance_eigenvalues(cov)
        return cov

    def _normalize_alpha_scores(self, alpha_scores: pd.Series) -> pd.Series:
        values = alpha_scores.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        mean = float(values.mean())
        std = float(values.std(ddof=0))
        if std <= 1e-12:
            return values - mean
        z = (values - mean) / std
        return z.clip(-3.0, 3.0)

    def _solve_once(
        self,
        *,
        tickers: list[str],
        alpha_scores: pd.Series,
        cov_matrix: pd.DataFrame,
        current_weights: np.ndarray,
        sector_mapping: Dict[str, str],
        risk_aversion: float,
        turnover_penalty: float,
        turnover_limit: float,
        sector_cap: float,
        relaxed: bool,
    ) -> dict:
        n = len(tickers)
        mu = alpha_scores.values
        sigma = np.asarray(cov_matrix.values, dtype=float)
        sigma = 0.5 * (sigma + sigma.T)

        w = cp.Variable(n)
        cash = cp.Variable(1)
        ret = mu.T @ w
        risk = cp.quad_form(w, cp.psd_wrap(sigma))
        turnover = cp.norm(w - current_weights, 1)
        objective = cp.Maximize(ret - risk_aversion * risk - turnover_penalty * turnover)

        constraints = [
            w >= 0,
            cash >= self.cash_min,
            cash <= self.cash_max,
            cp.sum(w) + cash == 1.0,
            w <= self.max_stock_weight,
            turnover <= turnover_limit,
        ]

        for sector in set(sector_mapping.get(t, "_other") for t in tickers):
            sector_idx = [i for i, t in enumerate(tickers) if sector_mapping.get(t, "_other") == sector]
            if sector_idx:
                constraints.append(cp.sum(w[sector_idx]) <= sector_cap)

        prob = cp.Problem(objective, constraints)
        attempt_diag = {
            "relaxed": relaxed,
            "turnover_limit": float(turnover_limit),
            "sector_cap": float(sector_cap),
            "status": None,
            "exception": None,
        }

        try:
            prob.solve(solver=cp.OSQP, warm_start=True, max_iter=20000)
            attempt_diag["status"] = prob.status
        except Exception as exc:
            attempt_diag["status"] = "exception"
            attempt_diag["exception"] = str(exc)
            logger.warning("Optimizer solve exception (relaxed=%s): %s", relaxed, exc)
            return {"weights": None, "attempt_diag": attempt_diag, "constraint_violations": {}}

        if prob.status not in ["optimal", "optimal_inaccurate"] or w.value is None:
            logger.warning(
                "Optimizer solve status=%s relaxed=%s turnover_limit=%.3f sector_cap=%.3f",
                prob.status,
                relaxed,
                turnover_limit,
                sector_cap,
            )
            return {"weights": None, "attempt_diag": attempt_diag, "constraint_violations": {}}

        weights = pd.Series(np.asarray(w.value).ravel(), index=tickers).clip(lower=0.0)
        weights[weights < 1e-6] = 0.0
        gross = float(weights.sum())
        cash_value = float(np.asarray(cash.value).ravel()[0]) if cash.value is not None else 0.0
        target_gross = min(max(1.0 - cash_value, 0.0), 1.0)
        if gross > 0:
            weights = weights / gross * target_gross
        weights = self._enforce_weight_limits(weights, sector_mapping, sector_cap)
        constraint_violations = self._constraint_violations(
            weights,
            current_weights,
            sector_mapping,
            sector_cap,
            turnover_limit,
        )
        return {
            "weights": weights,
            "attempt_diag": attempt_diag,
            "constraint_violations": constraint_violations,
        }

    def _constraint_violations(
        self,
        weights: pd.Series,
        current_weights: np.ndarray,
        sector_mapping: Dict[str, str],
        sector_cap: float,
        turnover_limit: float,
    ) -> dict:
        turnover = float(np.abs(weights.values - current_weights[: len(weights)]).sum())
        sector_weights: dict[str, float] = {}
        for ticker, weight in weights.items():
            sector = sector_mapping.get(ticker, "_other")
            sector_weights[sector] = sector_weights.get(sector, 0.0) + float(weight)
        max_sector = max(sector_weights.values()) if sector_weights else 0.0
        return {
            "sum_to_one_error": float(abs(1.0 - weights.sum())),
            "min_weight": float(weights.min()) if not weights.empty else 0.0,
            "max_weight_overage": float(max(0.0, weights.max() - self.max_stock_weight)) if not weights.empty else 0.0,
            "turnover_overage": float(max(0.0, turnover - turnover_limit)),
            "sector_cap_overage": float(max(0.0, max_sector - sector_cap)),
        }

    def _sector_distribution(self, tickers: list[str], sector_mapping: Dict[str, str]) -> dict:
        sector_distribution: dict[str, int] = {}
        for ticker in tickers:
            sector = sector_mapping.get(ticker, "_other")
            sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
        return sector_distribution

    def _enforce_weight_limits(
        self,
        weights: pd.Series,
        sector_mapping: Dict[str, str],
        sector_cap: float,
    ) -> pd.Series:
        cleaned = weights.clip(lower=0.0, upper=self.max_stock_weight).copy()
        for sector in {sector_mapping.get(t, "_other") for t in cleaned.index}:
            sector_names = [ticker for ticker in cleaned.index if sector_mapping.get(ticker, "_other") == sector]
            sector_weight = float(cleaned[sector_names].sum())
            if sector_weight > sector_cap and sector_weight > 0:
                cleaned[sector_names] *= sector_cap / sector_weight
        return cleaned

    def _fallback_equal_weight(self, alpha_scores: pd.Series, sector_mapping: Dict[str, str]) -> pd.Series:
        ranked = alpha_scores.sort_values(ascending=False)
        weights = pd.Series(0.0, index=alpha_scores.index, dtype=float)
        sector_weights: dict[str, float] = {}
        remaining = 1.0

        for ticker in ranked.index:
            if remaining <= 1e-8:
                break
            alloc = min(self.max_stock_weight, remaining)
            sector = sector_mapping.get(ticker, "_other")
            sector_used = sector_weights.get(sector, 0.0)
            sector_room = max(0.0, self.max_sector_weight - sector_used)
            alloc = min(alloc, sector_room)
            if alloc <= 1e-8:
                continue
            weights[ticker] = alloc
            sector_weights[sector] = sector_used + alloc
            remaining -= alloc

        return weights
