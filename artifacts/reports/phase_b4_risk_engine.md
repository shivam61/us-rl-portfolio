# Phase B.4 — Risk Engine Formalization

- Run date: 2026-05-01 05:39:21 UTC
- Baseline: B.3.1 `b3_band_50_90` (CAGR `16.49%`, Sharpe `1.075`, MaxDD `-33.69%`, turnover `85.36`).
- Scope: no `volatility_score` changes, no trend-signal changes, no new alpha, RL disabled.
- Method: replace the static B.3.1 beta cap (0.90) with a stress-aware dynamic cap:
  `beta_cap = 0.90 - 0.20 × stress_score`  (range ~0.70 at max stress → 0.90 at zero stress).
  Beta floor held at 0.50; gross ≤ 1.5 preserved.

## Gates

- Gross exposure must stay `≤ 1.5`.
- No rebalance-date gate violations.
- Sharpe drop vs B.3.1 must be `≤ 0.05` (floor 1.025).
- CAGR drop vs B.3.1 must be `≤ 1.0%` (floor 15.49%).
- MaxDD must be improved or unchanged vs B.3.1.
- Turnover must not increase vs B.3.1 (≤ 85.36 × 1.05 = 89.63).

## Performance Comparison

| variant                   |   cagr |   sharpe |   max_dd |   turnover_sum |   max_target_gross |   control_gate_violations |   avg_dynamic_cap |   min_dynamic_cap |   cagr_vs_b3_1_delta |   sharpe_vs_b3_1_delta |   max_dd_vs_b3_1_delta | passes_b4   |
|:--------------------------|-------:|---------:|---------:|---------------:|-------------------:|--------------------------:|------------------:|------------------:|---------------------:|-----------------------:|-----------------------:|:------------|
| b3_1_reference            | 0.1649 |   1.0751 |  -0.3369 |        85.3615 |             1.5000 |                         0 |            0.9000 |            0.9000 |               0.0000 |                 0.0000 |                 0.0000 | True        |
| b4_stress_beta_cap        | 0.1595 |   1.0730 |  -0.3298 |        83.4921 |             1.5000 |                         0 |            0.8294 |            0.7006 |              -0.0054 |                -0.0020 |                 0.0071 | True        |
| b4_stress_cap_trend_boost | 0.1604 |   1.0780 |  -0.3298 |        84.1187 |             1.5000 |                         0 |            0.8294 |            0.7006 |              -0.0045 |                 0.0030 |                 0.0071 | True        |

## Stress-Beta-Cap Dynamics

Dynamic cap statistics (rebalance dates only):

                          stress_score                                                                       dynamic_beta_cap                                                                       beta_after                                                                 
                                 count      mean       std       min       25%       50%       75%       max            count      mean       std       min       25%       50%       75%       max      count      mean       std  min       25%       50%       75%       max
variant                                                                                                                                                                                                                                                                        
b4_stress_beta_cap               120.0  0.352894  0.241196  0.003969  0.151414  0.309204  0.526718  0.997024            120.0  0.829421  0.048239  0.700595  0.794656  0.838159  0.869717  0.899206      120.0  0.770134  0.128805  0.5  0.717171  0.818801  0.866028  0.899206
b4_stress_cap_trend_boost        120.0  0.352894  0.241196  0.003969  0.151414  0.309204  0.526718  0.997024            120.0  0.829421  0.048239  0.700595  0.794656  0.838159  0.869717  0.899206      120.0  0.770066  0.128946  0.5  0.717151  0.818801  0.866028  0.899206

## Interpretation

- PASS: `b4_stress_cap_trend_boost` — CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`, turnover `84.12`, avg dynamic cap `0.829` (min `0.701`).
- MaxDD improved or unchanged in: b4_stress_beta_cap, b4_stress_cap_trend_boost.

## Decision

- Promote `b4_stress_cap_trend_boost` as the Phase B.4 candidate. Carry it into B.5 final gate run.

## Output Files

- `artifacts/reports/phase_b4_risk_engine.md`
- `artifacts/reports/beta_cap_tracking.csv`
- `artifacts/reports/stress_vs_exposure.csv`
- `artifacts/reports/performance_vs_b3_1.csv`
