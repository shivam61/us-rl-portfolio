# Phase A.4.1 Crisis Diversifier v2 Results

- Run date: 2026-04-29 17:03:09 UTC
- Objective: build a truly orthogonal Sleeve 2 for the volatility alpha.
- Score inputs: balance sheet strength, cash-flow quality, profitability stability, valuation buffer.
- Excluded from score: returns, volatility, drawdown, momentum, and beta.
- Beta is used only after selection for sleeve construction.
- RL disabled.

## Data Availability

| universe     | feature           |   coverage_pct |   ticker_coverage_pct |
|:-------------|:------------------|---------------:|----------------------:|
| sp100_sample | debt_to_assets    |         0.9654 |                1.0000 |
| sp100_sample | debt_to_equity    |         0.9654 |                1.0000 |
| sp100_sample | interest_coverage |         0.9654 |                1.0000 |
| sp100_sample | ocf_to_net_income |         0.9654 |                1.0000 |
| sp100_sample | accruals_proxy    |         0.9654 |                1.0000 |
| sp100_sample | roe               |         0.9654 |                1.0000 |
| sp100_sample | gross_margin      |         0.9654 |                1.0000 |
| sp100_sample | eps_growth_yoy    |         0.9160 |                1.0000 |
| sp100_sample | pe_ratio          |         0.9654 |                1.0000 |
| sp100_sample | pb_ratio          |         0.9654 |                1.0000 |

## Standalone Metrics

| universe     | sleeve                                 | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |   target_beta |   avg_realized_beta |
|:-------------|:---------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|--------------:|--------------------:|
| sp100_sample | vol_top_10                             | volatility    | 0.2400 |   0.7948 |  -0.5088 |       0.3019 |        81.2000 |            239 |      nan      |              1.4099 |
| sp100_sample | vol_top_20                             | volatility    | 0.2024 |   0.8225 |  -0.4939 |       0.2460 |        59.0000 |            239 |      nan      |              1.1819 |
| sp100_sample | crisis_diversifier_top_10_equal_weight | diversifier   | 0.1794 |   0.8537 |  -0.4529 |       0.2101 |        83.0000 |            239 |      nan      |              0.9147 |
| sp100_sample | crisis_diversifier_top_20_equal_weight | diversifier   | 0.1728 |   0.8621 |  -0.4635 |       0.2004 |        50.4000 |            239 |      nan      |              0.9125 |
| sp100_sample | crisis_diversifier_top_30_equal_weight | diversifier   | 0.1687 |   0.8629 |  -0.4261 |       0.1955 |        25.4667 |            239 |      nan      |              0.8935 |
| sp100_sample | crisis_diversifier_top_10_beta_0_6     | diversifier   | 0.1391 |   0.7441 |  -0.4228 |       0.1869 |       125.3181 |            239 |        0.6000 |              0.6989 |
| sp100_sample | crisis_diversifier_top_20_beta_0_6     | diversifier   | 0.1224 |   0.7338 |  -0.4227 |       0.1668 |       125.4928 |            239 |        0.6000 |              0.6149 |
| sp100_sample | crisis_diversifier_top_30_beta_0_6     | diversifier   | 0.1364 |   0.8433 |  -0.3948 |       0.1617 |        98.4779 |            239 |        0.6000 |              0.6056 |
| sp100_sample | crisis_diversifier_top_10_beta_0_8     | diversifier   | 0.1432 |   0.7410 |  -0.4137 |       0.1933 |       124.0278 |            239 |        0.8000 |              0.8080 |
| sp100_sample | crisis_diversifier_top_20_beta_0_8     | diversifier   | 0.1526 |   0.8438 |  -0.4281 |       0.1808 |        93.0772 |            239 |        0.8000 |              0.8003 |
| sp100_sample | crisis_diversifier_top_30_beta_0_8     | diversifier   | 0.1497 |   0.8415 |  -0.4180 |       0.1779 |        60.0590 |            239 |        0.8000 |              0.8004 |

## Hard Gate

| universe     | sleeve                                 |   sharpe |   max_dd |   min_full_corr_vs_vol |   min_crisis_corr_vs_vol | passes_hard_gate   |
|:-------------|:---------------------------------------|---------:|---------:|-----------------------:|-------------------------:|:-------------------|
| sp100_sample | crisis_diversifier_top_10_equal_weight |   0.8537 |  -0.4529 |                 0.8852 |                   0.9236 | False              |
| sp100_sample | crisis_diversifier_top_20_equal_weight |   0.8621 |  -0.4635 |                 0.9108 |                   0.9354 | False              |
| sp100_sample | crisis_diversifier_top_30_equal_weight |   0.8629 |  -0.4261 |                 0.9091 |                   0.9371 | False              |
| sp100_sample | crisis_diversifier_top_10_beta_0_6     |   0.7441 |  -0.4228 |                 0.7492 |                   0.8102 | False              |
| sp100_sample | crisis_diversifier_top_20_beta_0_6     |   0.7338 |  -0.4227 |                 0.7107 |                   0.7665 | False              |
| sp100_sample | crisis_diversifier_top_30_beta_0_6     |   0.8433 |  -0.3948 |                 0.7139 |                   0.7664 | False              |
| sp100_sample | crisis_diversifier_top_10_beta_0_8     |   0.7410 |  -0.4137 |                 0.8076 |                   0.8449 | False              |
| sp100_sample | crisis_diversifier_top_20_beta_0_8     |   0.8438 |  -0.4281 |                 0.8258 |                   0.8464 | False              |
| sp100_sample | crisis_diversifier_top_30_beta_0_8     |   0.8415 |  -0.4180 |                 0.8341 |                   0.8562 | False              |

Gate result: FAIL

## Correlation

| universe     | vol_sleeve   | diversifier_sleeve                     |   full_correlation |   avg_rolling_252d_correlation |
|:-------------|:-------------|:---------------------------------------|-------------------:|-------------------------------:|
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_6     |             0.7492 |                         0.7049 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_8     |             0.8076 |                         0.7819 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_equal_weight |             0.8852 |                         0.8574 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_6     |             0.7107 |                         0.6693 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_8     |             0.8258 |                         0.8183 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_equal_weight |             0.9108 |                         0.8921 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_6     |             0.7139 |                         0.6810 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_8     |             0.8341 |                         0.8242 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_equal_weight |             0.9091 |                         0.8873 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_6     |             0.8398 |                         0.7973 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_8     |             0.8813 |                         0.8542 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_equal_weight |             0.9340 |                         0.9063 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_6     |             0.8060 |                         0.7707 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_8     |             0.9006 |                         0.8946 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_equal_weight |             0.9630 |                         0.9489 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_6     |             0.8083 |                         0.7830 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_8     |             0.9119 |                         0.9065 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_equal_weight |             0.9663 |                         0.9535 |

## Crisis Correlation

| universe     | vol_sleeve   | diversifier_sleeve                     |   crisis_correlation |   crisis_observations |
|:-------------|:-------------|:---------------------------------------|---------------------:|----------------------:|
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_6     |               0.8102 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_8     |               0.8449 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_equal_weight |               0.9236 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_6     |               0.7665 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_8     |               0.8464 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_equal_weight |               0.9354 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_6     |               0.7664 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_8     |               0.8562 |                   902 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_equal_weight |               0.9371 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_6     |               0.8886 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_8     |               0.9132 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_equal_weight |               0.9643 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_6     |               0.8490 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_8     |               0.9162 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_equal_weight |               0.9782 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_6     |               0.8465 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_8     |               0.9262 |                   902 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_equal_weight |               0.9805 |                   902 |

## Rolling Correlation

| universe     | vol_sleeve   | diversifier_sleeve                     |   rolling_corr_min |   rolling_corr_median |   rolling_corr_max |
|:-------------|:-------------|:---------------------------------------|-------------------:|----------------------:|-------------------:|
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_6     |             0.4221 |                0.7116 |             0.9024 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_8     |             0.5682 |                0.8001 |             0.9283 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_equal_weight |             0.5615 |                0.8689 |             0.9601 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_6     |             0.3898 |                0.6853 |             0.8847 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_8     |             0.6129 |                0.8243 |             0.9388 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_equal_weight |             0.6159 |                0.9032 |             0.9702 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_6     |             0.4365 |                0.6954 |             0.8768 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_8     |             0.6418 |                0.8291 |             0.9355 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_equal_weight |             0.6627 |                0.8899 |             0.9634 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_6     |             0.5914 |                0.7942 |             0.9324 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_8     |             0.7195 |                0.8602 |             0.9550 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_equal_weight |             0.7163 |                0.9101 |             0.9786 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_6     |             0.5778 |                0.7799 |             0.9199 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_8     |             0.7424 |                0.8929 |             0.9671 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_equal_weight |             0.7852 |                0.9536 |             0.9875 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_6     |             0.5553 |                0.7931 |             0.9129 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_8     |             0.7816 |                0.9075 |             0.9740 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_equal_weight |             0.8235 |                0.9545 |             0.9914 |

## Overlap

| universe     | vol_sleeve   | diversifier_sleeve                     |   ticker_overlap_pct |   sector_overlap_pct |   n_rebalances |
|:-------------|:-------------|:---------------------------------------|---------------------:|---------------------:|---------------:|
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_equal_weight |               0.3096 |               0.9168 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_equal_weight |               0.6033 |               0.9895 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_equal_weight |               0.7987 |               0.9994 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_6     |               0.3096 |               0.9168 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_6     |               0.6033 |               0.9895 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_6     |               0.7987 |               0.9994 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_10_beta_0_8     |               0.3096 |               0.9168 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_20_beta_0_8     |               0.6033 |               0.9895 |            239 |
| sp100_sample | vol_top_10   | crisis_diversifier_top_30_beta_0_8     |               0.7987 |               0.9994 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_equal_weight |               0.5238 |               0.9028 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_equal_weight |               0.5259 |               0.9884 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_equal_weight |               0.7483 |               0.9996 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_6     |               0.5238 |               0.9028 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_6     |               0.5259 |               0.9884 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_6     |               0.7483 |               0.9996 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_10_beta_0_8     |               0.5238 |               0.9028 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_20_beta_0_8     |               0.5259 |               0.9884 |            239 |
| sp100_sample | vol_top_20   | crisis_diversifier_top_30_beta_0_8     |               0.7483 |               0.9996 |            239 |

## Benchmarks

| universe     | benchmark                   |   cagr |   sharpe |   max_dd |   volatility |
|:-------------|:----------------------------|-------:|---------:|---------:|-------------:|
| sp100_sample | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |
| sp100_sample | equal_weight_universe_daily | 0.1620 |   0.8302 |  -0.4318 |       0.1952 |

## Blend Metrics

Skipped by decision rule because no standalone crisis diversifier passed the hard gate.

## Decision

Do not tune blend weights and do not scale SEC ingestion to SP500 from this result. The next step is feature-level redesign or a different orthogonal sleeve.
