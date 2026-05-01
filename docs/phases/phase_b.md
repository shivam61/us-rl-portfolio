# Phase B — Portfolio Stabilization

> **Navigation:** [← Phase A](phase_a.md) | [← ROADMAP](../ROADMAP.md) | Next: [Phase C →](phase_c.md)

**Objective:** turn the A.7.3 stress-scaled volatility/trend expression into a stable portfolio construction path with explicit data-window guards, turnover controls, execution realism, and optimizer/risk integration.

**Entry research candidate:** Phase A locked candidate:
`vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.

**Phase A matrix headline on `sp500_dynamic`:**
- CAGR `23.51%`
- Sharpe `1.538`
- MaxDD `-26.36%`
- max gross `1.375`
- min candidate count `128`
- min selected count `20`

**Production baseline after B.1 on `sp500_dynamic` clipped to `2026-04-24`:**
- CAGR `17.56%`
- Sharpe `1.116`
- MaxDD `-26.98%`
- max gross `1.375`
- min selected count `21`
- equal-weight simulator Sharpe `0.619`

Do not use the unlagged Phase A matrix headline as a Phase B promotion baseline. B.1 found same-day signal/return alignment in the unlagged A.7.3 matrix path; the production baseline is the open/next-day simulator result, reconciled to a one-day-lagged matrix reference.

**Important scope:** do not modify `volatility_score`, add a new alpha, import historical index membership, or enable RL in Phase B.

---

## Phase B Goals

| Goal | Target |
|---|---|
| Preserve Phase A drawdown profile | sp500 MaxDD stays `<40%` |
| Preserve risk-adjusted return | sp500 Sharpe stays above equal-weight baseline and preferably `>1.0` under production-style simulation |
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

- **B.1 drift tolerance:** production-style runner must keep Sharpe within `10-15%` of the lagged A.7.3 matrix reference, MaxDD `<40%`, max gross `<=1.5`, and explain any CAGR/Sharpe drift from simulator costs, execution timing, cash handling, or rebalance-date differences.
- **B.1 failure condition:** if reproduction falls outside tolerance, do not proceed to B.2. Identify and reconcile differences in signal alignment, timing, cost model, and cash handling; then update baseline or simulator assumptions before continuing.
- **B.1 baseline reset:** the unlagged A.7.3 matrix headline is retained only as research history. Phase B promotion comparisons should use `phase_b1_production_open_next_day` from `artifacts/reports/phase_b1_runner_detail.csv`.
- **Portfolio beta:** primary control is rebalance-date ex-ante beta using latest available `beta_to_spy_63d`; report rolling realized beta separately.
- **Execution realism:** use configured liquidity constraints as first defaults: `max_participation_rate=5%`, ADV/min-liquidity checks, max single-name weight, turnover controls, and minimum trade thresholds where implemented.
- **Turnover:** measured as sum of absolute weight changes per rebalance period; report both average and peak turnover across the backtest.
- **Gross exposure rejection:** any configuration exceeding max gross `1.5` is rejected unless explicitly tagged as exploratory and excluded from Phase B promotion.
- **Risk engine integration:** start from the A.7.1/A.7.2 stress signal; do not add independent VIX/SPY brakes unless attribution proves incremental benefit.
- **Optimizer role:** shape exposure, beta, sector concentration, liquidity, and turnover; do not use it as return maximization over noisy alpha estimates.

---

## Phase B.2 — Turnover Control / Rebalance Hysteresis

**Goal:** reduce turnover/cost drag without materially changing the B.1 return profile.

### Implementation

| Item | File | Status |
|---|---|---|
| B.2 turnover frontier runner | `scripts/run_phase_b2_turnover_control.py` | Implemented |
| Main report | `artifacts/reports/phase_b2_turnover_control.md` | Done |
| Turnover frontier | `artifacts/reports/turnover_frontier.csv` | Done |
| Cost sensitivity | `artifacts/reports/cost_sensitivity.csv` | Done |
| Trade threshold slice | `artifacts/reports/trade_threshold_results.csv` | Done |
| Persistence slice | `artifacts/reports/persistence_results.csv` | Done |

### B.2 Result

B.2 used a fast one-day-lagged target-weight approximation to select turnover controls, anchored to the B.1 production simulator baseline. It did not modify `volatility_score`, the trend signal, stress-scaling logic, or RL settings.

Best promoted B.2 control is `every_2_rebalances`:

- CAGR `18.33%`
- Sharpe `1.144`
- MaxDD `-33.69%`
- turnover sum `89.62`
- turnover reduction `61.2%`
- 50 bps Sharpe `0.999` versus same-cost baseline `0.765`
- max gross `1.346`

Other passing but less aggressive controls:

- 50 bps minimum trade threshold: Sharpe `1.166`, MaxDD `-31.57%`, turnover reduction `25.0%`.
- 50 bps threshold + top-40 persistence: Sharpe `1.147`, MaxDD `-33.78%`, turnover reduction `34.7%`.
- 50% partial rebalance: Sharpe `1.176`, MaxDD `-28.43%`, turnover reduction `25.0%`.

Rejected/fragile observations:

- 4-week/monthly cadence reduced turnover `73.3%` but failed the B.2 drawdown gate with MaxDD `-36.65%`.
- 100 bps trade threshold reduced turnover `31.8%` but failed MaxDD/gross gates.
- Partial-rebalance plus threshold/persistence combinations can accumulate stale residual positions and exceed max gross; those rows are rejected and excluded from promotion.

### B.2 Decision

PASS. Carry `every_2_rebalances` as the primary B.2 turnover-control candidate into B.3 exposure-constrained portfolio shaping. Keep threshold-only and partial-rebalance rows as secondary references, not the main promoted setting, unless B.3 beta/exposure shaping shows the every-2 cadence is too drawdown-sensitive.

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

- A.7.x unlagged matrix headline used same-day target weights against same-day returns; B.1 reconciled this by introducing a one-day-lagged matrix reference and resetting the Phase B baseline to the production simulator row.
- The production baseline has lower Sharpe/CAGR than the Phase A headline but preserves the drawdown/gross profile and beats equal-weight on the same clipped universe.
- sp500 PIT mask has three trailing zero-active dates in late April 2026; this is a data-window artifact to clean or clip.
- Regime Sharpe remains weak in 2008 and 2022 even though regime MaxDD passes.
- B.2 every-2-rebalances reduces turnover materially but moves MaxDD to `-33.69%`; B.3 should focus on beta/exposure shaping without chasing return.
- Results validated on configured ticker universe with PIT liquidity mask, not true historical index membership.
- Historical index-membership data remains intentionally deferred; do not import it unless current-setup artifact checks become fragile.

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-04-30 | B.0 baseline guard | Done | A.7.3 baseline locked; sp500 recommended validation end is `2026-04-24` unless PIT mask is refreshed |
| 2026-04-30 | B.1 simulator reproduction | Reconciled | Production open/next-day sp500 baseline: CAGR `17.56%`, Sharpe `1.116`, MaxDD `-26.98%`; within tolerance versus lagged matrix reference, not versus unlagged A.7.3 headline |
| 2026-05-01 | B.2 turnover control | Passed | Primary candidate `every_2_rebalances`: CAGR `18.33%`, Sharpe `1.144`, MaxDD `-33.69%`, turnover reduction `61.2%`; 50 bps Sharpe `0.999` versus same-cost baseline `0.765` |
