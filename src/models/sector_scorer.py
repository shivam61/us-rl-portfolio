import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge


class SectorScorer:
    def __init__(self, use_lgbm: bool = True, **kwargs):
        self.use_lgbm = use_lgbm and LGBM_AVAILABLE
        n_jobs = int(os.environ.get("LGBM_N_JOBS", "2"))
        if self.use_lgbm:
            self.model = lgb.LGBMRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=n_jobs, **kwargs)
        else:
            self.model = HistGradientBoostingRegressor(max_iter=100, max_depth=5, random_state=42)
            
    def fit(self, X: pd.DataFrame, y: pd.Series):
        # Drop NaNs
        mask = ~X.isna().any(axis=1) & ~y.isna()
        if mask.sum() < 50: # Arbitrary minimum sample size
            # Fallback to Ridge if not enough data
            self.model = Ridge()
            
        self.model.fit(X[mask], y[mask])
        return self
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        X_clean = X.fillna(X.mean())
        # Replace remaining NaNs with 0 (if mean is NaN)
        X_clean = X_clean.fillna(0)
        preds = self.model.predict(X_clean)
        return pd.Series(preds, index=X.index)
