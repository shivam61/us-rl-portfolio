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

## Phase B.3 — Exposure-Constrained Portfolio Shaping

**Goal:** enforce gross `<=1.5` and rebalance-date beta band `0.5-0.8` without modifying alpha, trend, stress scaling, or B.2 turnover control.

### Implementation

| Item | File | Status |
|---|---|---|
| B.3 exposure-control runner | `scripts/run_phase_b3_exposure_control.py` | Implemented |
| Main report | `artifacts/reports/phase_b3_exposure_control.md` | Done |
| Constraint violations | `artifacts/reports/constraint_violations.csv` | Done |
| Beta tracking | `artifacts/reports/beta_tracking.csv` | Done |
| Gross exposure tracking | `artifacts/reports/gross_exposure.csv` | Done |

### B.3 Result

B.3 compared the B.2 `every_2_rebalances` candidate with and without projection. The projection uses scalar shaping first; when scalar scaling cannot meet the beta floor inside gross `1.5`, it applies a minimal SPY beta-floor projection. This is a constraint projection, not a new alpha or optimizer return-maximization step.

| Variant | CAGR | Sharpe | MaxDD | Turnover | Rebalance beta violations | Max gross | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| B.2 no projection | `18.33%` | `1.144` | `-33.69%` | `89.62` | `90` | `1.346` | Fails beta band |
| B.3 beta projection | `15.50%` | `1.069` | `-31.28%` | `81.67` | `0` | `1.500` | Fails CAGR tolerance |

### B.3 Decision

FAIL/WATCH. The projection satisfies rebalance-date gross and beta constraints and preserves turnover improvement, but the hard `0.5-0.8` beta band reduces CAGR by `2.83` percentage points versus B.2, exceeding the `2` percentage-point tolerance. Do not promote this B.3 variant as-is.

Recommended next B.3 iteration:

- Test a one-sided beta cap, e.g. beta `<=0.8`, instead of a hard lower floor.
- Test a slightly wider band such as `0.4-0.9` or `0.5-0.9` before introducing a full optimizer.
- Keep B.2 `every_2_rebalances` as the active promoted construction until a B.3 exposure-control variant clears both constraint and performance gates.

### B.3.1 Soft Policy Result

B.3.1 treated exposure shaping as policy design, not optimizer work. It tested one-sided beta caps and wider bands against the B.2 `every_2_rebalances` baseline.

| Policy | CAGR | Sharpe | MaxDD | Turnover | Rebalance beta violations | Max gross | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| B.2 no projection | `18.33%` | `1.144` | `-33.69%` | `89.62` | reference only | `1.346` | Reference |
| Cap `<=0.80` | `15.11%` | `1.081` | `-31.28%` | `78.36` | `0` | `1.341` | Fails CAGR tolerance |
| Cap `<=0.90` | `16.10%` | `1.085` | `-33.69%` | `82.24` | `0` | `1.346` | Fails CAGR tolerance |
| Band `0.4-0.9` | `16.17%` | `1.080` | `-33.69%` | `83.27` | `0` | `1.377` | Fails CAGR tolerance |
| Band `0.5-0.9` | `16.49%` | `1.075` | `-33.69%` | `85.36` | `0` | `1.500` | Pass |

Decision: promote `b3_band_50_90` as the current B.3 exposure policy candidate. It satisfies rebalance-date beta/gross constraints, keeps Sharpe within tolerance, keeps CAGR drop within `2` percentage points, and preserves most of the B.2 turnover improvement. Do not promote the hard `0.5-0.8` policy.

Residual caveat: B.3.1 gates are rebalance-date ex-ante controls. Daily beta can drift between rebalances; this should be tracked but not corrected daily unless B.4 risk-engine integration shows regime-specific need.

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
- B.3 hard beta band `0.5-0.8` is mechanically feasible with projection, but costs too much CAGR. B.3.1 soft band `0.5-0.9` passes the current policy gate; daily beta drift remains a monitoring item.
- Results validated on configured ticker universe with PIT liquidity mask, not true historical index membership.
- Historical index-membership data remains intentionally deferred; do not import it unless current-setup artifact checks become fragile.

---

## Iteration Log

| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-04-30 | B.0 baseline guard | Done | A.7.3 baseline locked; sp500 recommended validation end is `2026-04-24` unless PIT mask is refreshed |
| 2026-04-30 | B.1 simulator reproduction | Reconciled | Production open/next-day sp500 baseline: CAGR `17.56%`, Sharpe `1.116`, MaxDD `-26.98%`; within tolerance versus lagged matrix reference, not versus unlagged A.7.3 headline |
| 2026-05-01 | B.2 turnover control | Passed | Primary candidate `every_2_rebalances`: CAGR `18.33%`, Sharpe `1.144`, MaxDD `-33.69%`, turnover reduction `61.2%`; 50 bps Sharpe `0.999` versus same-cost baseline `0.765` |
| 2026-05-01 | B.3 exposure control | Fail/watch | Projection satisfies gross/beta constraints but CAGR drops to `15.50%`, `2.83` pp below B.2; keep B.2 active and iterate beta policy |
| 2026-05-01 | B.3.1 soft exposure policy | Passed | Promote `0.5-0.9` rebalance-date beta band: CAGR `16.49%`, Sharpe `1.075`, MaxDD `-33.69%`, turnover `85.36`, max gross `1.500` |
