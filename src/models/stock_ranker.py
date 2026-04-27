import pandas as pd
from typing import Dict, Any, Optional

try:
    import lightgbm as lgb
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

class StockRanker:
    """
    Ranks stocks within a cross-section using regression as a proxy for ranking
    or LGBMRanker if available and configured.
    """
    def __init__(self, use_lgbm_ranker: bool = False, **kwargs):
        self.use_lgbm_ranker = use_lgbm_ranker and LGBM_AVAILABLE
        if self.use_lgbm_ranker:
            self.model = lgb.LGBMRanker(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1, **kwargs)
        elif LGBM_AVAILABLE:
            self.model = lgb.LGBMRegressor(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1, **kwargs)
        else:
            self.model = HistGradientBoostingRegressor(max_iter=50, max_depth=5, random_state=42)
            
    def fit(self, X: pd.DataFrame, y: pd.Series, group: Optional[pd.Series] = None):
        mask = ~X.isna().any(axis=1) & ~y.isna()
        if mask.sum() < 50:
            self.model = Ridge()
            
        X_train = X[mask]
        y_train = y[mask]
        
        if self.use_lgbm_ranker and group is not None:
            group_train = group[mask]
            # LGBMRanker needs group counts
            group_counts = group_train.value_counts().sort_index()
            # Must sort X_train and y_train by group
            sorted_idx = group_train.argsort()
            X_train = X_train.iloc[sorted_idx]
            y_train = y_train.iloc[sorted_idx]
            group_counts = group_train.iloc[sorted_idx].value_counts(sort=False)
            
            self.model.fit(X_train, y_train, group=group_counts.values)
        else:
            self.model.fit(X_train, y_train)
        return self
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        X_clean = X.fillna(X.mean()).fillna(0)
        preds = self.model.predict(X_clean)
        return pd.Series(preds, index=X.index)
