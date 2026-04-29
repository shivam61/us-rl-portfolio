import pandas as pd
import numpy as np
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FundamentalProvider:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def fetch_fundamentals(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Simulates fetching fundamental data for a list of tickers.
        Output columns include the legacy fields plus simulated balance-sheet,
        cash-flow, and margin fields used to validate feature plumbing.
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        logger.info(f"Simulating fundamental data for {len(tickers)} tickers from {start_date} to {end_date}")
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # We assume earnings are filed quarterly.
        # Let's generate end of quarter dates, then add a random delay of 10-30 days to get the filing date.
        quarters = pd.date_range(start=start, end=end, freq='QE') # 'QE' for Quarter End
        
        all_data = []
        
        for ticker in tickers:
            # Base values for simulation (positive eps to make PE positive initially)
            base_eps = self.rng.uniform(1.0, 10.0)
            base_shares = self.rng.uniform(1e7, 1e9)
            base_bv = base_eps * base_shares * self.rng.uniform(1.0, 5.0)
            base_revenue = base_eps * base_shares * self.rng.uniform(8.0, 25.0)
            base_assets = base_bv * self.rng.uniform(1.5, 4.0)
            base_debt = base_assets * self.rng.uniform(0.05, 0.55)
            
            # Start slightly before the first quarter to have some baseline growth data
            for q_end in quarters:
                # Delay for filing date (simulating it happens after the quarter ends)
                delay_days = self.rng.integers(10, 45)
                filing_date = q_end + pd.Timedelta(days=delay_days)
                
                if filing_date > end:
                    break
                    
                # Add some random walk to values
                eps = base_eps * (1 + self.rng.normal(0, 0.1))
                shares = base_shares * (1 + self.rng.normal(0, 0.01))
                book_value = base_bv * (1 + self.rng.normal(0, 0.05))
                net_income = eps * shares
                revenue = base_revenue * (1 + self.rng.normal(0.01, 0.08))
                total_assets = max(book_value * 1.05, base_assets * (1 + self.rng.normal(0.005, 0.04)))
                total_debt = max(0.0, min(total_assets * 0.95, base_debt * (1 + self.rng.normal(0.0, 0.08))))
                interest_expense = max(abs(total_debt) * self.rng.uniform(0.005, 0.025), 1.0)
                operating_income = net_income + interest_expense * self.rng.uniform(1.5, 4.0)
                operating_cash_flow = net_income * self.rng.uniform(0.7, 1.3)
                gross_profit = revenue * self.rng.uniform(0.15, 0.65)
                
                # Update base values for next quarter
                base_eps = eps
                base_shares = shares
                base_bv = book_value
                base_revenue = revenue
                base_assets = total_assets
                base_debt = total_debt
                
                all_data.append({
                    "filing_date": filing_date,
                    "ticker": ticker,
                    "eps": eps,
                    "book_value": book_value,
                    "net_income": net_income,
                    "shares_outstanding": shares,
                    "revenue": revenue,
                    "gross_profit": gross_profit,
                    "total_assets": total_assets,
                    "total_debt": total_debt,
                    "operating_income": operating_income,
                    "interest_expense": interest_expense,
                    "operating_cash_flow": operating_cash_flow,
                })
                
        df = pd.DataFrame(all_data)
        if not df.empty:
            df = df.sort_values(["ticker", "filing_date"]).reset_index(drop=True)
            
        return df
