# US RL Portfolio — Master Roadmap

> **For AI agents:** This file is the navigation index only. Each phase has a dedicated doc in `docs/phases/`. Read this file first, then open only the phase doc you need.

**System:** LightGBM alpha signal → MVO optimizer → (Phase D) RL sector overlay → heuristic risk engine → walk-forward backtest (2006–2026, S&P 500).

---

## Current State — 2026-04-29

| | |
|---|---|
| Active phase | **A.4** — beta-targeted defensive sleeve improved correlation but failed sp500 gate; data-layer upgrade next |
| Current production alpha candidate | `volatility_score` as component only, not standalone sleeve |
| Best IC so far | sp100 mean period IC 0.0379; sp500 mean period IC 0.0259; rebalance IC ~0.034 on sp500 |
| Best IC Sharpe | ~0.13 in Phase A.1 portfolio diagnostics — original 0.30 gate still not met |
| Phase A status | Conditionally passed for alpha discovery only: high-vol/risk-premium alpha is real, but standalone and defensive-blend expressions failed |
| Blocking gate | Do not continue optimizer/RL; add true point-in-time survivability fundamentals before more sleeve-blend tuning |
| sp500 baselines | Locked validation/system baseline — see table below, do not redefine |

## Baseline Convention

- **sp100 (44 tickers)** = research baseline / dev universe / fast iteration track
- **sp500 (503 tickers)** = validation baseline / system benchmark / locked comparison track
- If a note says only "baseline", resolve whether it refers to research (`sp100`) or validation (`sp500`) before comparing metrics

### Stable Baselines (sp500 validation baseline, 2008–2026)

| Experiment | CAGR | Sharpe | MaxDD |
|---|---|---|---|
| Equal Weight Universe | 12.9% | 0.62 | -55% |
| Alpha Top-50 EW | 13.5% | 0.64 | -55% |
| Alpha + Optimizer (no risk) | 11.2% | 0.55 | -55% |
| Full System (opt + risk) | 8.7% | 0.59 | -34% |
| Optimizer to=0.5 sensitivity | 11.9% | 0.68 | -40% |

---

## Phase Overview

| Phase | Goal | Status | Detail |
|---|---|---|---|
| **A** | Lift IC: new feature families + IC eval | 🔄 In progress | [phases/phase_a.md](phases/phase_a.md) |
| **B** | Experiment matrix: label × top-N × retrain × features | ⏳ Pending Phase A gate | [phases/phase_b.md](phases/phase_b.md) |
| **C** | LightGBM hyperparameter search | ⏳ Pending Phase B gate | [phases/phase_c.md](phases/phase_c.md) |
| **D** | RL sector rotation overlay | ⏳ Pending Phase C gate | [phases/phase_d.md](phases/phase_d.md) |

### Phase Gates

| Gate | Metric | Target |
|---|---|---|
| A → B | Mean Rank IC | ≥ 0.040 |
| A → B | IC Sharpe | ≥ 0.30 |
| B → C | Best experiment config identified | top-N, label, retrain freq |
| C → D | IC Sharpe on 2019–2026 holdout | ≥ 0.50 |
| D done | RL Sharpe vs heuristic on holdout | RL ≥ 0.70 |

---

## Key Files

| File | What's in it |
|---|---|
| `config/base.yaml` | All hyperparams |
| `config/universes/sp500.yaml` | 503-ticker universe + PIT mask path |
| `config/universes/sp100.yaml` | 44-ticker research universe (use for dev) |
| `src/features/stock_features.py` | 30 vectorized features |
| `src/labels/targets.py` | 3 target labels |
| `src/backtest/walk_forward.py` | Main backtest loop |
| `src/rl/environment.py` | RL env skeleton (Phase D) |
| `docs/phases/phase_a.md` | Phase A detail: features, IC results, decisions |
| `docs/phases/phase_d.md` | Phase D detail: RL design, state/action/reward |
| `docs/agent_handoff.md` | Experiment history, legacy session notes, useful commands |

---

## Governance

- **Research baseline on sp100, validate on sp500** — sp100 (44 tickers) is 10× faster
- **Leakage rule:** all features `.shift(1)`; targets use forward horizon only
- **PIT rule:** universe change → rebuild `universe_mask_*.parquet` first
- **Baseline rule:** never redefine sp500 baselines without a full diagnostics run
- **Docs-current rule:** after material implementation, experiment results, baseline decisions, or next-step changes, update the relevant phase doc plus `docs/agent_handoff.md`, then refresh shared session state
- **Never commit** `data/`, `.venv/`, `__pycache__/`
- **Python:** always use `.venv/bin/python`
