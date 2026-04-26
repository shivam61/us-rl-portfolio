import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

class ExecutionSimulator:
    def __init__(self, config: Any):
        self.initial_capital = config.portfolio.initial_capital
        self.tc = config.portfolio.transaction_cost_bps / 10000.0
        self.slippage = config.portfolio.slippage_bps / 10000.0
        
        self.max_participation_rate = config.execution.max_participation_rate
        self.min_adv_dollar = config.execution.min_adv_dollar
        self.allow_partial_fills = config.execution.allow_partial_fills
        
        self.nav = self.initial_capital
        self.holdings = pd.Series(dtype=float)
        self.history = []
        self.trades_history = []
        
    def rebalance(self, 
                  target_weights: pd.Series, 
                  execution_date: pd.Timestamp, 
                  prices_open: pd.Series, 
                  prices_close: pd.Series,
                  daily_volume: pd.Series,
                  adv: pd.Series):
        """
        Execute trades to reach target_weights on the execution_date.
        Uses open prices by default, falls back to close prices.
        Applies volume constraints based on daily_volume and ADV.
        """
        # Clean target weights
        target_weights = target_weights[target_weights > 0]
        
        # Determine execution prices
        exec_prices = prices_open.copy()
        # Fallback to close if open is missing/nan
        missing_open = exec_prices.isna() | (exec_prices <= 0)
        exec_prices[missing_open] = prices_close[missing_open]
        
        # Calculate current weights based on current prices
        current_weights = pd.Series(0.0, index=target_weights.index.union(self.holdings.index))
        current_value = 0.0
        
        if not self.holdings.empty:
            for t, shares in self.holdings.items():
                price = exec_prices.get(t, prices_close.get(t, np.nan))
                if not np.isnan(price) and price > 0:
                    current_value += shares * price
                    
            if current_value > 0:
                for t, shares in self.holdings.items():
                    price = exec_prices.get(t, prices_close.get(t, np.nan))
                    if not np.isnan(price) and price > 0:
                        current_weights[t] = (shares * price) / self.nav
                        
        # Identify required trades (in terms of weight)
        target_weights = target_weights.reindex(current_weights.index).fillna(0.0)
        weight_trades = target_weights - current_weights
        
        executed_trades = {}
        total_trade_cost_usd = 0.0
        
        # Filter for liquidity
        liquid_tickers = []
        for t in weight_trades.index:
            if adv.get(t, 0) >= self.min_adv_dollar:
                liquid_tickers.append(t)
            elif abs(weight_trades[t]) > 1e-4:
                logger.warning(f"{execution_date}: {t} skipped due to low ADV (${adv.get(t, 0):.0f})")
                
        # Simulate execution
        new_holdings_dict = {}
        total_turnover_weight = 0.0
        
        # For tracking slippage & TC drag specifically
        tc_drag_usd = 0.0
        slippage_drag_usd = 0.0

        for t in current_weights.index:
            w_diff = weight_trades.get(t, 0.0)
            price = exec_prices.get(t, np.nan)
            
            if np.isnan(price) or price <= 0:
                # Can't trade, keep current holdings
                if t in self.holdings:
                    new_holdings_dict[t] = self.holdings[t]
                continue
                
            if abs(w_diff) < 1e-6:
                # No trade needed
                if t in self.holdings:
                    new_holdings_dict[t] = self.holdings[t]
                continue
                
            if t not in liquid_tickers:
                # Low liquidity, hold existing
                if t in self.holdings:
                    new_holdings_dict[t] = self.holdings[t]
                continue

            # Calculate desired trade in shares
            dollars_to_trade = w_diff * self.nav
            shares_to_trade = dollars_to_trade / price
            
            # Constraints
            vol = daily_volume.get(t, adv.get(t, 0)) # fallback to ADV if today's volume is missing
            max_shares_allowed = vol * self.max_participation_rate
            
            if abs(shares_to_trade) > max_shares_allowed:
                if self.allow_partial_fills:
                    old_shares = shares_to_trade
                    shares_to_trade = np.sign(shares_to_trade) * max_shares_allowed
                    logger.debug(f"{execution_date}: Partial fill for {t}. Req: {old_shares:.0f}, Fill: {shares_to_trade:.0f}")
                else:
                    shares_to_trade = 0.0
                    logger.debug(f"{execution_date}: Skipped trade for {t} due to max participation.")
                    
            # Update holdings
            current_shares = self.holdings.get(t, 0.0)
            final_shares = current_shares + shares_to_trade
            if final_shares > 1e-6:
                new_holdings_dict[t] = final_shares
                
            # Log Trade
            if abs(shares_to_trade) > 0:
                executed_trades[t] = shares_to_trade
                trade_value_usd = abs(shares_to_trade * price)
                
                tc_usd = trade_value_usd * self.tc
                sl_usd = trade_value_usd * self.slippage
                
                total_trade_cost_usd += (tc_usd + sl_usd)
                tc_drag_usd += tc_usd
                slippage_drag_usd += sl_usd
                total_turnover_weight += trade_value_usd / self.nav
                
                self.trades_history.append({
                    "date": execution_date,
                    "ticker": t,
                    "shares": shares_to_trade,
                    "price": price,
                    "cost_usd": tc_usd + sl_usd
                })
        
        # Update NAV
        self.nav -= total_trade_cost_usd
        self.holdings = pd.Series(new_holdings_dict, dtype=float)
        
        self.history.append({
            "date": execution_date,
            "nav": self.nav,
            "turnover": total_turnover_weight / 2.0, # One-way turnover
            "cost": total_trade_cost_usd,
            "tc_drag": tc_drag_usd,
            "slippage_drag": slippage_drag_usd,
            "cash_exposure": self._calculate_cash_exposure(exec_prices)
        })
        
    def mark_to_market(self, date: pd.Timestamp, prices: pd.Series):
        if self.holdings.empty:
            self.history.append({
                "date": date, "nav": self.nav, "turnover": 0.0, 
                "cost": 0.0, "tc_drag": 0.0, "slippage_drag": 0.0, "cash_exposure": 1.0
            })
            return
            
        port_value = 0.0
        for t, shares in self.holdings.items():
            if t in prices and not np.isnan(prices[t]):
                port_value += shares * prices[t]
                
        # Assume cash yields 0 for simplicity
        invested_weight = sum([shares * prices.get(t, 0) for t, shares in self.holdings.items() if t in prices]) / self.nav if self.nav > 0 else 0
        cash = self.nav * (1.0 - min(1.0, invested_weight))
        
        self.nav = port_value + cash
        
        self.history.append({
            "date": date, 
            "nav": self.nav, 
            "turnover": 0.0, 
            "cost": 0.0,
            "tc_drag": 0.0,
            "slippage_drag": 0.0,
            "cash_exposure": max(0.0, 1.0 - invested_weight)
        })
        
    def _calculate_cash_exposure(self, prices: pd.Series) -> float:
        if self.holdings.empty or self.nav <= 0:
            return 1.0
        invested = sum([shares * prices.get(t, 0) for t, shares in self.holdings.items() if t in prices])
        return max(0.0, 1.0 - (invested / self.nav))

    def get_history(self) -> pd.DataFrame:
        df = pd.DataFrame(self.history)
        if df.empty:
            return df
        df.set_index("date", inplace=True)
        # Drop duplicate dates, keeping last (rebalance overwrites MTM)
        df = df[~df.index.duplicated(keep='last')]
        return df

    def get_trades(self) -> pd.DataFrame:
        return pd.DataFrame(self.trades_history)
