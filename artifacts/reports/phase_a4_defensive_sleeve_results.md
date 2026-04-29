# Phase A.4 Defensive Sleeve Results

- Run date: 2026-04-29 05:51:43 UTC
- Sleeve 1 unchanged: existing `volatility_score`.
- Sleeve 2 rebuilt as `defensive_stability_score`: stability + survivability, not growth/momentum.
- Defensive sleeve tests include equal weight and beta-targeted weights.
- RL disabled.

## Goal

Create a more orthogonal alpha stream by changing the economic exposure of Sleeve 2 and controlling its beta inside the sleeve.

## Data Availability

| universe      | feature           |   coverage_pct |   ticker_coverage_pct |
|:--------------|:------------------|---------------:|----------------------:|
| sp100_sample  | roe               |         0.9654 |                1.0000 |
| sp100_sample  | eps_growth_yoy    |         0.9160 |                1.0000 |
| sp100_sample  | pe_ratio          |         0.9654 |                1.0000 |
| sp100_sample  | pb_ratio          |         0.9654 |                1.0000 |
| sp100_sample  | debt_to_assets    |         0.9654 |                1.0000 |
| sp100_sample  | debt_to_equity    |         0.9654 |                1.0000 |
| sp100_sample  | interest_coverage |         0.9654 |                1.0000 |
| sp100_sample  | ocf_to_net_income |         0.9654 |                1.0000 |
| sp100_sample  | accruals_proxy    |         0.9654 |                1.0000 |
| sp100_sample  | gross_margin      |         0.9654 |                1.0000 |
| sp100_sample  | asset_turnover    |         0.9654 |                1.0000 |
| sp100_sample  | beta_to_spy_63d   |         0.9675 |                1.0000 |
| sp100_sample  | downside_vol_63d  |         0.9675 |                1.0000 |
| sp100_sample  | max_drawdown_63d  |         0.9677 |                1.0000 |
| sp100_sample  | mom_stability_3m  |         0.9877 |                1.0000 |
| sp100_sample  | analyst_revisions |         0.0000 |                0.0000 |
| sp500_dynamic | roe               |         0.9048 |                1.0000 |
| sp500_dynamic | eps_growth_yoy    |         0.8555 |                0.9980 |
| sp500_dynamic | pe_ratio          |         0.9048 |                1.0000 |
| sp500_dynamic | pb_ratio          |         0.9048 |                1.0000 |
| sp500_dynamic | debt_to_assets    |         0.9048 |                1.0000 |
| sp500_dynamic | debt_to_equity    |         0.9048 |                1.0000 |
| sp500_dynamic | interest_coverage |         0.9048 |                1.0000 |
| sp500_dynamic | ocf_to_net_income |         0.9048 |                1.0000 |
| sp500_dynamic | accruals_proxy    |         0.9048 |                1.0000 |
| sp500_dynamic | gross_margin      |         0.9048 |                1.0000 |
| sp500_dynamic | asset_turnover    |         0.9048 |                1.0000 |
| sp500_dynamic | beta_to_spy_63d   |         0.9047 |                1.0000 |
| sp500_dynamic | downside_vol_63d  |         0.9047 |                1.0000 |
| sp500_dynamic | max_drawdown_63d  |         0.9049 |                1.0000 |
| sp500_dynamic | mom_stability_3m  |         0.9877 |                1.0000 |
| sp500_dynamic | analyst_revisions |         0.0000 |                0.0000 |

## Sleeve Metrics

| universe      | sleeve                                  | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |   target_beta |   avg_realized_beta |
|:--------------|:----------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|--------------:|--------------------:|
| sp100_sample  | vol_top_10                              | volatility    | 0.2400 |   0.7948 |  -0.5088 |       0.3019 |        81.2000 |            239 |      nan      |              1.4099 |
| sp100_sample  | vol_top_20                              | volatility    | 0.2024 |   0.8225 |  -0.4939 |       0.2460 |        59.0000 |            239 |      nan      |              1.1819 |
| sp100_sample  | defensive_stability_top_30_equal_weight | defensive     | 0.1603 |   0.8377 |  -0.4155 |       0.1913 |        43.1333 |            239 |      nan      |              0.8717 |
| sp100_sample  | defensive_stability_top_50_equal_weight | defensive     | 0.1633 |   0.8756 |  -0.3861 |       0.1865 |         1.4767 |            239 |      nan      |              0.8933 |
| sp100_sample  | defensive_stability_top_30_beta_0_6     | defensive     | 0.1252 |   0.7813 |  -0.3908 |       0.1603 |       110.7804 |            239 |        0.6000 |              0.6054 |
| sp100_sample  | defensive_stability_top_50_beta_0_6     | defensive     | 0.1264 |   0.7897 |  -0.4121 |       0.1601 |        81.6602 |            239 |        0.6000 |              0.6038 |
| sp100_sample  | defensive_stability_top_30_beta_0_8     | defensive     | 0.1474 |   0.8252 |  -0.4149 |       0.1787 |        76.1497 |            239 |        0.8000 |              0.8001 |
| sp100_sample  | defensive_stability_top_50_beta_0_8     | defensive     | 0.1468 |   0.8258 |  -0.4249 |       0.1778 |        37.0824 |            239 |        0.8000 |              0.8003 |
| sp500_dynamic | vol_top_10                              | volatility    | 0.2588 |   0.5334 |  -0.7811 |       0.4852 |       145.8000 |            239 |      nan      |              2.1534 |
| sp500_dynamic | vol_top_20                              | volatility    | 0.2661 |   0.6385 |  -0.6242 |       0.4168 |       128.1000 |            239 |      nan      |              1.9672 |
| sp500_dynamic | defensive_stability_top_30_equal_weight | defensive     | 0.1194 |   0.6499 |  -0.4761 |       0.1838 |       152.6667 |            239 |      nan      |              0.8222 |
| sp500_dynamic | defensive_stability_top_50_equal_weight | defensive     | 0.1142 |   0.6021 |  -0.4968 |       0.1897 |       128.2400 |            239 |      nan      |              0.8479 |
| sp500_dynamic | defensive_stability_top_30_beta_0_6     | defensive     | 0.0956 |   0.6009 |  -0.4524 |       0.1591 |       205.1125 |            239 |        0.6000 |              0.6032 |
| sp500_dynamic | defensive_stability_top_50_beta_0_6     | defensive     | 0.0676 |   0.4143 |  -0.5179 |       0.1632 |       188.3928 |            239 |        0.6000 |              0.6009 |
| sp500_dynamic | defensive_stability_top_30_beta_0_8     | defensive     | 0.1034 |   0.5721 |  -0.4678 |       0.1807 |       177.2259 |            239 |        0.8000 |              0.8000 |
| sp500_dynamic | defensive_stability_top_50_beta_0_8     | defensive     | 0.0939 |   0.5149 |  -0.5013 |       0.1824 |       155.4681 |            239 |        0.8000 |              0.8000 |

## Blend Metrics

| universe      | sleeve                                                         | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |   target_beta |   avg_realized_beta | vol_sleeve   | defensive_sleeve                        |   vol_weight |   defensive_weight |
|:--------------|:---------------------------------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|--------------:|--------------------:|:-------------|:----------------------------------------|-------------:|-------------------:|
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2112 |   0.8385 |  -0.4690 |       0.2519 |        63.5733 |            239 |           nan |              1.1946 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.2034 |   0.8464 |  -0.4591 |       0.2403 |        59.1667 |            239 |           nan |              1.1408 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2188 |   0.8290 |  -0.4789 |       0.2639 |        67.9800 |            239 |           nan |              1.2484 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1953 |   0.8522 |  -0.4492 |       0.2292 |        54.7600 |            239 |           nan |              1.0870 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2122 |   0.8461 |  -0.4580 |       0.2507 |        49.3023 |            239 |           nan |              1.2033 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.2046 |   0.8569 |  -0.4451 |       0.2387 |        41.3279 |            239 |           nan |              1.1516 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2195 |   0.8342 |  -0.4708 |       0.2631 |        57.2767 |            239 |           nan |              1.2549 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1968 |   0.8663 |  -0.4322 |       0.2272 |        33.3535 |            239 |           nan |              1.1000 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2003 |   0.8683 |  -0.4423 |       0.2307 |        86.6538 |            239 |           nan |              1.0881 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1891 |   0.8799 |  -0.4284 |       0.2149 |        88.7339 |            239 |           nan |              1.0076 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2110 |   0.8526 |  -0.4570 |       0.2475 |        85.2903 |            239 |           nan |              1.1685 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1774 |   0.8854 |  -0.4162 |       0.2004 |        91.1050 |            239 |           nan |              0.9272 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.2006 |   0.8688 |  -0.4456 |       0.2309 |        76.6606 |            239 |           nan |              1.0875 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1895 |   0.8808 |  -0.4326 |       0.2151 |        76.1511 |            239 |           nan |              1.0068 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2112 |   0.8529 |  -0.4593 |       0.2476 |        77.7954 |            239 |           nan |              1.1681 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1779 |   0.8870 |  -0.4217 |       0.2005 |        75.7494 |            239 |           nan |              0.9262 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.2073 |   0.8504 |  -0.4607 |       0.2438 |        74.8070 |            239 |           nan |              1.1660 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1983 |   0.8599 |  -0.4487 |       0.2306 |        73.3168 |            239 |           nan |              1.1050 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2160 |   0.8385 |  -0.4726 |       0.2576 |        76.4052 |            239 |           nan |              1.2269 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1889 |   0.8661 |  -0.4383 |       0.2181 |        71.9380 |            239 |           nan |              1.0440 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2068 |   0.8479 |  -0.4597 |       0.2438 |        61.4302 |            239 |           nan |              1.1661 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1976 |   0.8570 |  -0.4496 |       0.2306 |        56.5366 |            239 |           nan |              1.1051 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2156 |   0.8366 |  -0.4709 |       0.2577 |        66.3727 |            239 |           nan |              1.2270 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1881 |   0.8628 |  -0.4413 |       0.2181 |        51.7887 |            239 |           nan |              1.0441 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.1867 |   0.8410 |  -0.4614 |       0.2220 |        49.2933 |            239 |           nan |              1.0578 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.1826 |   0.8439 |  -0.4530 |       0.2164 |        46.8667 |            239 |           nan |              1.0268 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.1907 |   0.8373 |  -0.4696 |       0.2278 |        51.7200 |            239 |           nan |              1.0888 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1784 |   0.8458 |  -0.4446 |       0.2109 |        44.4400 |            239 |           nan |              0.9958 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.1875 |   0.8501 |  -0.4506 |       0.2206 |        35.9807 |            239 |           nan |              1.0665 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.1836 |   0.8561 |  -0.4393 |       0.2145 |        30.2259 |            239 |           nan |              1.0376 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.1913 |   0.8437 |  -0.4617 |       0.2268 |        41.7355 |            239 |           nan |              1.0953 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1797 |   0.8616 |  -0.4280 |       0.2086 |        24.4711 |            239 |           nan |              1.0088 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.1748 |   0.8630 |  -0.4304 |       0.2026 |        72.6950 |            239 |           nan |              0.9513 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1673 |   0.8660 |  -0.4209 |       0.1932 |        76.8410 |            239 |           nan |              0.8937 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.1821 |   0.8565 |  -0.4404 |       0.2126 |        68.6618 |            239 |           nan |              1.0090 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1596 |   0.8644 |  -0.4120 |       0.1846 |        81.0388 |            239 |           nan |              0.8360 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.1750 |   0.8633 |  -0.4367 |       0.2027 |        63.7015 |            239 |           nan |              0.9507 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1676 |   0.8667 |  -0.4288 |       0.1933 |        65.3903 |            239 |           nan |              0.8929 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.1822 |   0.8565 |  -0.4450 |       0.2128 |        62.0761 |            239 |           nan |              1.0085 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1599 |   0.8656 |  -0.4214 |       0.1847 |        67.1388 |            239 |           nan |              0.8350 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.1823 |   0.8489 |  -0.4543 |       0.2147 |        61.0986 |            239 |           nan |              1.0292 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1769 |   0.8520 |  -0.4443 |       0.2077 |        61.9443 |            239 |           nan |              0.9910 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.1875 |   0.8442 |  -0.4643 |       0.2221 |        60.3306 |            239 |           nan |              1.0674 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1715 |   0.8532 |  -0.4352 |       0.2010 |        62.7960 |            239 |           nan |              0.9528 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.1817 |   0.8459 |  -0.4540 |       0.2147 |        48.8181 |            239 |           nan |              1.0293 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1762 |   0.8485 |  -0.4459 |       0.2076 |        46.4724 |            239 |           nan |              0.9911 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.1870 |   0.8418 |  -0.4641 |       0.2222 |        51.2128 |            239 |           nan |              1.0674 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1706 |   0.8493 |  -0.4412 |       0.2008 |        44.1386 |            239 |           nan |              0.9530 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2219 |   0.6402 |  -0.6576 |       0.3466 |       147.8533 |            239 |           nan |              1.6209 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.2086 |   0.6643 |  -0.6232 |       0.3139 |       148.3667 |            239 |           nan |              1.4878 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2337 |   0.6144 |  -0.6916 |       0.3803 |       147.3400 |            239 |           nan |              1.7540 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1936 |   0.6853 |  -0.5922 |       0.2826 |       148.8800 |            239 |           nan |              1.3546 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2187 |   0.6250 |  -0.6645 |       0.3500 |       138.1520 |            239 |           nan |              1.6312 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.2048 |   0.6439 |  -0.6326 |       0.3181 |       136.2400 |            239 |           nan |              1.5006 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2312 |   0.6038 |  -0.6964 |       0.3828 |       140.0640 |            239 |           nan |              1.7617 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1894 |   0.6590 |  -0.6041 |       0.2874 |       134.3280 |            239 |           nan |              1.3701 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2157 |   0.6511 |  -0.6534 |       0.3313 |       169.1685 |            239 |           nan |              1.5333 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.2000 |   0.6780 |  -0.6174 |       0.2949 |       175.0107 |            239 |           nan |              1.3783 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2295 |   0.6224 |  -0.6880 |       0.3687 |       163.3264 |            239 |           nan |              1.6883 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1824 |   0.7010 |  -0.5803 |       0.2602 |       180.8560 |            239 |           nan |              1.2233 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.2027 |   0.6085 |  -0.6727 |       0.3331 |       162.5246 |            239 |           nan |              1.5324 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1841 |   0.6191 |  -0.6436 |       0.2973 |       166.7057 |            239 |           nan |              1.3771 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2196 |   0.5933 |  -0.7012 |       0.3701 |       158.3434 |            239 |           nan |              1.6876 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1638 |   0.6224 |  -0.6143 |       0.2631 |       170.8940 |            239 |           nan |              1.2219 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.2154 |   0.6248 |  -0.6542 |       0.3447 |       157.6428 |            239 |           nan |              1.6120 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.2004 |   0.6431 |  -0.6175 |       0.3116 |       160.6270 |            239 |           nan |              1.4767 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2288 |   0.6039 |  -0.6891 |       0.3789 |       154.6821 |            239 |           nan |              1.7474 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1838 |   0.6569 |  -0.5834 |       0.2798 |       163.7020 |            239 |           nan |              1.3413 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2110 |   0.6103 |  -0.6676 |       0.3457 |       148.7912 |            239 |           nan |              1.6120 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1950 |   0.6234 |  -0.6358 |       0.3128 |       149.5649 |            239 |           nan |              1.4767 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2254 |   0.5938 |  -0.6982 |       0.3796 |       148.0434 |            239 |           nan |              1.7474 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1775 |   0.6311 |  -0.6031 |       0.2812 |       150.4218 |            239 |           nan |              1.3413 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2186 |   0.7065 |  -0.5468 |       0.3095 |       136.4867 |            239 |           nan |              1.5092 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.2043 |   0.7184 |  -0.5309 |       0.2844 |       138.5833 |            239 |           nan |              1.3947 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2320 |   0.6917 |  -0.5637 |       0.3354 |       134.3900 |            239 |           nan |              1.6237 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1891 |   0.7262 |  -0.5159 |       0.2604 |       140.6800 |            239 |           nan |              1.2802 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2156 |   0.6892 |  -0.5564 |       0.3128 |       126.6200 |            239 |           nan |              1.5195 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.2007 |   0.6958 |  -0.5427 |       0.2885 |       126.2500 |            239 |           nan |              1.4075 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2296 |   0.6794 |  -0.5708 |       0.3380 |       126.9900 |            239 |           nan |              1.6314 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1850 |   0.6977 |  -0.5298 |       0.2652 |       125.8800 |            239 |           nan |              1.2956 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2118 |   0.7208 |  -0.5305 |       0.2938 |       158.1680 |            239 |           nan |              1.4216 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1951 |   0.7357 |  -0.5113 |       0.2652 |       165.7099 |            239 |           nan |              1.2852 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2273 |   0.7025 |  -0.5510 |       0.3235 |       150.6260 |            239 |           nan |              1.5580 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1773 |   0.7448 |  -0.4934 |       0.2380 |       173.2708 |            239 |           nan |              1.1488 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.1989 |   0.6723 |  -0.5479 |       0.2958 |       151.3084 |            239 |           nan |              1.4207 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1793 |   0.6698 |  -0.5352 |       0.2677 |       157.1355 |            239 |           nan |              1.2840 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2174 |   0.6689 |  -0.5636 |       0.3250 |       145.4823 |            239 |           nan |              1.5573 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1587 |   0.6585 |  -0.5251 |       0.2411 |       162.9626 |            239 |           nan |              1.1474 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.2120 |   0.6889 |  -0.5400 |       0.3077 |       146.3786 |            239 |           nan |              1.5003 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1960 |   0.6946 |  -0.5227 |       0.2822 |       151.0216 |            239 |           nan |              1.3836 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2270 |   0.6795 |  -0.5583 |       0.3341 |       141.7906 |            239 |           nan |              1.6170 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1792 |   0.6949 |  -0.5069 |       0.2578 |       155.6802 |            239 |           nan |              1.2669 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2076 |   0.6724 |  -0.5532 |       0.3087 |       137.4162 |            239 |           nan |              1.5003 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1906 |   0.6726 |  -0.5397 |       0.2834 |       139.7952 |            239 |           nan |              1.3836 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2236 |   0.6679 |  -0.5679 |       0.3349 |       135.0637 |            239 |           nan |              1.6170 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1729 |   0.6667 |  -0.5274 |       0.2593 |       142.1743 |            239 |           nan |              1.2669 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |

## Cross-Sleeve Correlation

| universe      | vol_sleeve   | defensive_sleeve                        |   full_correlation |   avg_rolling_252d_correlation |   crisis_correlation |
|:--------------|:-------------|:----------------------------------------|-------------------:|-------------------------------:|---------------------:|
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_6     |             0.7021 |                         0.6689 |               0.7552 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_8     |             0.8308 |                         0.8147 |               0.8606 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_equal_weight |             0.8939 |                         0.8668 |               0.9280 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_6     |             0.7069 |                         0.6840 |               0.7528 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_8     |             0.8376 |                         0.8253 |               0.8631 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_equal_weight |             0.9062 |                         0.8843 |               0.9346 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_6     |             0.7995 |                         0.7769 |               0.8359 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_8     |             0.9106 |                         0.9018 |               0.9294 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_equal_weight |             0.9571 |                         0.9411 |               0.9749 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_6     |             0.8043 |                         0.7895 |               0.8349 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_8     |             0.9174 |                         0.9129 |               0.9317 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_equal_weight |             0.9670 |                         0.9567 |               0.9796 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_6     |             0.5655 |                         0.5660 |               0.6104 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_8     |             0.6866 |                         0.6831 |               0.7267 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_equal_weight |             0.7014 |                         0.6890 |               0.7591 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_6     |             0.5790 |                         0.5756 |               0.6242 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_8     |             0.6938 |                         0.6915 |               0.7297 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_equal_weight |             0.7245 |                         0.7103 |               0.7821 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_6     |             0.6204 |                         0.6161 |               0.6705 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_8     |             0.7446 |                         0.7382 |               0.7879 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_equal_weight |             0.7569 |                         0.7452 |               0.8176 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_6     |             0.6354 |                         0.6286 |               0.6846 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_8     |             0.7529 |                         0.7477 |               0.7922 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_equal_weight |             0.7795 |                         0.7666 |               0.8394 |

## Overlap

| universe      | vol_sleeve   | defensive_sleeve                        |   ticker_overlap_pct |   sector_overlap_pct |   n_rebalances |
|:--------------|:-------------|:----------------------------------------|---------------------:|---------------------:|---------------:|
| sp100_sample  | vol_top_10   | defensive_stability_top_30_equal_weight |               0.6623 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_equal_weight |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_6     |               0.6623 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_6     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_8     |               0.6623 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_8     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_equal_weight |               0.6914 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_equal_weight |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_6     |               0.6914 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_6     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_8     |               0.6914 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_8     |               1.0000 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_equal_weight |               0.0192 |               0.9985 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_equal_weight |               0.0481 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_6     |               0.0192 |               0.9985 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_6     |               0.0481 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_8     |               0.0192 |               0.9985 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_8     |               0.0481 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_equal_weight |               0.0238 |               0.9988 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_equal_weight |               0.0575 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_6     |               0.0238 |               0.9988 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_6     |               0.0575 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_8     |               0.0238 |               0.9988 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_8     |               0.0575 |               1.0000 |            239 |

## Benchmarks

| universe      | benchmark                   |   cagr |   sharpe |   max_dd |   volatility |
|:--------------|:----------------------------|-------:|---------:|---------:|-------------:|
| sp100_sample  | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |
| sp100_sample  | equal_weight_universe_daily | 0.1620 |   0.8302 |  -0.4318 |       0.1952 |
| sp500_dynamic | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |
| sp500_dynamic | equal_weight_universe_daily | 0.1649 |   0.7787 |  -0.4912 |       0.2117 |

## Success Criteria

- sp500 CAGR >= equal-weight, Sharpe > equal-weight, MaxDD < 40%: FAIL
- sp500 vol-defensive full corr < 0.5 and crisis corr < 0.6: FAIL
- No sp500 blend met all hard gates.

## Implementation Notes

- The score intentionally avoids positive growth and momentum as primary drivers.
- True balance-sheet debt, cash-flow accruals, margins, and analyst revisions are unavailable in the current cached feature set.
- Beta targeting is applied inside the defensive sleeve after sector-balanced selection.
