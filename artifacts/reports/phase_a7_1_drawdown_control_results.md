# Phase A.7.1 Drawdown Control Results

- Run date: 2026-04-29 18:04:39 UTC
- Base alpha: unchanged `vol_top_20` volatility sleeve.
- Hedge sleeve: `trend_3m_6m_long_cash` from A.7.
- Tests: wider trend frontier, continuous stress scaling, residual beta hedge.
- RL disabled.

## Benchmarks

| universe      | benchmark                   |   cagr |   sharpe |   max_dd |   volatility |
|:--------------|:----------------------------|-------:|---------:|---------:|-------------:|
| sp500_dynamic | spy_buy_hold                | 0.1114 |   0.5607 |  -0.5187 |       0.1986 |
| sp500_dynamic | equal_weight_universe_daily | 0.1648 |   0.7784 |  -0.4912 |       0.2117 |

## Metrics

| universe      | sleeve                         | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   avg_gross |   max_gross |   n_rebalances |   base_vol_weight |   base_trend_weight |   stress_k |   beta_target |
|:--------------|:-------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|------------:|------------:|---------------:|------------------:|--------------------:|-----------:|--------------:|
| sp500_dynamic | vol_top_20                     | volatility    | 0.2664 |   0.6392 |  -0.6242 |       0.4167 |       128.0000 |      0.9993 |      1.0000 |            239 |          nan      |            nan      |   nan      |      nan      |
| sp500_dynamic | trend_3m_6m_long_cash          | trend         | 0.1144 |   1.1862 |  -0.1456 |       0.0964 |       110.8484 |      1.2442 |      1.5000 |            239 |          nan      |            nan      |   nan      |      nan      |
| sp500_dynamic | a7_1_frontier_60_40            | a7_1_blend    | 0.2292 |   0.8987 |  -0.4517 |       0.2551 |       121.1394 |      1.0973 |      1.2000 |           4610 |            0.6000 |              0.4000 |     0.0000 |      nan      |
| sp500_dynamic | a7_1_frontier_55_45            | a7_1_blend    | 0.2222 |   0.9432 |  -0.4261 |       0.2356 |       120.2818 |      1.1095 |      1.2250 |           4610 |            0.5500 |              0.4500 |     0.0000 |      nan      |
| sp500_dynamic | a7_1_frontier_50_50            | a7_1_blend    | 0.2147 |   0.9920 |  -0.3995 |       0.2164 |       119.4242 |      1.1218 |      1.2500 |           4610 |            0.5000 |              0.5000 |     0.0000 |      nan      |
| sp500_dynamic | a7_1_frontier_45_55            | a7_1_blend    | 0.2067 |   1.0457 |  -0.3718 |       0.1977 |       118.5666 |      1.1340 |      1.2750 |           4610 |            0.4500 |              0.5500 |     0.0000 |      nan      |
| sp500_dynamic | a7_1_frontier_40_60            | a7_1_blend    | 0.1982 |   1.1046 |  -0.3431 |       0.1794 |       117.7091 |      1.1462 |      1.3000 |           4610 |            0.4000 |              0.6000 |     0.0000 |      nan      |
| sp500_dynamic | a7_1_stress_60_40_k_10         | a7_1_blend    | 0.2371 |   1.0315 |  -0.4081 |       0.2299 |       159.0084 |      1.1025 |      1.2472 |           4610 |            0.6000 |              0.4000 |     0.1000 |      nan      |
| sp500_dynamic | a7_1_stress_60_40_k_20         | a7_1_blend    | 0.2439 |   1.1840 |  -0.3617 |       0.2060 |       197.0132 |      1.1077 |      1.2944 |           4610 |            0.6000 |              0.4000 |     0.2000 |      nan      |
| sp500_dynamic | a7_1_stress_60_40_k_30         | a7_1_blend    | 0.2496 |   1.3570 |  -0.3123 |       0.1839 |       235.1281 |      1.1130 |      1.3417 |           4610 |            0.6000 |              0.4000 |     0.3000 |      nan      |
| sp500_dynamic | a7_1_stress_50_50_k_10         | a7_1_blend    | 0.2211 |   1.1494 |  -0.3524 |       0.1923 |       157.2816 |      1.1270 |      1.2972 |           4610 |            0.5000 |              0.5000 |     0.1000 |      nan      |
| sp500_dynamic | a7_1_stress_50_50_k_20         | a7_1_blend    | 0.2263 |   1.3305 |  -0.3025 |       0.1701 |       195.2360 |      1.1322 |      1.3444 |           4610 |            0.5000 |              0.5000 |     0.2000 |      nan      |
| sp500_dynamic | a7_1_stress_50_50_k_30         | a7_1_blend    | 0.2276 |   1.4883 |  -0.2641 |       0.1529 |       231.3958 |      1.1375 |      1.3750 |           4610 |            0.5000 |              0.5000 |     0.3000 |      nan      |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | a7_1_blend    | 0.2585 |   1.3069 |  -0.3810 |       0.1978 |       228.6637 |      1.0926 |      1.8382 |           4610 |            0.6000 |              0.4000 |     0.1000 |        0.7000 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | a7_1_blend    | 0.2709 |   1.4981 |  -0.3438 |       0.1808 |       260.2412 |      1.1309 |      1.9960 |           4610 |            0.6000 |              0.4000 |     0.1000 |        0.5000 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | a7_1_blend    | 0.2536 |   1.3708 |  -0.3515 |       0.1850 |       238.1089 |      1.0713 |      1.7135 |           4610 |            0.6000 |              0.4000 |     0.2000 |        0.7000 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | a7_1_blend    | 0.2635 |   1.5487 |  -0.3203 |       0.1701 |       266.8187 |      1.0945 |      1.8713 |           4610 |            0.6000 |              0.4000 |     0.2000 |        0.5000 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | a7_1_blend    | 0.2323 |   1.3291 |  -0.3439 |       0.1747 |       198.7549 |      1.0885 |      1.6801 |           4610 |            0.5000 |              0.5000 |     0.1000 |        0.7000 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | a7_1_blend    | 0.2422 |   1.5145 |  -0.3138 |       0.1599 |       229.3387 |      1.0957 |      1.8378 |           4610 |            0.5000 |              0.5000 |     0.1000 |        0.5000 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | a7_1_blend    | 0.2308 |   1.4433 |  -0.2988 |       0.1599 |       214.4577 |      1.0843 |      1.5554 |           4610 |            0.5000 |              0.5000 |     0.2000 |        0.7000 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | a7_1_blend    | 0.2359 |   1.5845 |  -0.2885 |       0.1489 |       238.8961 |      1.0759 |      1.7131 |           4610 |            0.5000 |              0.5000 |     0.2000 |        0.5000 |

## Gate

| universe      | sleeve                         |   cagr |   sharpe |   max_dd |   equal_weight_sharpe |   trend_crisis_corr_vs_vol | passes_gate   |
|:--------------|:-------------------------------|-------:|---------:|---------:|----------------------:|---------------------------:|:--------------|
| sp500_dynamic | a7_1_frontier_60_40            | 0.2292 |   0.8987 |  -0.4517 |                0.7784 |                    -0.1151 | False         |
| sp500_dynamic | a7_1_frontier_55_45            | 0.2222 |   0.9432 |  -0.4261 |                0.7784 |                    -0.1151 | False         |
| sp500_dynamic | a7_1_frontier_50_50            | 0.2147 |   0.9920 |  -0.3995 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_frontier_45_55            | 0.2067 |   1.0457 |  -0.3718 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_frontier_40_60            | 0.1982 |   1.1046 |  -0.3431 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_60_40_k_10         | 0.2371 |   1.0315 |  -0.4081 |                0.7784 |                    -0.1151 | False         |
| sp500_dynamic | a7_1_stress_60_40_k_20         | 0.2439 |   1.1840 |  -0.3617 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_60_40_k_30         | 0.2496 |   1.3570 |  -0.3123 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_10         | 0.2211 |   1.1494 |  -0.3524 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_20         | 0.2263 |   1.3305 |  -0.3025 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_30         | 0.2276 |   1.4883 |  -0.2641 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | 0.2585 |   1.3069 |  -0.3810 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | 0.2709 |   1.4981 |  -0.3438 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | 0.2536 |   1.3708 |  -0.3515 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | 0.2635 |   1.5487 |  -0.3203 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | 0.2323 |   1.3291 |  -0.3439 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | 0.2422 |   1.5145 |  -0.3138 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | 0.2308 |   1.4433 |  -0.2988 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | 0.2359 |   1.5845 |  -0.2885 |                0.7784 |                    -0.1151 | True          |

Validation gate result: PASS

## Best By Sharpe

| universe      | sleeve                         |   cagr |   sharpe |   max_dd |   equal_weight_sharpe |   trend_crisis_corr_vs_vol | passes_gate   |
|:--------------|:-------------------------------|-------:|---------:|---------:|----------------------:|---------------------------:|:--------------|
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | 0.2359 |   1.5845 |  -0.2885 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | 0.2635 |   1.5487 |  -0.3203 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | 0.2422 |   1.5145 |  -0.3138 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | 0.2709 |   1.4981 |  -0.3438 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_30         | 0.2276 |   1.4883 |  -0.2641 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | 0.2308 |   1.4433 |  -0.2988 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | 0.2536 |   1.3708 |  -0.3515 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_60_40_k_30         | 0.2496 |   1.3570 |  -0.3123 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_20         | 0.2263 |   1.3305 |  -0.3025 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | 0.2323 |   1.3291 |  -0.3439 |                0.7784 |                    -0.1151 | True          |

## Best By Drawdown

| universe      | sleeve                         |   cagr |   sharpe |   max_dd |   equal_weight_sharpe |   trend_crisis_corr_vs_vol | passes_gate   |
|:--------------|:-------------------------------|-------:|---------:|---------:|----------------------:|---------------------------:|:--------------|
| sp500_dynamic | a7_1_stress_50_50_k_30         | 0.2276 |   1.4883 |  -0.2641 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | 0.2359 |   1.5845 |  -0.2885 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | 0.2308 |   1.4433 |  -0.2988 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_50_50_k_20         | 0.2263 |   1.3305 |  -0.3025 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_stress_60_40_k_30         | 0.2496 |   1.3570 |  -0.3123 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | 0.2422 |   1.5145 |  -0.3138 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | 0.2635 |   1.5487 |  -0.3203 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_frontier_40_60            | 0.1982 |   1.1046 |  -0.3431 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | 0.2709 |   1.4981 |  -0.3438 |                0.7784 |                    -0.1151 | True          |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | 0.2323 |   1.3291 |  -0.3439 |                0.7784 |                    -0.1151 | True          |

## Crisis Correlation

| universe      | vol_sleeve   | other_sleeve          | other_type   |   crisis_correlation |   crisis_observations |
|:--------------|:-------------|:----------------------|:-------------|---------------------:|----------------------:|
| sp500_dynamic | vol_top_20   | trend_3m_6m_long_cash | trend        |              -0.1151 |                   902 |

## Period Drawdowns

| universe      | sleeve                         | period         |    cagr |   sharpe |   max_dd |
|:--------------|:-------------------------------|:---------------|--------:|---------:|---------:|
| sp500_dynamic | vol_top_20                     | gfc            |  0.1646 |   0.2247 |  -0.6176 |
| sp500_dynamic | vol_top_20                     | covid          | -0.4707 |  -0.4567 |  -0.6242 |
| sp500_dynamic | vol_top_20                     | inflation_2022 | -0.4708 |  -0.7910 |  -0.4975 |
| sp500_dynamic | vol_top_20                     | recent         |  0.7240 |   1.9595 |  -0.3764 |
| sp500_dynamic | trend_3m_6m_long_cash          | gfc            |  0.0725 |   0.6487 |  -0.1288 |
| sp500_dynamic | trend_3m_6m_long_cash          | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp500_dynamic | trend_3m_6m_long_cash          | inflation_2022 |  0.1100 |   1.0387 |  -0.0834 |
| sp500_dynamic | trend_3m_6m_long_cash          | recent         |  0.1409 |   1.6354 |  -0.0631 |
| sp500_dynamic | a7_1_frontier_60_40            | gfc            |  0.2087 |   0.4841 |  -0.3623 |
| sp500_dynamic | a7_1_frontier_60_40            | covid          | -0.1839 |  -0.2857 |  -0.4517 |
| sp500_dynamic | a7_1_frontier_60_40            | inflation_2022 | -0.2521 |  -0.7358 |  -0.3031 |
| sp500_dynamic | a7_1_frontier_60_40            | recent         |  0.4839 |   2.0744 |  -0.2439 |
| sp500_dynamic | a7_1_frontier_55_45            | gfc            |  0.2064 |   0.5238 |  -0.3264 |
| sp500_dynamic | a7_1_frontier_55_45            | covid          | -0.1481 |  -0.2485 |  -0.4261 |
| sp500_dynamic | a7_1_frontier_55_45            | inflation_2022 | -0.2226 |  -0.7145 |  -0.2759 |
| sp500_dynamic | a7_1_frontier_55_45            | recent         |  0.4543 |   2.0953 |  -0.2261 |
| sp500_dynamic | a7_1_frontier_50_50            | gfc            |  0.2023 |   0.5664 |  -0.2903 |
| sp500_dynamic | a7_1_frontier_50_50            | covid          | -0.1130 |  -0.2058 |  -0.3995 |
| sp500_dynamic | a7_1_frontier_50_50            | inflation_2022 | -0.1929 |  -0.6866 |  -0.2481 |
| sp500_dynamic | a7_1_frontier_50_50            | recent         |  0.4248 |   2.1178 |  -0.2080 |
| sp500_dynamic | a7_1_frontier_45_55            | gfc            |  0.1965 |   0.6128 |  -0.2550 |
| sp500_dynamic | a7_1_frontier_45_55            | covid          | -0.0786 |  -0.1566 |  -0.3718 |
| sp500_dynamic | a7_1_frontier_45_55            | inflation_2022 | -0.1629 |  -0.6499 |  -0.2196 |
| sp500_dynamic | a7_1_frontier_45_55            | recent         |  0.3955 |   2.1417 |  -0.1911 |
| sp500_dynamic | a7_1_frontier_40_60            | gfc            |  0.1889 |   0.6640 |  -0.2194 |
| sp500_dynamic | a7_1_frontier_40_60            | covid          | -0.0452 |  -0.0993 |  -0.3431 |
| sp500_dynamic | a7_1_frontier_40_60            | inflation_2022 | -0.1326 |  -0.6005 |  -0.1905 |
| sp500_dynamic | a7_1_frontier_40_60            | recent         |  0.3664 |   2.1663 |  -0.1743 |
| sp500_dynamic | a7_1_stress_60_40_k_10         | gfc            |  0.2197 |   0.6002 |  -0.2897 |
| sp500_dynamic | a7_1_stress_60_40_k_10         | covid          | -0.1109 |  -0.1965 |  -0.4081 |
| sp500_dynamic | a7_1_stress_60_40_k_10         | inflation_2022 | -0.2069 |  -0.6764 |  -0.2662 |
| sp500_dynamic | a7_1_stress_60_40_k_10         | recent         |  0.4774 |   2.1681 |  -0.2225 |
| sp500_dynamic | a7_1_stress_60_40_k_20         | gfc            |  0.2251 |   0.7447 |  -0.2185 |
| sp500_dynamic | a7_1_stress_60_40_k_20         | covid          | -0.0381 |  -0.0784 |  -0.3617 |
| sp500_dynamic | a7_1_stress_60_40_k_20         | inflation_2022 | -0.1603 |  -0.5938 |  -0.2287 |
| sp500_dynamic | a7_1_stress_60_40_k_20         | recent         |  0.4706 |   2.2670 |  -0.2007 |
| sp500_dynamic | a7_1_stress_60_40_k_30         | gfc            |  0.2249 |   0.9328 |  -0.1687 |
| sp500_dynamic | a7_1_stress_60_40_k_30         | covid          |  0.0334 |   0.0815 |  -0.3123 |
| sp500_dynamic | a7_1_stress_60_40_k_30         | inflation_2022 | -0.1125 |  -0.4776 |  -0.1962 |
| sp500_dynamic | a7_1_stress_60_40_k_30         | recent         |  0.4634 |   2.3702 |  -0.1799 |
| sp500_dynamic | a7_1_stress_50_50_k_10         | gfc            |  0.2070 |   0.7059 |  -0.2163 |
| sp500_dynamic | a7_1_stress_50_50_k_10         | covid          | -0.0414 |  -0.0880 |  -0.3524 |
| sp500_dynamic | a7_1_stress_50_50_k_10         | inflation_2022 | -0.1462 |  -0.5966 |  -0.2096 |
| sp500_dynamic | a7_1_stress_50_50_k_10         | recent         |  0.4179 |   2.2228 |  -0.1874 |
| sp500_dynamic | a7_1_stress_50_50_k_20         | gfc            |  0.2062 |   0.8888 |  -0.1664 |
| sp500_dynamic | a7_1_stress_50_50_k_20         | covid          |  0.0286 |   0.0726 |  -0.3025 |
| sp500_dynamic | a7_1_stress_50_50_k_20         | inflation_2022 | -0.0984 |  -0.4667 |  -0.1765 |
| sp500_dynamic | a7_1_stress_50_50_k_20         | recent         |  0.4106 |   2.3330 |  -0.1666 |
| sp500_dynamic | a7_1_stress_50_50_k_30         | gfc            |  0.1841 |   0.9753 |  -0.1349 |
| sp500_dynamic | a7_1_stress_50_50_k_30         | covid          |  0.0582 |   0.1735 |  -0.2641 |
| sp500_dynamic | a7_1_stress_50_50_k_30         | inflation_2022 | -0.0515 |  -0.2873 |  -0.1431 |
| sp500_dynamic | a7_1_stress_50_50_k_30         | recent         |  0.4029 |   2.4464 |  -0.1472 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | gfc            |  0.2250 |   0.7848 |  -0.2207 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | covid          | -0.0678 |  -0.1310 |  -0.3810 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | inflation_2022 | -0.1363 |  -0.5100 |  -0.2083 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_7 | recent         |  0.5140 |   2.7668 |  -0.1489 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | gfc            |  0.2639 |   1.0739 |  -0.1749 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | covid          | -0.0037 |  -0.0081 |  -0.3438 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | inflation_2022 | -0.1003 |  -0.4058 |  -0.1861 |
| sp500_dynamic | a7_1_hedge_60_40_k_10_beta_0_5 | recent         |  0.5149 |   2.8960 |  -0.1404 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | gfc            |  0.1879 |   0.7343 |  -0.1924 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | covid          | -0.0229 |  -0.0487 |  -0.3515 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | inflation_2022 | -0.1237 |  -0.5017 |  -0.2013 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_7 | recent         |  0.4984 |   2.7844 |  -0.1407 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | gfc            |  0.2149 |   0.9621 |  -0.1594 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | covid          |  0.0131 |   0.0314 |  -0.3203 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | inflation_2022 | -0.0877 |  -0.3859 |  -0.1734 |
| sp500_dynamic | a7_1_hedge_60_40_k_20_beta_0_5 | recent         |  0.4992 |   2.9203 |  -0.1322 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | gfc            |  0.1815 |   0.7223 |  -0.1920 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | covid          | -0.0186 |  -0.0404 |  -0.3439 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | inflation_2022 | -0.1171 |  -0.5108 |  -0.1899 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_7 | recent         |  0.4474 |   2.7374 |  -0.1325 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | gfc            |  0.2051 |   0.9351 |  -0.1593 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | covid          |  0.0230 |   0.0564 |  -0.3138 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | inflation_2022 | -0.0794 |  -0.3766 |  -0.1618 |
| sp500_dynamic | a7_1_hedge_50_50_k_10_beta_0_5 | recent         |  0.4481 |   2.8901 |  -0.1239 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | gfc            |  0.1722 |   0.7975 |  -0.1664 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | covid          |  0.0379 |   0.0965 |  -0.2988 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | inflation_2022 | -0.0915 |  -0.4469 |  -0.1733 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_7 | recent         |  0.4319 |   2.7462 |  -0.1260 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | gfc            |  0.1635 |   0.8471 |  -0.1456 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | covid          |  0.0361 |   0.0982 |  -0.2885 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | inflation_2022 | -0.0664 |  -0.3478 |  -0.1547 |
| sp500_dynamic | a7_1_hedge_50_50_k_20_beta_0_5 | recent         |  0.4327 |   2.9082 |  -0.1174 |

## Decision

At least one A.7.1 variant passed the sp500 drawdown, Sharpe, CAGR, and trend-correlation gates. Review turnover/hedge diagnostics before promotion.
