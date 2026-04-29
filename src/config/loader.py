import yaml
from pathlib import Path
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class DataConfig(BaseModel):
    cache_dir: str = "data"
    force_download: bool = False

class FundamentalsConfig(BaseModel):
    provider: str = "simulated"
    path: Optional[str] = None
    min_ticker_coverage: float = 0.80
    require_pit_dates: bool = True

class BacktestConfig(BaseModel):
    start_date: str = "2013-01-01"
    end_date: Optional[str] = None
    benchmark: str = "SPY"
    rebalance_frequency: str = "4W"
    warmup_years: int = 2
    training_window_years: int = 3
    retrain_frequency: int = 3

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
    top_n_stocks: int = 50

class AlphaConfig(BaseModel):
    default_score: str = "volatility_score"

class IntraperiodRiskConfig(BaseModel):
    enabled: bool = False
    benchmark_return_window: int = 5
    benchmark_return_trigger: float = -0.06
    vix_change_window: int = 3
    vix_change_trigger: float = 0.40
    exposure_multiplier: float = 0.60
    use_hysteresis: bool = False
    exit_benchmark_return_trigger: float = -0.02
    exit_vix_change_trigger: float = 0.15
    min_hold_days: int = 0
    cooldown_days: int = 0
    restore_exposure_multipliers: List[float] = Field(default_factory=lambda: [1.0])

class RLConfig(BaseModel):
    enabled: bool = False
    model_type: str = "ppo"

class ResearchConfig(BaseModel):
    research_universe: str = "config/universes/sp100.yaml"
    diagnostic_universe: str = "config/universes/sp500.yaml"

class BaseConfig(BaseModel):
    project: str = "us-rl-portfolio"
    data: DataConfig
    fundamentals: FundamentalsConfig = FundamentalsConfig()
    backtest: BacktestConfig
    execution: ExecutionConfig = ExecutionConfig()
    portfolio: PortfolioConfig
    alpha: AlphaConfig = AlphaConfig()
    intraperiod_risk: IntraperiodRiskConfig = IntraperiodRiskConfig()
    rl: RLConfig
    research: ResearchConfig = ResearchConfig()

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
