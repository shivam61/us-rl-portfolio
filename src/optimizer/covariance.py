import pandas as pd
from sklearn.covariance import LedoitWolf

def estimate_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Estimates covariance matrix using Ledoit-Wolf shrinkage.
    Expects a DataFrame of returns where rows are dates and columns are tickers.
    """
    # Fill missing returns with 0
    ret_clean = returns.fillna(0.0)
    
    try:
        lw = LedoitWolf()
        cov = lw.fit(ret_clean).covariance_
        return pd.DataFrame(cov, index=returns.columns, columns=returns.columns)
    except Exception:
        # Fallback to sample covariance
        cov = ret_clean.cov()
        # Ensure positive semi-definite and handle nans
        cov = cov.fillna(0.0)
        # Add small ridge
        cov.values[[range(len(cov))]*2] += 1e-6
        return cov
