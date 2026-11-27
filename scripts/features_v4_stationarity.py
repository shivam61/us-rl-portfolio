"""M7 stationarity check for the v4.1 daily table (FH). Augmented Dickey-Fuller regression with one lag and a
constant, implemented in numpy (statsmodels is not installed in this environment). Reports the ADF t-statistic,
the 5% MacKinnon asymptotic critical value (-2.86 with a constant), a flag, and the drift of the 252-day rolling
mean (range of the rolling mean divided by the full-sample sd). Output: runs_fh/features_v4_1/stationarity.csv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rl import features_risk_v4 as L  # noqa: E402

CV5 = -2.86  # MacKinnon (1994) asymptotic 5% critical value, ADF with constant, no trend


def adf_t(x: np.ndarray) -> float:
    """ADF(1) with constant: dx_t = a + g*x_{t-1} + b*dx_{t-1} + e. Returns the t-statistic of g."""
    dx = np.diff(x)
    y = dx[1:]
    X = np.column_stack([np.ones(len(y)), x[1:-1], dx[:-1]])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = resid @ resid / (len(y) - X.shape[1])
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(beta[1] / np.sqrt(cov[1, 1]))


def main():
    P = pd.read_parquet(ROOT / "runs_fh" / "features_v4_1" / "daily_v4.parquet")
    rows = []
    for c in L.FEATURE_NAMES:
        s = P[c].dropna()
        t = adf_t(s.values.astype(float))
        rm = s.rolling(252, min_periods=252).mean().dropna()
        drift = float((rm.max() - rm.min()) / s.std()) if len(rm) else np.nan
        rows.append(dict(feature=c, n=len(s), adf_t=round(t, 3), stationary_5pct=bool(t < CV5),
                         rolling_mean_range_over_sd=round(drift, 3)))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "runs_fh" / "features_v4_1" / "stationarity.csv", index=False)
    print(out.to_string(index=False))
    print("non-stationary (ADF fails to reject unit root):", out.loc[~out.stationary_5pct, "feature"].tolist())


if __name__ == "__main__":
    main()
