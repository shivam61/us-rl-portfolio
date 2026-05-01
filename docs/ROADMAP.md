# US RL Portfolio — Master Roadmap

> **For AI agents:** This file is the navigation index only. Each phase has a dedicated doc in `docs/phases/`. Read this file first, then open only the phase doc you need.

**System:** LightGBM alpha signal → MVO optimizer → (Phase D) RL sector overlay → heuristic risk engine → walk-forward backtest (2006–2026, S&P 500).

---

## Current State — 2026-05-01

| | |
|---|---|
| Active phase | **Phase B** — portfolio stabilization |
| Current step | **B.5** — final Phase B gate run, starting from B.4 promoted candidate |
| Best system so far | **B.4 candidate:** `b4_stress_cap_trend_boost` — dynamic beta cap `0.90 − 0.20 × stress`, floor 0.50, small high-stress trend boost |
| Current headline metrics (sp500) | B.4 candidate CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`, turnover `84.12`, max gross `1.500`; B.1 production simulator anchor remains `17.6% / 1.12 / -27.0%` |
| Current production alpha candidate | `volatility_score` as component only, not standalone sleeve |
| Phase A status | A.7.3 current-setup membership/coverage artifact validation did not show strategy fragility, but B.1 found same-day signal/return alignment in the unlagged matrix headline; do not use it as a promotion baseline |
| Blocking gate | Production validation must clip `sp500_dynamic` to `2026-04-24` or refresh PIT mask before using trailing dates; B.4 must preserve B.3.1 turnover/exposure gates and avoid daily beta-chasing |
| sp500 baselines | Locked validation/system baseline plus B.1 production baseline — do not redefine without full diagnostics |

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
| B.1 production stress blend | 17.6% | 1.12 | -27% |
| B.2 every-2-rebalances frontier | 18.3% | 1.14 | -34% |
| B.3 hard beta-band projection | 15.5% | 1.07 | -31% |
| B.3.1 soft beta-band projection | 16.5% | 1.08 | -34% |
| B.4 stress-aware beta cap + trend | 16.0% | 1.08 | -33% |

---

## Phase Overview

| Phase | Goal | Status | Detail |
|---|---|---|---|
| **A** | Alpha discovery + alpha expression (A.1–A.7.3) | ✅ Candidate validated; hand off to Phase B | [phases/phase_a.md](phases/phase_a.md) |
| **B** | Portfolio stabilization: optimizer integration, risk engine redesign, exposure shaping | 🔄 In progress | [phases/phase_b.md](phases/phase_b.md) |
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
