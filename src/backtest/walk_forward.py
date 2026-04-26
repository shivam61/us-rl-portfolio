import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

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
                 prices_dict: Dict[str, pd.DataFrame]):
        self.config = config
        self.universe_config = universe_config
        self.stock_features = stock_features
        self.macro_features = macro_features
        self.targets = targets
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
        
    def generate_rebalance_dates(self) -> List[pd.Timestamp]:
        start = pd.Timestamp(self.config.backtest.start_date)
        start = start + pd.DateOffset(years=self.config.backtest.warmup_years)
        
        end = pd.Timestamp(self.config.backtest.end_date) if self.config.backtest.end_date else self.prices_close.index[-1]
        
        dates = pd.date_range(start=start, end=end, freq=self.config.backtest.rebalance_frequency)
        return list(dates)

    def run(self):
        rebalance_dates = self.generate_rebalance_dates()
        trading_dates = self.prices_close.index.tolist()
        
        if not rebalance_dates:
            logger.error("No rebalance dates generated.")
            return pd.DataFrame(), pd.DataFrame()
            
        first_execution_date = get_next_trading_day(rebalance_dates[0], trading_dates)
        mtm_dates = [d for d in trading_dates if d >= first_execution_date]
        
        reb_idx = 0
        current_weights = pd.Series(dtype=float)
        
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
                    target_weights = self._generate_target_weights(signal_date, current_weights)
                    
                    exec_open = self.prices_open.loc[date]
                    exec_close = self.prices_close.loc[date]
                    daily_vol = self.volume.loc[date]
                    
                    # Safe ADV lookup using last valid observation
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
                    continue
                
            # Mark to market using adj_close for true performance
            mtm_prices = self.prices_adj_close.loc[date]
            self.simulator.mark_to_market(date, mtm_prices)
                
        return self.simulator.get_history(), self.simulator.get_trades()
        
    def _get_latest_available(self, df_or_series, date: pd.Timestamp):
        idx = df_or_series.index.get_indexer([date], method='ffill')[0]
        if idx >= 0:
            return df_or_series.iloc[idx]
        return pd.Series(dtype=float) if isinstance(df_or_series, pd.DataFrame) else 0.0
        
    def _generate_target_weights(self, signal_date: pd.Timestamp, current_weights: pd.Series) -> pd.Series:
        train_start = signal_date - pd.DateOffset(years=self.config.backtest.training_window_years)
        
        # Strict leakage guard
        cutoff_date = signal_date - pd.DateOffset(days=25) 
        
        try:
            mask = (self.stock_features.index.get_level_values('date') >= train_start) & \
                   (self.stock_features.index.get_level_values('date') <= cutoff_date)
            
            X_train = self.stock_features[mask]
            y_train = self.targets.loc[X_train.index, "target_fwd_ret"]
            
            ranker = StockRanker()
            ranker.fit(X_train, y_train)
            
            # Predict (need to find closest trading day for inference features)
            idx = self.stock_features.index.levels[0].get_indexer([signal_date], method='ffill')[0]
            if idx < 0:
                raise ValueError("No features available before signal date")
            latest_feature_date = self.stock_features.index.levels[0][idx]
            
            X_infer = self.stock_features.xs(latest_feature_date, level="date")
            tradable_tickers = list(self.universe_config.tickers.keys())
            X_infer = X_infer.reindex(tradable_tickers).dropna(how='all')
            alpha_scores = ranker.predict(X_infer)
            
        except Exception as e:
            logger.warning(f"Model training failed at {signal_date}: {e}. Using equal weight.")
            tickers = list(self.universe_config.tickers.keys())
            alpha_scores = pd.Series(1.0, index=tickers)
            
        # Covariance estimation using adj_close
        cov_start = signal_date - pd.DateOffset(years=1)
        cov_mask = (self.prices_adj_close.index >= cov_start) & (self.prices_adj_close.index <= signal_date)
        recent_returns = self.prices_adj_close[cov_mask].pct_change().dropna(how='all')
        cov_matrix = estimate_covariance(recent_returns)
        
        raw_weights = self.optimizer.optimize(
            alpha_scores=alpha_scores,
            cov_matrix=cov_matrix,
            current_weights=current_weights,
            sector_mapping=self.universe_config.tickers
        )
        
        macro_state = self._get_latest_available(self.macro_features, signal_date)
            
        final_weights = self.risk_engine.apply_risk_controls(
            weights=raw_weights,
            macro_features=macro_state,
            sector_mapping=self.universe_config.tickers
        )
        
        return final_weights
