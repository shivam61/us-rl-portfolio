# Phase G.0 — Feature Parity Check

- Run date: 2026-05-04 10:14:40 UTC
- Universe: config/universes/sp500.yaml
- Holdout window: 2019-01-01 → 2026-04-24
- Steps checked: 30 (last 30 rebalance steps)
- Gate: max absolute deviation < 1e-06 for all 42 features

## Verdict: **PASS**

| Metric | Value |
|--------|-------|
| Max global deviation | `0.00e+00` |
| Total NaN values | 0 |
| Range violations | 0 |
| Steps passing gate | 30 / 30 |

## Per-Step Deviation

| date       |   step |   max_dev | worst_feat        | gate_pass   |
|:-----------|-------:|----------:|:------------------|:------------|
| 2021-12-20 |     19 |         0 | vix_percentile_1y | True        |
| 2022-02-14 |     20 |         0 | vix_percentile_1y | True        |
| 2022-04-11 |     21 |         0 | vix_percentile_1y | True        |
| 2022-06-06 |     22 |         0 | vix_percentile_1y | True        |
| 2022-08-01 |     23 |         0 | vix_percentile_1y | True        |
| 2022-09-26 |     24 |         0 | vix_percentile_1y | True        |
| 2022-11-21 |     25 |         0 | vix_percentile_1y | True        |
| 2023-01-17 |     26 |         0 | vix_percentile_1y | True        |
| 2023-03-13 |     27 |         0 | vix_percentile_1y | True        |
| 2023-05-08 |     28 |         0 | vix_percentile_1y | True        |
| 2023-07-03 |     29 |         0 | vix_percentile_1y | True        |
| 2023-08-28 |     30 |         0 | vix_percentile_1y | True        |
| 2023-10-23 |     31 |         0 | vix_percentile_1y | True        |
| 2023-12-18 |     32 |         0 | vix_percentile_1y | True        |
| 2024-02-12 |     33 |         0 | vix_percentile_1y | True        |
| 2024-04-08 |     34 |         0 | vix_percentile_1y | True        |
| 2024-06-03 |     35 |         0 | vix_percentile_1y | True        |
| 2024-07-29 |     36 |         0 | vix_percentile_1y | True        |
| 2024-09-23 |     37 |         0 | vix_percentile_1y | True        |
| 2024-11-18 |     38 |         0 | vix_percentile_1y | True        |
| 2025-01-13 |     39 |         0 | vix_percentile_1y | True        |
| 2025-03-10 |     40 |         0 | vix_percentile_1y | True        |
| 2025-05-05 |     41 |         0 | vix_percentile_1y | True        |
| 2025-06-30 |     42 |         0 | vix_percentile_1y | True        |
| 2025-08-25 |     43 |         0 | vix_percentile_1y | True        |
| 2025-10-20 |     44 |         0 | vix_percentile_1y | True        |
| 2025-12-15 |     45 |         0 | vix_percentile_1y | True        |
| 2026-02-09 |     46 |         0 | vix_percentile_1y | True        |
| 2026-04-06 |     47 |         0 | vix_percentile_1y | True        |
| 2026-04-06 |     48 |         0 | vix_percentile_1y | True        |

## Per-Feature Maximum Deviation (across all checked steps)

_All deviations exactly zero._

## Range Violations

_None._

## Methodology

**Backtest path:** Run `PortfolioEnvV2` (no-op policy) on the holdout window.
The env's `_build_obs()` calls `build_state_v2` at each rebalance step and
returns the obs vector. This is the ground-truth reference.

**Live sim path:** After the episode, call `build_state_v2` standalone with the
portfolio state (equity_frac, trend_frac, cash_frac, nav_series) captured from
the corresponding episode step. This simulates what the nightly production
pipeline will do when it calls `build_state_v2` with tracked portfolio state.

**Gate:** max|backtest_obs − live_obs| < 1e-6 for each of the last 30 steps.
A deviation of exactly 0.0 is expected since both paths call the same function
with identical arguments; the 1e-6 tolerance guards against float32/float64 cast
differences.

## Artifacts

- `artifacts/reports/phase_g0_feature_parity.md` — this file
- `artifacts/reports/g0_feature_max_dev.csv` — per-feature deviation (for G.3 baseline)
- `artifacts/reports/g0_per_step_deviation.csv` — per-step deviation detail
