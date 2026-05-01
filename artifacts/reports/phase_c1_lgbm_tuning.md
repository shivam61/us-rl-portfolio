# Phase C.1 — LightGBM Hyperparameter Tuning

- Run date: 2026-05-01 11:21:50 UTC
- Baseline: `b4_stress_cap_trend_boost` — CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`
- Universe: sp500, clipped to 2026-04-24, evaluation 2008–2026.
- Holdout window for IC grid search: 2019-01-01 — 2026-04-24.
- Construction preserved: every_2_rebalances cadence, dynamic beta cap, stress blend, trend sleeve.
- Tuned: num_leaves, min_data_in_leaf, feature_fraction, bagging_fraction, lambda_l1, lambda_l2.

## Verdict: REJECT

## Phase C.1 Acceptance Gates

| gate                                                | value   | target    | pass   |
|:----------------------------------------------------|:--------|:----------|:-------|
| Sharpe ≥ baseline − 0.05 (1.028)                    | 1.029   | ≥ 1.028   | True   |
| Sharpe preferred ≥ baseline + 0.05 (1.128)          | 1.029   | ≥ 1.128   | False  |
| MaxDD ≤ baseline (-32.98%)                          | -29.68% | ≤ -32.98% | True   |
| 50 bps Sharpe competitive (> B5 50bps 0.934 − 0.05) | 0.819   | ≥ 0.884   | False  |
| No turnover spike (sum ≤ 100)                       | 119.3   | ≤ 100.0   | False  |

## Baseline IC (current LGBM config)

| Metric | Value |
|---|---|
| Mean IC | -0.0123 |
| IC Sharpe | -1.3831 |
| N dates | 238 |

## Best Tuned Config IC

| Metric | Value |
|---|---|
| Mean IC | -0.0021 |
| IC Sharpe | -0.1389 |
| N dates | 94 |

**Best hyperparameters:**

- `num_leaves`: `15.0`
- `min_data_in_leaf`: `100.0`
- `feature_fraction`: `0.6`
- `bagging_fraction`: `0.9`
- `lambda_l1`: `0.0`
- `lambda_l2`: `0.0`

## Top 10 Grid Search Configs (holdout IC Sharpe)

|   mean_ic |   ic_sharpe |   n |   num_leaves |   min_data_in_leaf |   feature_fraction |   bagging_fraction |   lambda_l1 |   lambda_l2 |
|----------:|------------:|----:|-------------:|-------------------:|-------------------:|-------------------:|------------:|------------:|
|   -0.0021 |     -0.1389 |  94 |           15 |                100 |                0.6 |                0.9 |         0   |         0   |
|   -0.0023 |     -0.161  |  94 |           63 |                 20 |                0.6 |                0.7 |         0.5 |         0.5 |
|   -0.0024 |     -0.172  |  94 |           63 |                100 |                0.6 |                0.9 |         0.5 |         0   |
|   -0.0028 |     -0.193  |  94 |           31 |                 20 |                0.6 |                0.7 |         0   |         0.5 |
|   -0.003  |     -0.1984 |  94 |           15 |                100 |                0.6 |                0.9 |         0   |         0.5 |
|   -0.0032 |     -0.2069 |  94 |           15 |                 20 |                0.6 |                0.7 |         0.5 |         0   |
|   -0.0031 |     -0.2147 |  94 |           63 |                100 |                0.8 |                0.9 |         0.5 |         0.5 |
|   -0.0032 |     -0.2221 |  94 |           31 |                 20 |                0.6 |                0.7 |         0   |         0   |
|   -0.0035 |     -0.2255 |  94 |           15 |                 20 |                0.6 |                0.7 |         0.5 |         0.5 |
|   -0.0035 |     -0.2319 |  94 |           15 |                 20 |                1   |                0.9 |         0.5 |         0   |

## IC by Regime

| regime                | start      | end        |   baseline_mean_ic |   baseline_ic_sharpe |   best_mean_ic |   best_ic_sharpe |   n |
|:----------------------|:-----------|:-----------|-------------------:|---------------------:|---------------:|-----------------:|----:|
| full 2008-2026        | 2008-01-01 | 2026-04-24 |            -0.0123 |              -1.3831 |        -0.0134 |          -1.4591 | 238 |
| train 2008-2018       | 2008-01-01 | 2018-12-31 |            -0.0145 |              -1.2465 |        -0.0208 |          -1.7995 | 144 |
| holdout 2019-2026     | 2019-01-01 | 2026-04-24 |            -0.0088 |              -0.6436 |        -0.0021 |          -0.1389 |  94 |
| 2008 financial crisis | 2008-01-01 | 2009-12-31 |            -0.0059 |              -0.1681 |        -0.0085 |          -0.2904 |  26 |
| 2015-16 vol stress    | 2015-06-01 | 2016-12-31 |            -0.0571 |              -2.2366 |        -0.0700 |          -2.7339 |  21 |
| 2020 COVID            | 2020-01-01 | 2020-12-31 |             0.0057 |               0.1127 |         0.0217 |           0.3942 |  13 |
| 2022 bear market      | 2022-01-01 | 2022-12-31 |            -0.0140 |              -0.3509 |        -0.0128 |          -0.2856 |  13 |
| recovery 2023-2026    | 2023-01-01 | 2026-04-24 |             0.0004 |               0.0223 |         0.0090 |           0.4370 |  42 |

## Portfolio Metrics vs B.5 Baseline

| Metric | B.5 Baseline (vol) | C.1 Best (LGBM) | Delta |
|---|---|---|---|
| CAGR | 16.04% | 14.78% | -1.26% |
| Sharpe | 1.078 | 1.029 | -0.049 |
| MaxDD | -32.98% | -29.68% | +3.30% |
| Turnover sum | 84.1 | 119.3 | +35.2 |

## Cost Sensitivity (LGBM best)

|   cost_bps | cagr   |   sharpe | max_dd   |
|-----------:|:-------|---------:|:---------|
|         10 | 14.78% |    1.029 | -29.68%  |
|         25 | 13.66% |    0.95  | -29.68%  |
|         50 | 11.81% |    0.819 | -29.68%  |

## Regime Breakdown (LGBM best, 10 bps)

| regime                | start      | end        |    cagr |   sharpe |   max_dd |   n_days |
|:----------------------|:-----------|:-----------|--------:|---------:|---------:|---------:|
| 2008 financial crisis | 2008-01-01 | 2009-12-31 |  0.0605 |   0.3115 |  -0.2481 |      505 |
| 2015-16 vol stress    | 2015-06-01 | 2016-12-31 |  0.0635 |   0.4803 |  -0.1532 |      402 |
| 2020 COVID            | 2020-01-01 | 2020-12-31 |  0.3078 |   1.2060 |  -0.2968 |      253 |
| 2022 bear market      | 2022-01-01 | 2022-12-31 | -0.0707 |  -0.4209 |  -0.1583 |      251 |
| 2023-2026 recovery    | 2023-01-01 | 2026-04-24 |  0.1989 |   1.5890 |  -0.1345 |      830 |
| full 2008-2026        | 2008-01-01 | 2026-04-24 |  0.1478 |   1.0291 |  -0.2968 |     4607 |

## Output Files

- `artifacts/reports/phase_c1_lgbm_tuning.md`
- `artifacts/reports/ic_by_regime.csv`
- `artifacts/reports/portfolio_vs_baseline.csv`
- `artifacts/reports/phase_c1_grid_results.csv`

