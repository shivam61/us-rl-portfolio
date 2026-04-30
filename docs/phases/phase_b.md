# Phase B — Portfolio Stabilization

> **Navigation:** [← Phase A](phase_a.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase C →](phase_c.md)

**Objective:** turn the A.7.3 stress-scaled volatility/trend expression into a stable portfolio construction path with explicit data-window guards, turnover controls, execution realism, and optimizer/risk integration.

**Entry baseline:** Phase A locked candidate:
`vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.

**Entry metrics on `sp500_dynamic`:**
- CAGR `23.51%`
- Sharpe `1.538`
- MaxDD `-26.36%`
- max gross `1.375`
- min candidate count `128`
- min selected count `20`

**Important scope:** do not modify `volatility_score`, add a new alpha, import historical index membership, or enable RL in Phase B.

---

## Phase B Goals

| Goal | Target |
|---|---|
| Preserve Phase A drawdown profile | sp500 MaxDD stays `<40%` |
| Preserve risk-adjusted return | sp500 Sharpe stays above equal-weight baseline and preferably `>1.0` |
| Control exposure | max gross `<=1.5` unless explicitly testing rejected variants |
| Control market exposure | portfolio beta remains within defined band, e.g. `0.5-0.8` |
| Control turnover/cost | turnover controlled via rebalance frequency, trade thresholds, and persistence; 25-50 bps Sharpe remains competitive |
| Ensure execution realism | turnover and position sizing remain feasible under realistic liquidity assumptions |
| Improve implementation realism | actual simulator/optimizer path matches A.7.3 path closely enough to explain differences |
| Keep attribution clear | each change isolated as data-window, turnover, optimizer, or risk-engine effect |

---

## Phase B Non-Negotiable Gates

| Gate | Target |
|---|---|
| sp500 MaxDD | `<40%` |
| sp500 Sharpe | `>1.0` preferred, must beat equal-weight baseline on the same universe and cost assumptions |
| max gross | `<=1.5` |
| portfolio beta | initially `0.5-0.8` |
| 50 bps cost-adjusted Sharpe | still competitive versus baseline |
| min selected names | `20` |
| alpha changes | none; `volatility_score` unchanged |
| RL | disabled |

---

## Phase B.0 — Baseline Guard

**Goal:** lock the Phase A baseline and cleanly define the usable validation window before changing portfolio construction.

### Implementation

| Item | File | Status |
|---|---|---|
| B.0 baseline/data-window guard | `scripts/run_phase_b0_baseline_guard.py` | Implemented |
| Main report | `artifacts/reports/phase_b0_baseline_guard.md` | Done |
| Data-window audit | `artifacts/reports/phase_b0_data_window_guard.csv` | Done |
| Baseline lock | `artifacts/reports/phase_b0_baseline_lock.csv` | Done |

### B.0 Result

Use A.7.3 as the Phase A baseline for Phase B comparisons. Before production-style validation, clip `sp500_dynamic` to `2026-04-24` or rebuild the PIT mask around the trailing zero-active dates observed from `2026-04-27` to `2026-04-29`.

---

## Planned Work

| Step | Purpose | Output |
|---|---|---|
| B.0 | Lock A.7.3 baseline and define valid data window | baseline guard report |
| B.1 | Reproduce A.7.3 candidate in the main simulator with identical signal construction, sleeve weights, stress-scaling logic, rebalance timing, and cost assumptions | simulator-compatible baseline |
| B.2 | Turnover smoothing / rebalance hysteresis | turnover-cost frontier |
| B.3 | Exposure-constrained portfolio shaping (not return maximization) | optimizer attribution report |
| B.4 | Risk engine formalization and integration (stress-based) | risk attribution report |
| B.5 | Final Phase B gate run on sp500 | promoted portfolio construction |

---

## Measurement Definitions

- **B.1 drift tolerance:** production-style runner must keep Sharpe within `10-15%` of the A.7.3 baseline, MaxDD `<40%`, max gross `<=1.5`, and explain any CAGR/Sharpe drift from simulator costs, execution timing, cash handling, or rebalance-date differences.
- **B.1 failure condition:** if reproduction falls outside tolerance, do not proceed to B.2. Identify and reconcile differences in signal alignment, timing, cost model, and cash handling; then update baseline or simulator assumptions before continuing.
- **Portfolio beta:** primary control is rebalance-date ex-ante beta using latest available `beta_to_spy_63d`; report rolling realized beta separately.
- **Execution realism:** use configured liquidity constraints as first defaults: `max_participation_rate=5%`, ADV/min-liquidity checks, max single-name weight, turnover controls, and minimum trade thresholds where implemented.
- **Turnover:** measured as sum of absolute weight changes per rebalance period; report both average and peak turnover across the backtest.
- **Gross exposure rejection:** any configuration exceeding max gross `1.5` is rejected unless explicitly tagged as exploratory and excluded from Phase B promotion.
- **Risk engine integration:** start from the A.7.1/A.7.2 stress signal; do not add independent VIX/SPY brakes unless attribution proves incremental benefit.
- **Optimizer role:** shape exposure, beta, sector concentration, liquidity, and turnover; do not use it as return maximization over noisy alpha estimates.

---

## Phase B Exit Criteria

Proceed to Phase C only if:

- sp500 MaxDD remains `<40%` under production-style simulation.
- Cost-adjusted Sharpe remains `>0.9-1.0`.
- Portfolio beta remains within the defined band.
- Turnover is stable and explainable.
- Differences versus A.7.3 baseline are understood and attributable.

---

## Current Open Risks

- Current A.7.x blend runner is return/weight-matrix based, not the main simulator path.
- A.7.x candidate currently blends sleeve returns/weights daily; production implementation may change rebalance timing and cost realization.
- sp500 PIT mask has three trailing zero-active dates in late April 2026; this is a data-window artifact to clean or clip.
- Regime Sharpe remains weak in 2008 and 2022 even though regime MaxDD passes.
- Results validated on configured ticker universe with PIT liquidity mask, not true historical index membership.
- Historical index-membership data remains intentionally deferred; do not import it unless current-setup artifact checks become fragile.

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-04-30 | B.0 baseline guard | Done | A.7.3 baseline locked; sp500 recommended validation end is `2026-04-24` unless PIT mask is refreshed |
