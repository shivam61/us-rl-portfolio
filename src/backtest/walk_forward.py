import time
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional

from src.models.stock_ranker import StockRanker
from src.optimizer.portfolio_optimizer import PortfolioOptimizer
from src.optimizer.covariance import estimate_covariance
from src.risk.risk_engine import RiskEngine
from src.backtest.simulator import ExecutionSimulator
from src.data.calendar import get_next_trading_day

logger = logging.getLogger(__name__)

class WalkForwardEngine:
    def __init__(self, 
                 config: Any, 
                 universe_config: Any,
                 stock_features: pd.DataFrame, 
                 macro_features: pd.DataFrame, 
                 targets: pd.DataFrame,
                 prices_dict: Dict[str, pd.DataFrame],
                 pit_mask: Optional[pd.DataFrame] = None):
        self.config = config
        self.universe_config = universe_config
        self.stock_features = stock_features
        self.macro_features = macro_features
        self.targets = targets
        self.pit_mask = pit_mask
        self.prices_open = prices_dict["open"].ffill()
        self.prices_close = prices_dict["close"].ffill()
        self.prices_adj_close = prices_dict["adj_close"].ffill()
        self.volume = prices_dict["volume"].fillna(0)
        
        # Pre-compute ADV (63 days)
        self.adv = (self.prices_close * self.volume).rolling(63, min_periods=1).mean().ffill()
        
        self.simulator = ExecutionSimulator(config=config)
        
        self.optimizer = PortfolioOptimizer(
            max_stock_weight=config.portfolio.max_stock_weight,
            max_sector_weight=config.portfolio.max_sector_weight,
            max_turnover=config.portfolio.max_turnover,
            cash_min=config.portfolio.cash_min,
            cash_max=config.portfolio.cash_max
        )
        
        self.risk_engine = RiskEngine(
            max_stock_weight=config.portfolio.max_stock_weight,
            max_sector_weight=config.portfolio.max_sector_weight
        )

        self._cached_ranker: Optional[StockRanker] = None
        self._retrain_counter: int = 0
        
    def generate_rebalance_dates(self) -> List[pd.Timestamp]:
        start = pd.Timestamp(self.config.backtest.start_date)
        start = start + pd.DateOffset(years=self.config.backtest.warmup_years)
        
        end = pd.Timestamp(self.config.backtest.end_date) if self.config.backtest.end_date else self.prices_close.index[-1]
        
        dates = pd.date_range(start=start, end=end, freq=self.config.backtest.rebalance_frequency)
        return list(dates)

    def run(self, 
            use_optimizer: bool = True, 
            use_risk_engine: bool = True,
            top_n_equal_weight: Optional[int] = None):
        """
        Run the walk-forward backtest loop with optional component overrides.
        """
        rebalance_dates = self.generate_rebalance_dates()
        trading_dates = self.prices_close.index.tolist()
        
        if not rebalance_dates:
            logger.error("No rebalance dates generated.")
            return pd.DataFrame(), pd.DataFrame(), {}
            
        first_execution_date = get_next_trading_day(rebalance_dates[0], trading_dates)
        mtm_dates = [d for d in trading_dates if d >= first_execution_date]
        
        reb_idx = 0
        current_weights = pd.Series(dtype=float)
        
        # Diagnostics
        diagnostics = {
            "risk_interventions": [],
            "alpha_quality": [],
            "optimizer_stats": [],
            "exposure": [],
            "train_stats": [],
        }
        
        logger.info(f"Starting walk-forward backtest from {first_execution_date.date()}")
        
        for date in mtm_dates:
            if reb_idx < len(rebalance_dates):
                try:
                    next_exec_date = get_next_trading_day(rebalance_dates[reb_idx], trading_dates)
                except ValueError:
                    break
                    
                if date == next_exec_date:
                    signal_date = rebalance_dates[reb_idx]
                    
                    logger.info(f"Rebalancing: Signal Date {signal_date.date()}, Execution Date {date.date()}")
                    
                    # Generate signal and track quality
                    target_weights, step_diag = self._generate_target_weights(
                        signal_date, 
                        current_weights,
                        use_optimizer=use_optimizer,
                        use_risk_engine=use_risk_engine,
                        top_n_equal_weight=top_n_equal_weight
                    )
                    
                    # Track diagnostics
                    if "alpha_quality" in step_diag:
                        diagnostics["alpha_quality"].append(step_diag["alpha_quality"])
                    if "optimizer_stats" in step_diag:
                        diagnostics["optimizer_stats"].append(step_diag["optimizer_stats"])
                    if "train_stats" in step_diag:
                        diagnostics["train_stats"].append(step_diag["train_stats"])
                    if "risk_interventions" in step_diag:
                        for inter in step_diag["risk_interventions"]:
                            inter["date"] = str(signal_date.date())
                            diagnostics["risk_interventions"].append(inter)
                    
                    exec_open = self.prices_open.loc[date]
                    exec_close = self.prices_close.loc[date]
                    daily_vol = self.volume.loc[date]
                    curr_adv = self._get_latest_available(self.adv, signal_date)
                    
                    self.simulator.rebalance(
                        target_weights=target_weights, 
                        execution_date=date, 
                        prices_open=exec_open,
                        prices_close=exec_close,
                        daily_volume=daily_vol,
                        adv=curr_adv
                    )
                    current_weights = target_weights
                    reb_idx += 1
                    
                    # Exposure tracking
                    w = target_weights[target_weights > 0.001]
                    hhi   = float((w ** 2).sum()) if not w.empty else 1.0
                    eff_n = float(1.0 / hhi)      if hhi > 0    else float(len(w))
                    diagnostics["exposure"].append({
                        "date":           str(date.date()),
                        "gross_exposure": float(target_weights.sum()),
                        "cash_pct":       float(1.0 - target_weights.sum()),
                        "num_holdings":   int((target_weights > 0.001).sum()),
                        "hhi":            hhi,
                        "effective_n":    eff_n,
                    })
                    continue
                
            # Mark to market
            mtm_prices = self.prices_adj_close.loc[date]
            self.simulator.mark_to_market(date, mtm_prices)
                
        return self.simulator.get_history(), self.simulator.get_trades(), diagnostics
        
    def _get_latest_available(self, df_or_series, date: pd.Timestamp):
        idx = df_or_series.index.get_indexer([date], method='ffill')[0]
        if idx >= 0:
            return df_or_series.iloc[idx]
        return pd.Series(dtype=float) if isinstance(df_or_series, pd.DataFrame) else 0.0
        
    def _get_active_tickers(self, date: pd.Timestamp) -> List[str]:
        base_tickers = list(self.universe_config.tickers.keys())
        if self.pit_mask is None:
            return base_tickers
            
        try:
            # find the closest date in pit_mask
            idx = self.pit_mask.index.get_indexer([date], method='ffill')[0]
            if idx >= 0:
                mask_date = self.pit_mask.index[idx]
                active_series = self.pit_mask.loc[mask_date]
                active_tickers = active_series[active_series].index.tolist()
                return [t for t in base_tickers if t in active_tickers]
            return base_tickers
        except Exception as e:
            logger.warning(f"Failed to get active tickers from pit_mask for {date}: {e}")
            return base_tickers

    def _select_sector_capped_top_n(
        self,
        alpha_scores: pd.Series,
        top_n: int,
        sector_mapping: dict,
        max_sector_weight: float
    ) -> list:
        """Greedy top-N selection with per-sector cap enforced during selection."""
        per_stock_weight = 1.0 / top_n
        max_per_sector = max(1, int(max_sector_weight / per_stock_weight))

        ranked = alpha_scores.dropna().sort_values(ascending=False)
        selected: list = []
        sector_counts: dict = {}

        for ticker in ranked.index:
            if len(selected) >= top_n:
                break
            sector = sector_mapping.get(ticker, "_other")
            if sector_counts.get(sector, 0) < max_per_sector:
                selected.append(ticker)
                sector_counts[sector] = sector_counts.get(sector, 0) + 1

        return selected

    def _generate_target_weights(self,
                                 signal_date: pd.Timestamp, 
                                 current_weights: pd.Series,
                                 use_optimizer: bool = True,
                                 use_risk_engine: bool = True,
                                 top_n_equal_weight: Optional[int] = None) -> tuple[pd.Series, dict]:
        step_diag = {}
        
        active_tickers = self._get_active_tickers(signal_date)
        if not active_tickers:
            return pd.Series(dtype=float), step_diag

        train_start = signal_date - pd.DateOffset(years=self.config.backtest.training_window_years)
        cutoff_date = signal_date - pd.DateOffset(days=25)

        alpha_scores = pd.Series(0.0, index=active_tickers)

        try:
            # Fast date-range slice on sorted (date, ticker) MultiIndex
            X_train = self.stock_features.loc[pd.IndexSlice[train_start:cutoff_date, :], :]
            X_train = X_train.loc[X_train.index.get_level_values('ticker').isin(active_tickers)]
            # Use reindex to avoid KeyError on (date, ticker) pairs absent from targets
            y_train = self.targets.reindex(X_train.index)["target_fwd_ret"]
            
            retrain_freq = getattr(self.config.backtest, 'retrain_frequency', 1)
            should_retrain = (self._cached_ranker is None) or (self._retrain_counter % retrain_freq == 0)
            self._retrain_counter += 1

            t0 = time.perf_counter()
            if should_retrain:
                ranker = StockRanker()
                ranker.fit(X_train, y_train)
                self._cached_ranker = ranker
            else:
                ranker = self._cached_ranker
            train_secs = time.perf_counter() - t0 if should_retrain else 0.0
            step_diag["train_stats"] = {"trained": should_retrain, "train_seconds": train_secs}
            
            idx = self.stock_features.index.levels[0].get_indexer([signal_date], method='ffill')[0]
            if idx < 0:
                raise ValueError("No features available before signal date")
            latest_feature_date = self.stock_features.index.levels[0][idx]
            
            X_infer = self.stock_features.xs(latest_feature_date, level="date")
            X_infer = X_infer.reindex(active_tickers).dropna(how='all')
            
            if not X_infer.empty:
                alpha_scores = ranker.predict(X_infer)
                
                # Alpha Quality Metrics — isolated try so failures never affect weights
                try:
                    actual_fwd_rets = self.targets.xs(latest_feature_date, level="date")["target_fwd_ret"]
                    common = alpha_scores.index.intersection(actual_fwd_rets.dropna().index)
                    if len(common) > 10:
                        rank_ic = alpha_scores.loc[common].rank().corr(actual_fwd_rets.loc[common].rank())

                        # Top vs Bottom Decile
                        labels = pd.qcut(alpha_scores.loc[common], 10, labels=False, duplicates='drop')
                        top_decile = actual_fwd_rets.loc[common][labels == labels.max()].mean()
                        bot_decile = actual_fwd_rets.loc[common][labels == labels.min()].mean()

                        # Precision@N
                        def _precision_at(n):
                            if len(common) < n:
                                return float("nan")
                            pred_top = set(alpha_scores.loc[common].nlargest(n).index)
                            act_top  = set(actual_fwd_rets.loc[common].nlargest(n).index)
                            return len(pred_top & act_top) / n

                        # Per-sector IC
                        sec_map = {t: s for t, s in self.universe_config.tickers.items() if t in common}
                        sector_groups: dict = {}
                        for t in common:
                            sector_groups.setdefault(sec_map.get(t, "Unknown"), []).append(t)
                        sector_ic = {
                            sec: float(alpha_scores.loc[ts].rank().corr(actual_fwd_rets.loc[ts].rank()))
                            for sec, ts in sector_groups.items() if len(ts) >= 5
                        }

                        step_diag["alpha_quality"] = {
                            "date":           str(signal_date.date()),
                            "rank_ic":        float(rank_ic),
                            "top_decile_ret": float(top_decile),
                            "bot_decile_ret": float(bot_decile),
                            "spread":         float(top_decile - bot_decile),
                            "precision_20":   _precision_at(20),
                            "precision_50":   _precision_at(50),
                            "sector_ic":      sector_ic,
                        }
                except Exception as diag_e:
                    logger.debug(f"Alpha quality metrics failed at {signal_date}: {diag_e}")
            
        except Exception as e:
            logger.warning(f"Model training failed at {signal_date}: {e}. Using equal weight.")
            alpha_scores = pd.Series(1.0, index=active_tickers)
            
        # Decision Logic
        if top_n_equal_weight:
            active_sector_mapping = {t: s for t, s in self.universe_config.tickers.items() if t in active_tickers}
            selected = self._select_sector_capped_top_n(
                alpha_scores, top_n_equal_weight,
                active_sector_mapping, self.config.portfolio.max_sector_weight
            )
            raw_weights = pd.Series(0.0, index=alpha_scores.index)
            if selected:
                raw_weights[selected] = 1.0 / len(selected)
        elif use_optimizer:
            cov_start = signal_date - pd.DateOffset(years=1)
            cov_mask = (self.prices_adj_close.index >= cov_start) & (self.prices_adj_close.index <= signal_date)
            recent_returns = self.prices_adj_close[cov_mask].pct_change().dropna(how='all')
            
            # Align with active tickers
            available_returns = recent_returns.columns.intersection(active_tickers)
            recent_returns = recent_returns[available_returns].fillna(0)
            cov_matrix = estimate_covariance(recent_returns)
            
            # Filter alpha_scores for what we have returns for
            valid_alphas = alpha_scores.index.intersection(available_returns)
            alpha_scores_filtered = alpha_scores[valid_alphas]
            
            active_sector_mapping = {t: s for t, s in self.universe_config.tickers.items() if t in active_tickers}

            raw_weights = self.optimizer.optimize(
                alpha_scores=alpha_scores_filtered,
                cov_matrix=cov_matrix,
                current_weights=current_weights,
                sector_mapping=active_sector_mapping
            )
            step_diag["optimizer_stats"] = {
                "date": str(signal_date.date()),
                "num_assets": len(active_tickers),
                "gross_raw": float(raw_weights.sum())
            }
        else:
            # Simple equal weight of all active
            raw_weights = pd.Series(1.0 / len(active_tickers), index=active_tickers)
            
        if use_risk_engine:
            active_sector_mapping = {t: s for t, s in self.universe_config.tickers.items() if t in active_tickers}
            macro_state = self._get_latest_available(self.macro_features, signal_date)
            final_weights, interventions = self.risk_engine.apply_risk_controls(
                weights=raw_weights,
                macro_features=macro_state,
                sector_mapping=active_sector_mapping
            )
            step_diag["risk_interventions"] = interventions
        else:
            final_weights = raw_weights
            
        return final_weights, step_diag
