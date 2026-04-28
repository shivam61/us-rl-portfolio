import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


def _as_covariance_frame(values: np.ndarray, columns: pd.Index) -> pd.DataFrame:
    return pd.DataFrame(values, index=columns, columns=columns)


def clip_covariance_eigenvalues(cov_matrix: pd.DataFrame, min_eigenvalue: float = 1e-6) -> pd.DataFrame:
    values = cov_matrix.fillna(0.0).values
    values = (values + values.T) / 2.0
    eigvals, eigvecs = np.linalg.eigh(values)
    clipped = np.clip(eigvals, min_eigenvalue, None)
    repaired = eigvecs @ np.diag(clipped) @ eigvecs.T
    repaired = (repaired + repaired.T) / 2.0
    return _as_covariance_frame(repaired, cov_matrix.columns)


def diagonal_covariance(returns: pd.DataFrame, ridge: float = 1e-6) -> pd.DataFrame:
    ret_clean = returns.fillna(0.0)
    variances = ret_clean.var().fillna(0.0).clip(lower=0.0)
    diagonal = np.diag(variances.values + ridge)
    return _as_covariance_frame(diagonal, returns.columns)


def covariance_condition_number(cov_matrix: pd.DataFrame) -> float:
    values = cov_matrix.fillna(0.0).values
    values = (values + values.T) / 2.0
    try:
        eigvals = np.linalg.eigvalsh(values)
    except np.linalg.LinAlgError:
        return float("inf")
    max_eig = float(np.max(np.abs(eigvals))) if eigvals.size else 0.0
    min_eig = float(np.min(np.abs(eigvals))) if eigvals.size else 0.0
    if min_eig <= 0.0:
        return float("inf")
    return max_eig / min_eig


def estimate_covariance(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Estimates covariance matrix using Ledoit-Wolf shrinkage.
    If Ledoit-Wolf fails, falls back to diagonal covariance and finally
    repairs the matrix with eigenvalue clipping if needed.
    """
    ret_clean = returns.fillna(0.0)
    columns = returns.columns

    try:
        lw = LedoitWolf()
        cov = _as_covariance_frame(lw.fit(ret_clean).covariance_, columns)
    except Exception:
        cov = diagonal_covariance(ret_clean)
        if not np.isfinite(covariance_condition_number(cov)):
            cov = clip_covariance_eigenvalues(cov)
        return cov

    cov = cov.fillna(0.0)
    cov = (cov + cov.T) / 2.0
    if not np.isfinite(covariance_condition_number(cov)):
        cov = clip_covariance_eigenvalues(cov)
    return cov
