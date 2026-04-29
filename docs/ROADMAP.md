# US RL Portfolio — Master Roadmap

> **For AI agents:** This file is the navigation index only. Each phase has a dedicated doc in `docs/phases/`. Read this file first, then open only the phase doc you need.

**System:** LightGBM alpha signal → MVO optimizer → (Phase D) RL sector overlay → heuristic risk engine → walk-forward backtest (2006–2026, S&P 500).

---

## Current State — 2026-04-29

| | |
|---|---|
| Active phase | **Phase A** — alpha discovery + alpha expression |
| Current step | **A.7.2** — robustness (costs, leverage caps, periods, regimes) |
| Best system so far | volatility + trend blend (A.7.1 candidate) |
| Current headline metrics (sp500) | CAGR ~24%, Sharpe ~1.0+, MaxDD ~30–40% |
| Current production alpha candidate | `volatility_score` as component only, not standalone sleeve |
| Phase A status | Candidate investable non-RL expression found: `vol_top_20` + stress-scaled trend overlay passed sp500 drawdown/Sharpe gates; validating robustness in A.7.2 |
| Blocking gate | Do not proceed to Phase B until A.7.2 confirms MaxDD < 40% and Sharpe beats equal-weight under realistic costs/constraints |
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
| **A** | Alpha discovery + alpha expression (A.1–A.7.2) | 🔄 In progress (A.7.2) | [phases/phase_a.md](phases/phase_a.md) |
| **B** | Portfolio stabilization: optimizer integration, risk engine redesign, exposure shaping | ⏳ Pending Phase A gate | [phases/phase_b.md](phases/phase_b.md) |
| **C** | Model refinement (deferred): LightGBM tuning + feature improvements | ⏳ Deferred until Phase B stabilizes | [phases/phase_c.md](phases/phase_c.md) |
| **D** | RL overlay (stricter gate): sector RL policy | ⏳ Pending Phase C gate | [phases/phase_d.md](phases/phase_d.md) |

### Phase Gates

| Gate | Metric | Target |
|---|---|---|
| A → B | MaxDD (sp500) | < 40% |
| A → B | Sharpe (sp500) | > equal-weight baseline |
| B → C | Stable portfolio behavior | optimizer + risk engine consistent; exposures controlled; no brittle regime dependence |
| C → D | Stable signals + stable portfolio | signals and portfolio behavior remain stable under robustness checks |
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
| `docs/DATA_AND_FEATURE_ENGINEERING.md` | Data/feature cache conventions, coverage audits, and extension guide |
| `docs/phases/phase_d.md` | Phase D detail: RL design, state/action/reward |
| `docs/agent_handoff.md` | Experiment history, legacy session notes, useful commands |

---

## Governance

- **Research baseline on sp100, validate on sp500** — sp100 (44 tickers) is 10× faster
- **Leakage rule:** all features `.shift(1)`; targets use forward horizon only
- **PIT rule:** universe change → rebuild `universe_mask_*.parquet` first
- **Baseline rule:** never redefine sp500 baselines without a full diagnostics run
- **Long-horizon rule:** preserve 2006+ raw data and remember metrics start after warmup; future RL splits must remain chronological
- **Docs-current rule:** after material implementation, experiment results, baseline decisions, or next-step changes, update the relevant phase doc plus `docs/agent_handoff.md`, then refresh shared session state
- **Never commit** `data/`, `.venv/`, `__pycache__/`
- **Python:** always use `.venv/bin/python`
