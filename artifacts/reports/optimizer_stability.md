# Optimizer Stability

- Run ID: `optimizer_stability_20260428T125149Z`
- Config: `config/baseline_v1_volatility_score_sp100.yaml`
- Universe: `config/universes/sp100.yaml`
- Default alpha: `volatility_score`

## Strategy Metrics

- CAGR: `17.30%`
- Sharpe: `0.917`
- MaxDD: `-37.06%`

## Fallback Counts

- `full_optimizer`: 236
- `relaxed_constraints`: 2
- `equal_weight_top_n`: 1

## Aggregate Diagnostics

- Rebalances: `239`
- Max covariance condition number: `4.025e+02`
- Median covariance condition number: `1.509e+02`
- Max stock-weight overage: `0.000e+00`
- Max sector-cap overage: `0.000e+00`
- Max turnover overage: `4.399e-04`

## Worst Condition Numbers

| date       | fallback_level   |   cov_condition_number |   num_assets |   gross_raw |
|:-----------|:-----------------|-----------------------:|-------------:|------------:|
| 2009-08-16 | full_optimizer   |             4.0247e+02 |           37 |  9.2500e-01 |
| 2009-09-13 | full_optimizer   |             3.9272e+02 |           37 |  9.2500e-01 |
| 2009-07-19 | full_optimizer   |             3.9152e+02 |           37 |  8.5000e-01 |
| 2009-06-21 | full_optimizer   |             3.8451e+02 |           37 |  7.7504e-01 |
| 2009-05-24 | full_optimizer   |             3.7601e+02 |           36 |  7.7500e-01 |
| 2009-10-11 | full_optimizer   |             3.7548e+02 |           37 |  8.2480e-01 |
| 2009-04-26 | full_optimizer   |             3.6942e+02 |           36 |  8.4992e-01 |
| 2009-11-08 | full_optimizer   |             3.6779e+02 |           37 |  9.5002e-01 |
| 2009-03-29 | full_optimizer   |             3.4606e+02 |           36 |  8.4998e-01 |
| 2012-05-20 | full_optimizer   |             3.3936e+02 |           39 |  9.4969e-01 |

## Equal-Weight Fallback Samples

| date       |   cov_condition_number |   num_assets |   gross_raw |
|:-----------|-----------------------:|-------------:|------------:|
| 2011-09-11 |             1.7671e+02 |           39 |  1.0000e+00 |
