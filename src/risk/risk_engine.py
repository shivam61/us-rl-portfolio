import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RiskEngine:
    def __init__(self, 
                 max_stock_weight: float = 0.05,
                 max_sector_weight: float = 0.25,
                 vix_threshold: float = 0.90,
                 crash_drawdown: float = -0.15):
        self.max_stock_weight = max_stock_weight
        self.max_sector_weight = max_sector_weight
        self.vix_threshold = vix_threshold
        self.crash_drawdown = crash_drawdown
        
    def apply_risk_controls(self, 
                            weights: pd.Series, 
                            macro_features: pd.Series,
                            sector_mapping: Dict[str, str]) -> pd.Series:
        """
        Heuristic risk engine applied post-optimization.
        """
        w = weights.copy()
        cash = 1.0 - w.sum()
        
        # 1. Market crash protection
        vix_pct = macro_features.get("vix_percentile_1y", 0.0)
        spy_dd = macro_features.get("spy_drawdown", 0.0)
        
        if vix_pct > self.vix_threshold or spy_dd < self.crash_drawdown:
            logger.info("Risk Engine: High risk regime detected. Raising cash.")
            # Reduce all equity positions by 50%
            w = w * 0.5
            cash = 1.0 - w.sum()
            
        # 2. Hard caps (just in case optimizer failed or drifted)
        w = w.clip(lower=0.0, upper=self.max_stock_weight)
        
        # Sector caps
        sectors = set(sector_mapping.values())
        for sector in sectors:
            sector_tickers = [t for t in w.index if sector_mapping.get(t) == sector]
            if not sector_tickers:
                continue
                
            sector_weight = w[sector_tickers].sum()
            if sector_weight > self.max_sector_weight:
                logger.info(f"Risk Engine: Trimming sector {sector} from {sector_weight:.2f} to {self.max_sector_weight:.2f}")
                scale = self.max_sector_weight / sector_weight
                w[sector_tickers] *= scale
                
        # Final normalization to ensure we don't exceed 1.0
        total_w = w.sum()
        if total_w > 1.0:
            w = w / total_w
            
        return w
