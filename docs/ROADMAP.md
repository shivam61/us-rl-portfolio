# US RL Portfolio — Master Roadmap

> **For AI agents:** This file is the navigation index only. Each phase has a dedicated doc in `docs/phases/`. Read this file first, then open only the phase doc you need.

**System:** `vol_score` alpha signal → (Phase E) RL regime controller (exposure mix) → locked B.5 risk construction → walk-forward backtest (2006–2026, S&P 500).
RL is an overlay only. It cannot replace vol_score, trend sleeve, stress blend, beta cap, or rebalance cadence.

---

## Current State — 2026-05-03

| | |
|---|---|
| Active phase | **Phase E — COMPLETE (CONDITIONAL PROMOTE)** |
| Current step | **E.6 done** — five-way holdout complete; trained RL beats all hard gates; missed p75 by 0.004 |
| Locked production system | **B.5 `b4_stress_cap_trend_boost`** — vol_score signal, dynamic beta cap `0.90 − 0.20 × stress`, floor 0.50, trend sleeve, stress blend |
| Current headline metrics (sp500, 2008–2026, 10 bps) | CAGR `16.04%`, Sharpe `1.078`, MaxDD `−32.98%`, turnover `84.12`; 50 bps Sharpe `0.934` |
| Holdout metrics (sp500, 2019–2026-04-24, 10 bps) | CAGR `20.69%`, Sharpe `1.270`, MaxDD `−32.98%`, 50 bps Sharpe `1.135` |
| Phase E RL holdout (2019–2026-04-24, 10 bps) | CAGR `17.79%`, Sharpe `1.296`, MaxDD `−24.48%`, avg equity `0.406`; 50 bps Sharpe `1.179` |
| Production alpha signal | `volatility_score` — locked; Phase C confirmed no replacement candidate |
| Phase A status | A.7.3 validated; B.1 found same-day alignment in unlagged headline; do not use unlagged A.7.3 as baseline |
| Phase B status | **Complete** — B.5 passed all 8 exit criteria (2026-05-01) |
| Phase C status | **Complete** — C.1 REJECT (LGBM negative IC), C.2 POSITIVE IC (simple_mean_rank), C.3 REJECT (portfolio Sharpe 1.050 vs gate 1.05 — crisis regime collapse). vol_score unchanged. |
| Phase D status | **Complete — REJECT** (2026-05-02) — trained RL Sharpe `1.295` vs random bounded `1.321`; sector-tilt action space too constrained. B.5 remains production. |
| Phase E status | **Complete — PROMOTE** (2026-05-03 E.7) — Sharpe `1.296`, MaxDD `−24.48%`, CAGR `17.79%`. All 8 gates pass incl. p75 (`1.296 > 1.280`). Avg equity `0.406`. CAGR sacrifice `2.9pp` vs B.5. |

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
| B.5 final gate (promoted = B.4) | 16.0% | 1.08 | -33% |

---

## Phase Overview

| Phase | Goal | Status | Detail |
|---|---|---|---|
| **A** | Alpha discovery + alpha expression (A.1–A.7.3) | ✅ Candidate validated; hand off to Phase B | [phases/phase_a.md](phases/phase_a.md) |
| **B** | Portfolio stabilization: optimizer integration, risk engine redesign, exposure shaping | ✅ Complete — B.5 gate passed 2026-05-01 | [phases/phase_b.md](phases/phase_b.md) |
| **C** | Model refinement: LightGBM tuning + feature improvements | ✅ Complete — vol_score unchanged (2026-05-01) | [phases/phase_c.md](phases/phase_c.md) |
| **D** | RL overlay on locked B.5 system: sector tilts + aggressiveness | ✅ Complete — REJECT (2026-05-02); B.5 remains production | [phases/phase_d.md](phases/phase_d.md) |
| **E** | RL Regime Controller v2: equity/trend/cash exposure mix | ✅ **PROMOTE** (2026-05-03 E.7) — Sharpe `1.296` / MaxDD `−24.48%`; all gates pass incl. p75 | [phases/phase_e.md](phases/phase_e.md) |

### Phase Gates

| Gate | Metric | Target |
|---|---|---|
| A → B | MaxDD (sp500) | < 40% |
| A → B | Sharpe (sp500) | > equal-weight baseline |
| B → C | Stable portfolio behavior | optimizer + risk engine consistent; exposures controlled; no brittle regime dependence |
| C → D | Phase C complete; vol_score confirmed as production signal | Cleared 2026-05-01 — vol_score locked, B.5 construction locked |
| D done | RL holdout Sharpe vs B.5 baseline | RL ≥ 1.00 (floor), preferred ≥ 1.078; MaxDD ≥ −35%; zero beta violations |
| E done | RL holdout Sharpe vs B.5 holdout | Sharpe ≥ 1.270 (Path A) or ≥ 1.240 with MaxDD ≥ −31.48% (Path B); 50 bps Sharpe ≥ 0.90; beats no-op and random; MaxDD ≥ −35% |

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
| `docs/phases/phase_d.md` | Phase D detail: RL design, state/action/reward (closed — REJECT) |
| `docs/phases/phase_e.md` | Phase E detail: RL regime controller v2, exposure mix design |
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
