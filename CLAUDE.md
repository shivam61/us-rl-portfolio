# US RL Portfolio — Claude Code Context

Quantitative US equity portfolio: LightGBM alpha signal → MVO optimizer → heuristic risk engine → walk-forward backtest (2006–2026, NYSE, S&P 500 universe). RL overlay is parked.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-27T00:00:00
**Active job:** diagnostics run (PID 2634, log `/tmp/diag_run.log`)
- Experiment 8/8 (sp100 comparison) in progress
- Run cmd: `python scripts/run_diagnostics.py --config config/base.yaml --universe config/universes/sp500.yaml --compare-universe config/universes/sp100.yaml`

**Last completed milestone:** sp500 universe expansion
- 503 tickers, PIT mask built, features rebuilt (517 tickers, 21 features, 5109 dates)
- Three bugs fixed this session: simulator MtM tautology, targets KeyError on post-IPO stocks, fundamental_features datetime precision mismatch

**Next step (when diagnostics complete):** Read `data/artifacts/reports/universe_expansion_results.md` and decide on alpha improvement track (feature engineering vs model tuning vs RL overlay).
<!-- CURRENT_STATE_END -->

## Stable Baselines (sp500 universe, 2008–2026, DO NOT redefine)
| Experiment | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| Equal Weight Universe | 12.9% | 0.62 | -55% |
| Alpha Top-50 EW | 13.5% | 0.64 | -55% |
| Alpha + Optimizer (no risk) | 11.2% | 0.55 | -55% |
| Full System (opt + risk) | 8.7% | 0.59 | -34% |
| Optimizer sensitivity to=0.5 | 11.9% | 0.68 | -40% |

> Previous sp100 (44-ticker) baselines are in `data/artifacts/diagnostics/20260426_*/ablation_results.csv`. Do not compare cross-universe without the comparison report.

## Key Files
| File | Purpose |
|---|---|
| `config/base.yaml` | All hyperparams (top_n_stocks=50, rebalance=BMS, capital=$1M) |
| `config/universes/sp500.yaml` | 503-ticker universe + PIT mask path |
| `config/universes/sp100.yaml` | 44-ticker baseline universe |
| `src/backtest/walk_forward.py` | Main backtest loop + signal generation |
| `src/backtest/simulator.py` | Execution simulator (cash tracking — was broken, now fixed) |
| `src/features/stock_features.py` | Vectorized feature gen (17 price/vol features) |
| `src/models/stock_ranker.py` | LightGBM regressor wrapper |
| `src/optimizer/portfolio_optimizer.py` | CVXPY MVO with sector/turnover constraints |
| `src/risk/risk_engine.py` | Heuristic risk overlay (VIX + SPY drawdown triggers) |
| `scripts/build_features.py` | Rebuild `data/features/*.parquet` |
| `scripts/build_pit_universe.py` | Rebuild `data/artifacts/universe_mask_sp500.parquet` |
| `scripts/run_diagnostics.py` | Full ablation + alpha quality + comparison report |
| `data/artifacts/reports/` | Output reports (comparison MD + alpha quality JSON) |
| `docs/session_handoff.md` | Deep context: experiment history, design decisions, commands |

## Governance Rules
- **Before any feature change:** run `scripts/run_diagnostics.py` and verify CAGR ≥ 12.9% (EW baseline)
- **Never commit** `data/`, `.venv/`, `__pycache__/`
- **Leakage rule:** all features must be `.shift(1)` before use; targets use forward horizon only
- **PIT rule:** any universe change requires rebuilding `universe_mask_*.parquet` first
- Run `.venv/bin/python` — system Python has no packages

## Parked Tracks
| Track | Status | Why paused |
|---|---|---|
| RL overlay (`src/rl/`) | Parked | Supervised alpha IC too low (0.033); RL can't learn from noisy signals |
| Brinson attribution | Parked | Needs stable alpha first |
| Hyperparameter tuning | Parked | Pending universe expansion results |
| ADV-based slippage model | Parked | Current model sufficient for research phase |

## Context Update
Run at session end:
```bash
bash scripts/save_context.sh
```
