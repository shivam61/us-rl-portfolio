# Phase A.1 Volatility Robustness

- Run date: 2026-04-28 18:40:20 UTC
- Universes tested: `sp100_sample, sp500_dynamic`
- Optional universes skipped: `config/universes/top_200_liquid.yaml`
- RL disabled for all portfolio tests.
- Phase A remains conditionally passed: Mean IC passed previously; IC Sharpe remains below the original gate.
- Current production alpha candidate: `volatility_score` / `volatility_only`.
- Wall time: 2102.4s

## Decision Frame

- Do not continue momentum-first.
- Treat high-vol/risk-premium and low-vol/quality directions as empirical alternatives.
- Do not tune optimizer/RL if the volatility sleeve fails robustness on sp500 and recent periods.

## Directionality

| universe      | direction             |   mean_period_ic |   positive_period_count |   period_count | best_selection         |   best_selection_excess_forward_return | best_portfolio_variant               |   best_portfolio_cagr |   best_portfolio_sharpe |
|:--------------|:----------------------|-----------------:|------------------------:|---------------:|:-----------------------|---------------------------------------:|:-------------------------------------|----------------------:|------------------------:|
| sp100_sample  | long_high_vol_rebound |           0.0379 |                       4 |              5 | top_10                 |                                 0.0082 | long_high_vol_rebound_optimizer_risk |                0.2501 |                  0.9171 |
| sp100_sample  | long_low_vol_quality  |          -0.0379 |                       1 |              5 | top_50                 |                                 0.0000 | long_low_vol_quality_top_50_ew       |                0.1616 |                  0.8523 |
| sp500_dynamic | long_high_vol_rebound |           0.0259 |                       5 |              5 | top_10                 |                                 0.0203 | long_high_vol_rebound_top_50_ew      |                0.2412 |                  0.5958 |
| sp500_dynamic | long_low_vol_quality  |          -0.0259 |                       0 |              5 | sector_balanced_top_50 |                                -0.0032 | long_low_vol_quality_optimizer_risk  |                0.0939 |                  0.6983 |

## IC By Period

| universe      | direction             |    period |   mean_ic |   ic_sharpe |   pct_positive_ic |   mean_top_bottom_spread |   n_dates |
|:--------------|:----------------------|----------:|----------:|------------:|------------------:|-------------------------:|----------:|
| sp100_sample  | long_high_vol_rebound | 2006_2009 |    0.0442 |      0.1557 |            0.5604 |                   0.0167 |       944 |
| sp100_sample  | long_high_vol_rebound | 2010_2014 |    0.0086 |      0.0280 |            0.5318 |                   0.0090 |      1258 |
| sp100_sample  | long_high_vol_rebound | 2015_2019 |    0.0465 |      0.1571 |            0.5541 |                   0.0107 |      1258 |
| sp100_sample  | long_high_vol_rebound | 2020_2022 |   -0.0133 |     -0.0452 |            0.4392 |                   0.0124 |       756 |
| sp100_sample  | long_high_vol_rebound | 2023_2026 |    0.1036 |      0.4236 |            0.6601 |                   0.0289 |       809 |
| sp100_sample  | long_low_vol_quality  | 2006_2009 |   -0.0442 |     -0.1557 |            0.4396 |                  -0.0167 |       944 |
| sp100_sample  | long_low_vol_quality  | 2010_2014 |   -0.0086 |     -0.0280 |            0.4682 |                  -0.0092 |      1258 |
| sp100_sample  | long_low_vol_quality  | 2015_2019 |   -0.0465 |     -0.1571 |            0.4459 |                  -0.0107 |      1258 |
| sp100_sample  | long_low_vol_quality  | 2020_2022 |    0.0133 |      0.0452 |            0.5608 |                  -0.0124 |       756 |
| sp100_sample  | long_low_vol_quality  | 2023_2026 |   -0.1036 |     -0.4236 |            0.3399 |                  -0.0289 |       809 |
| sp500_dynamic | long_high_vol_rebound | 2006_2009 |    0.0167 |      0.0670 |            0.5233 |                   0.0157 |       944 |
| sp500_dynamic | long_high_vol_rebound | 2010_2014 |    0.0157 |      0.0595 |            0.5421 |                   0.0062 |      1258 |
| sp500_dynamic | long_high_vol_rebound | 2015_2019 |    0.0190 |      0.0801 |            0.5064 |                   0.0051 |      1258 |
| sp500_dynamic | long_high_vol_rebound | 2020_2022 |    0.0172 |      0.0627 |            0.4987 |                   0.0110 |       756 |
| sp500_dynamic | long_high_vol_rebound | 2023_2026 |    0.0611 |      0.2440 |            0.5575 |                   0.0235 |       809 |
| sp500_dynamic | long_low_vol_quality  | 2006_2009 |   -0.0167 |     -0.0670 |            0.4767 |                  -0.0157 |       944 |
| sp500_dynamic | long_low_vol_quality  | 2010_2014 |   -0.0157 |     -0.0595 |            0.4579 |                  -0.0062 |      1258 |
| sp500_dynamic | long_low_vol_quality  | 2015_2019 |   -0.0190 |     -0.0801 |            0.4936 |                  -0.0051 |      1258 |
| sp500_dynamic | long_low_vol_quality  | 2020_2022 |   -0.0172 |     -0.0627 |            0.5013 |                  -0.0110 |       756 |
| sp500_dynamic | long_low_vol_quality  | 2023_2026 |   -0.0611 |     -0.2440 |            0.4425 |                  -0.0235 |       809 |

## IC By Regime

| universe      | direction             | regime   |   mean_ic |   ic_sharpe |   pct_positive_ic |   mean_top_bottom_spread |   n_dates |
|:--------------|:----------------------|:---------|----------:|------------:|------------------:|-------------------------:|----------:|
| sp100_sample  | long_high_vol_rebound | low_vix  |    0.0571 |      0.2143 |            0.6028 |                   0.0205 |      1901 |
| sp100_sample  | long_high_vol_rebound | high_vix |    0.0339 |      0.1067 |            0.5406 |                   0.0127 |      1084 |
| sp100_sample  | long_high_vol_rebound | crash    |    0.0814 |      0.2547 |            0.5861 |                   0.0255 |       906 |
| sp100_sample  | long_high_vol_rebound | recovery |    0.0648 |      0.1924 |            0.5685 |                   0.0204 |       248 |
| sp100_sample  | long_high_vol_rebound | trending |    0.0160 |      0.0574 |            0.5221 |                   0.0184 |      1061 |
| sp100_sample  | long_high_vol_rebound | sideways |    0.0374 |      0.1284 |            0.5597 |                   0.0098 |      1708 |
| sp100_sample  | long_low_vol_quality  | low_vix  |   -0.0571 |     -0.2143 |            0.3972 |                  -0.0205 |      1901 |
| sp100_sample  | long_low_vol_quality  | high_vix |   -0.0339 |     -0.1067 |            0.4594 |                  -0.0127 |      1084 |
| sp100_sample  | long_low_vol_quality  | crash    |   -0.0814 |     -0.2547 |            0.4139 |                  -0.0256 |       906 |
| sp100_sample  | long_low_vol_quality  | recovery |   -0.0648 |     -0.1924 |            0.4315 |                  -0.0204 |       248 |
| sp100_sample  | long_low_vol_quality  | trending |   -0.0160 |     -0.0574 |            0.4779 |                  -0.0184 |      1061 |
| sp100_sample  | long_low_vol_quality  | sideways |   -0.0374 |     -0.1284 |            0.4403 |                  -0.0099 |      1708 |
| sp500_dynamic | long_high_vol_rebound | low_vix  |    0.0247 |      0.1060 |            0.5387 |                   0.0095 |      1901 |
| sp500_dynamic | long_high_vol_rebound | high_vix |    0.0502 |      0.1809 |            0.5369 |                   0.0233 |      1084 |
| sp500_dynamic | long_high_vol_rebound | crash    |    0.0892 |      0.3020 |            0.5894 |                   0.0343 |       906 |
| sp500_dynamic | long_high_vol_rebound | recovery |    0.0747 |      0.2413 |            0.5685 |                   0.0356 |       248 |
| sp500_dynamic | long_high_vol_rebound | trending |    0.0118 |      0.0497 |            0.5014 |                   0.0101 |      1061 |
| sp500_dynamic | long_high_vol_rebound | sideways |    0.0112 |      0.0445 |            0.5018 |                   0.0049 |      1708 |
| sp500_dynamic | long_low_vol_quality  | low_vix  |   -0.0247 |     -0.1060 |            0.4613 |                  -0.0094 |      1901 |
| sp500_dynamic | long_low_vol_quality  | high_vix |   -0.0502 |     -0.1809 |            0.4631 |                  -0.0233 |      1084 |
| sp500_dynamic | long_low_vol_quality  | crash    |   -0.0892 |     -0.3020 |            0.4106 |                  -0.0343 |       906 |
| sp500_dynamic | long_low_vol_quality  | recovery |   -0.0747 |     -0.2413 |            0.4315 |                  -0.0356 |       248 |
| sp500_dynamic | long_low_vol_quality  | trending |   -0.0118 |     -0.0497 |            0.4986 |                  -0.0101 |      1061 |
| sp500_dynamic | long_low_vol_quality  | sideways |   -0.0112 |     -0.0445 |            0.4982 |                  -0.0049 |      1708 |

## Selection Sweep

| universe      | direction             | selection              |   top_n | sector_balanced   |   mean_forward_return |   mean_universe_forward_return |   mean_excess_forward_return |   hit_rate_vs_top_quintile |   n_rebalances |
|:--------------|:----------------------|:-----------------------|--------:|:------------------|----------------------:|-------------------------------:|-----------------------------:|---------------------------:|---------------:|
| sp100_sample  | long_high_vol_rebound | top_10                 |      10 | False             |                0.0219 |                         0.0138 |                       0.0082 |                     0.3099 |           5025 |
| sp100_sample  | long_high_vol_rebound | top_20                 |      20 | False             |                0.0180 |                         0.0138 |                       0.0042 |                     0.2651 |           5025 |
| sp100_sample  | long_high_vol_rebound | top_30                 |      30 | False             |                0.0158 |                         0.0138 |                       0.0020 |                     0.2361 |           5025 |
| sp100_sample  | long_high_vol_rebound | top_50                 |      50 | False             |                0.0138 |                         0.0138 |                       0.0000 |                     0.2090 |           5025 |
| sp100_sample  | long_high_vol_rebound | sector_balanced_top_20 |      20 | True              |                0.0167 |                         0.0138 |                       0.0029 |                     0.2504 |           5025 |
| sp100_sample  | long_high_vol_rebound | sector_balanced_top_50 |      50 | True              |                0.0138 |                         0.0138 |                       0.0000 |                     0.2090 |           5025 |
| sp100_sample  | long_low_vol_quality  | top_10                 |      10 | False             |                0.0093 |                         0.0138 |                      -0.0045 |                     0.1442 |           5025 |
| sp100_sample  | long_low_vol_quality  | top_20                 |      20 | False             |                0.0099 |                         0.0138 |                      -0.0039 |                     0.1567 |           5025 |
| sp100_sample  | long_low_vol_quality  | top_30                 |      30 | False             |                0.0109 |                         0.0138 |                      -0.0029 |                     0.1729 |           5025 |
| sp100_sample  | long_low_vol_quality  | top_50                 |      50 | False             |                0.0138 |                         0.0138 |                       0.0000 |                     0.2090 |           5025 |
| sp100_sample  | long_low_vol_quality  | sector_balanced_top_20 |      20 | True              |                0.0112 |                         0.0138 |                      -0.0026 |                     0.1691 |           5025 |
| sp100_sample  | long_low_vol_quality  | sector_balanced_top_50 |      50 | True              |                0.0138 |                         0.0138 |                      -0.0000 |                     0.2090 |           5025 |
| sp500_dynamic | long_high_vol_rebound | top_10                 |      10 | False             |                0.0338 |                         0.0135 |                       0.0203 |                     0.3734 |           5025 |
| sp500_dynamic | long_high_vol_rebound | top_20                 |      20 | False             |                0.0303 |                         0.0135 |                       0.0168 |                     0.3567 |           5025 |
| sp500_dynamic | long_high_vol_rebound | top_30                 |      30 | False             |                0.0273 |                         0.0135 |                       0.0138 |                     0.3434 |           5025 |
| sp500_dynamic | long_high_vol_rebound | top_50                 |      50 | False             |                0.0238 |                         0.0135 |                       0.0103 |                     0.3227 |           5025 |
| sp500_dynamic | long_high_vol_rebound | sector_balanced_top_20 |      20 | True              |                0.0271 |                         0.0135 |                       0.0136 |                     0.3307 |           5025 |
| sp500_dynamic | long_high_vol_rebound | sector_balanced_top_50 |      50 | True              |                0.0218 |                         0.0135 |                       0.0083 |                     0.3037 |           5025 |
| sp500_dynamic | long_low_vol_quality  | top_10                 |      10 | False             |                0.0090 |                         0.0135 |                      -0.0045 |                     0.1385 |           5025 |
| sp500_dynamic | long_low_vol_quality  | top_20                 |      20 | False             |                0.0095 |                         0.0135 |                      -0.0040 |                     0.1373 |           5025 |
| sp500_dynamic | long_low_vol_quality  | top_30                 |      30 | False             |                0.0095 |                         0.0135 |                      -0.0040 |                     0.1395 |           5025 |
| sp500_dynamic | long_low_vol_quality  | top_50                 |      50 | False             |                0.0095 |                         0.0135 |                      -0.0040 |                     0.1413 |           5025 |
| sp500_dynamic | long_low_vol_quality  | sector_balanced_top_20 |      20 | True              |                0.0099 |                         0.0135 |                      -0.0037 |                     0.1413 |           5025 |
| sp500_dynamic | long_low_vol_quality  | sector_balanced_top_50 |      50 | True              |                0.0103 |                         0.0135 |                      -0.0032 |                     0.1448 |           5025 |

## Portfolio Backtests

| universe      | variant                                 | direction             |    top_n | use_optimizer   | use_risk_engine   |   cagr |   sharpe |   max_dd |   volatility |   mean_ic |   ic_sharpe |   mean_spread |   n_rebalances |   trade_count |
|:--------------|:----------------------------------------|:----------------------|---------:|:----------------|:------------------|-------:|---------:|---------:|-------------:|----------:|------------:|--------------:|---------------:|--------------:|
| sp100_sample  | long_high_vol_rebound_top_10_ew         | long_high_vol_rebound |  10.0000 | False           | False             | 0.2501 |   0.8853 |  -0.5117 |       0.2824 |    0.0408 |      0.1259 |        0.0168 |            238 |          2815 |
| sp100_sample  | long_high_vol_rebound_top_20_ew         | long_high_vol_rebound |  20.0000 | False           | False             | 0.1976 |   0.8143 |  -0.5014 |       0.2426 |    0.0408 |      0.1259 |        0.0168 |            238 |          5350 |
| sp100_sample  | long_high_vol_rebound_top_30_ew         | long_high_vol_rebound |  30.0000 | False           | False             | 0.1756 |   0.8239 |  -0.4570 |       0.2131 |    0.0408 |      0.1259 |        0.0168 |            238 |          7632 |
| sp100_sample  | long_high_vol_rebound_top_50_ew         | long_high_vol_rebound |  50.0000 | False           | False             | 0.1616 |   0.8523 |  -0.4306 |       0.1896 |    0.0408 |      0.1259 |        0.0168 |            238 |          9710 |
| sp100_sample  | long_high_vol_rebound_optimizer_no_risk | long_high_vol_rebound | nan      | True            | False             | 0.2055 |   0.8658 |  -0.4690 |       0.2373 |    0.0408 |      0.1259 |        0.0168 |            238 |          5843 |
| sp100_sample  | long_high_vol_rebound_optimizer_risk    | long_high_vol_rebound | nan      | True            | True              | 0.1731 |   0.9171 |  -0.3706 |       0.1887 |    0.0408 |      0.1259 |        0.0168 |            238 |          5812 |
| sp100_sample  | long_low_vol_quality_top_10_ew          | long_low_vol_quality  |  10.0000 | False           | False             | 0.0983 |   0.6447 |  -0.3760 |       0.1525 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          2974 |
| sp100_sample  | long_low_vol_quality_top_20_ew          | long_low_vol_quality  |  20.0000 | False           | False             | 0.1075 |   0.6817 |  -0.3903 |       0.1577 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          5343 |
| sp100_sample  | long_low_vol_quality_top_30_ew          | long_low_vol_quality  |  30.0000 | False           | False             | 0.1291 |   0.7587 |  -0.4015 |       0.1702 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          7619 |
| sp100_sample  | long_low_vol_quality_top_50_ew          | long_low_vol_quality  |  50.0000 | False           | False             | 0.1616 |   0.8523 |  -0.4306 |       0.1896 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          9710 |
| sp100_sample  | long_low_vol_quality_optimizer_no_risk  | long_low_vol_quality  | nan      | True            | False             | 0.1013 |   0.6817 |  -0.3642 |       0.1485 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          5884 |
| sp100_sample  | long_low_vol_quality_optimizer_risk     | long_low_vol_quality  | nan      | True            | True              | 0.0834 |   0.6890 |  -0.2633 |       0.1211 |   -0.0408 |     -0.1259 |       -0.0179 |            238 |          5850 |
| sp100_sample  | spy_buy_hold                            | benchmark             | nan      | False           | False             | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |  nan      |    nan      |      nan      |              0 |             0 |
| sp100_sample  | equal_weight_universe_daily             | benchmark             | nan      | False           | False             | 0.1620 |   0.8302 |  -0.4318 |       0.1952 |  nan      |    nan      |      nan      |              0 |             0 |
| sp500_dynamic | long_high_vol_rebound_top_10_ew         | long_high_vol_rebound |  10.0000 | False           | False             | 0.2412 |   0.5666 |  -0.7073 |       0.4257 |    0.0339 |      0.1298 |        0.0149 |            230 |          3117 |
| sp500_dynamic | long_high_vol_rebound_top_20_ew         | long_high_vol_rebound |  20.0000 | False           | False             | 0.2126 |   0.5606 |  -0.6780 |       0.3791 |    0.0339 |      0.1298 |        0.0149 |            230 |          6020 |
| sp500_dynamic | long_high_vol_rebound_top_30_ew         | long_high_vol_rebound |  30.0000 | False           | False             | 0.2027 |   0.5773 |  -0.6641 |       0.3510 |    0.0339 |      0.1298 |        0.0149 |            230 |          8900 |
| sp500_dynamic | long_high_vol_rebound_top_50_ew         | long_high_vol_rebound |  50.0000 | False           | False             | 0.1893 |   0.5958 |  -0.6378 |       0.3177 |    0.0339 |      0.1298 |        0.0149 |            230 |         14446 |
| sp500_dynamic | long_high_vol_rebound_optimizer_no_risk | long_high_vol_rebound | nan      | True            | False             | 0.2070 |   0.5527 |  -0.6696 |       0.3745 |    0.0339 |      0.1298 |        0.0149 |            230 |         10360 |
| sp500_dynamic | long_high_vol_rebound_optimizer_risk    | long_high_vol_rebound | nan      | True            | True              | 0.1753 |   0.5829 |  -0.5779 |       0.3008 |    0.0339 |      0.1298 |        0.0149 |            230 |          9474 |
| sp500_dynamic | long_low_vol_quality_top_10_ew          | long_low_vol_quality  |  10.0000 | False           | False             | 0.0820 |   0.5618 |  -0.4015 |       0.1460 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |          3311 |
| sp500_dynamic | long_low_vol_quality_top_20_ew          | long_low_vol_quality  |  20.0000 | False           | False             | 0.0852 |   0.5836 |  -0.4053 |       0.1460 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |          6322 |
| sp500_dynamic | long_low_vol_quality_top_30_ew          | long_low_vol_quality  |  30.0000 | False           | False             | 0.0865 |   0.5855 |  -0.4090 |       0.1478 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |          9119 |
| sp500_dynamic | long_low_vol_quality_top_50_ew          | long_low_vol_quality  |  50.0000 | False           | False             | 0.0919 |   0.6058 |  -0.4289 |       0.1517 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |         14644 |
| sp500_dynamic | long_low_vol_quality_optimizer_no_risk  | long_low_vol_quality  | nan      | True            | False             | 0.0939 |   0.6438 |  -0.3983 |       0.1458 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |          9481 |
| sp500_dynamic | long_low_vol_quality_optimizer_risk     | long_low_vol_quality  | nan      | True            | True              | 0.0830 |   0.6983 |  -0.2867 |       0.1188 |   -0.0339 |     -0.1298 |       -0.0150 |            230 |          7850 |
| sp500_dynamic | spy_buy_hold                            | benchmark             | nan      | False           | False             | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |  nan      |    nan      |      nan      |              0 |             0 |
| sp500_dynamic | equal_weight_universe_daily             | benchmark             | nan      | False           | False             | 0.1649 |   0.7787 |  -0.4912 |       0.2117 |  nan      |    nan      |      nan      |              0 |             0 |

## Success Criteria

- `sp100_sample` high-vol direction mean period IC > 0.03: PASS (0.038)
- `sp100_sample` positive in most periods: PASS (4/5)
- `sp100_sample` top-bottom spread > 1%: PASS (1.55%)
- `sp500_dynamic` high-vol direction mean period IC > 0.02: PASS (0.026)
- `sp500_dynamic` positive in most periods: PASS (5/5)
- `sp500_dynamic` top-bottom spread > 1%: PASS (1.23%)

## Interpretation

- `volatility_score` is not just a sp100 artifact. The high-vol/risk-premium direction has positive IC in `4/5` sp100 periods and `5/5` sp500 periods.
- The correct direction is high-vol rebound/risk-premium. The low-vol/quality direction is negative across every sp500 period and should not be encoded as the production sleeve.
- Best selection edge is concentrated in smaller books: Top-10 has the strongest forward-return edge on both sp100 and sp500.
- Portfolio expression is not production-clean yet. On sp500, high-vol Top-N variants beat equal-weight on CAGR but have worse Sharpe and much deeper drawdowns; optimizer+risk reduces drawdown but still leaves `MaxDD=-57.79%`.
- Current decision: keep `volatility_score` as the production alpha candidate, keep RL disabled, and solve beta/crash exposure before calling this a production baseline.
- If controlled-beta/crash-aware expression destroys the alpha, stop production tuning and return to feature engineering: earnings quality, analyst revisions, value-quality composite, and regime-conditional factors.
