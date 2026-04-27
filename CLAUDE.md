# US RL Portfolio — Claude Code Context

Quantitative US equity portfolio: LightGBM alpha signal → MVO optimizer → heuristic risk engine → walk-forward backtest (2006–2026, NYSE, S&P 500 universe). RL overlay is parked.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-27T18:36:56
**Active job:** diagnostics complete — see data/artifacts/reports/universe_expansion_results.md
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

## Documentation

> **AI agents: start here, then open only the doc you need.**

| Doc | When to read it |
|---|---|
| `docs/ROADMAP.md` | Current phase, gates, stable baselines, governance — read first every session |
| `docs/phases/phase_a.md` | Feature engineering detail, IC eval results, iteration log |
| `docs/phases/phase_b.md` | Experiment matrix design, grid dimensions, pending Phase A gate |
| `docs/phases/phase_c.md` | LightGBM hyperparam search, pending Phase B gate |
| `docs/phases/phase_d.md` | RL sector overlay full design: state/action/reward, integration steps |
| `docs/session_handoff.md` | Experiment history, bug fixes, useful shell commands |

## Key Source Files
| File | Purpose |
|---|---|
| `config/base.yaml` | All hyperparams |
| `config/universes/sp500.yaml` | 503-ticker universe + PIT mask path |
| `config/universes/sp100.yaml` | 44-ticker research universe (use for dev) |
| `src/features/stock_features.py` | 30 vectorized features (17 baseline + 13 new) |
| `src/labels/targets.py` | 3 target labels |
| `src/backtest/walk_forward.py` | Main backtest loop + signal generation |
| `src/risk/risk_engine.py` | Heuristic risk overlay (replaced by RL in Phase D) |
| `src/rl/environment.py` | RL env skeleton — Phase D |

## Governance Rules
- **Before any feature change:** run `scripts/run_diagnostics.py` and verify CAGR ≥ 12.9% (EW baseline)
- **Never commit** `data/`, `.venv/`, `__pycache__/`
- **Leakage rule:** all features must be `.shift(1)` before use; targets use forward horizon only
- **PIT rule:** any universe change requires rebuilding `universe_mask_*.parquet` first
- **Research on sp100, validate on sp500**
- Run `.venv/bin/python` — system Python has no packages

## Context Update
Run at session end:
```bash
bash scripts/save_context.sh
```
