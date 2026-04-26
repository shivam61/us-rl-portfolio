import pandas as pd
import numpy as np

def calculate_metrics(nav_series: pd.Series, periods_per_year: int = 252) -> dict:
    if nav_series.empty:
        return {}
        
    rets = nav_series.pct_change().dropna()
    total_ret = nav_series.iloc[-1] / nav_series.iloc[0] - 1.0
    
    years = len(rets) / periods_per_year
    cagr = (1 + total_ret) ** (1 / years) - 1.0 if years > 0 else 0.0
    
    vol = rets.std() * np.sqrt(periods_per_year)
    sharpe = cagr / vol if vol > 0 else 0.0
    
    downside_rets = rets[rets < 0]
    downside_vol = downside_rets.std() * np.sqrt(periods_per_year)
    sortino = cagr / downside_vol if downside_vol > 0 else 0.0
    
    rolling_max = nav_series.expanding().max()
    drawdowns = (nav_series / rolling_max) - 1.0
    max_dd = drawdowns.min()
    
    calmar = cagr / abs(max_dd) if abs(max_dd) > 0 else 0.0
    
    return {
        "Total Return": float(total_ret),
        "CAGR": float(cagr),
        "Volatility": float(vol),
        "Sharpe": float(sharpe),
        "Sortino": float(sortino),
        "Max Drawdown": float(max_dd),
        "Calmar": float(calmar)
    }

def calculate_annual_returns(nav_series: pd.Series) -> dict:
    rets = nav_series.resample("YE").last().pct_change().dropna()
    return {str(k.year): float(v) for k, v in rets.items()}

def calculate_monthly_returns(nav_series: pd.Series) -> pd.DataFrame:
    rets = nav_series.resample("ME").last().pct_change().dropna()
    df = pd.DataFrame(rets)
    df["Year"] = df.index.year
    df["Month"] = df.index.month
    pivot = df.pivot(index="Year", columns="Month", values="nav")
    return pivot
