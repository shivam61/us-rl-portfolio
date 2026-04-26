import yaml
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class DataConfig(BaseModel):
    cache_dir: str = "data"
    force_download: bool = False

class BacktestConfig(BaseModel):
    start_date: str = "2013-01-01"
    end_date: Optional[str] = None
    benchmark: str = "SPY"
    rebalance_frequency: str = "4W"
    warmup_years: int = 2
    training_window_years: int = 3

class ExecutionConfig(BaseModel):
    max_participation_rate: float = 0.05
    min_adv_dollar: float = 10000000.0
    allow_partial_fills: bool = True

class PortfolioConfig(BaseModel):
    initial_capital: float = 100000.0
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0
    max_stock_weight: float = 0.05
    max_sector_weight: float = 0.25
    max_turnover: float = 0.30
    cash_min: float = 0.00
    cash_max: float = 0.30

class RLConfig(BaseModel):
    enabled: bool = False
    model_type: str = "ppo"

class BaseConfig(BaseModel):
    project: str = "us-rl-portfolio"
    data: DataConfig
    backtest: BacktestConfig
    execution: ExecutionConfig = ExecutionConfig()
    portfolio: PortfolioConfig
    rl: RLConfig

class UniverseConfig(BaseModel):
    name: str
    description: str
    benchmark: str
    vix_proxy: str
    macro_etfs: List[str]
    sector_etfs: List[str]
    tickers: Dict[str, str]
    is_static: bool = True
    pit_mask_path: Optional[str] = None

def load_config(base_path: str, universe_path: str) -> tuple[BaseConfig, UniverseConfig]:
    with open(base_path, "r") as f:
        base_dict = yaml.safe_load(f)
    with open(universe_path, "r") as f:
        universe_dict = yaml.safe_load(f)
        
    return BaseConfig(**base_dict), UniverseConfig(**universe_dict)
