# Phase A.4 Defensive Sleeve Results

- Run date: 2026-04-29 05:14:03 UTC
- Sleeve 1 unchanged: existing `volatility_score`.
- Sleeve 2 rebuilt as `defensive_stability_score`: stability + survivability, not growth/momentum.
- Defensive sleeve tests include equal weight and beta-targeted weights.
- RL disabled.

## Goal

Create a more orthogonal alpha stream by changing the economic exposure of Sleeve 2 and controlling its beta inside the sleeve.

## Data Availability

| universe      | feature             |   coverage_pct |   ticker_coverage_pct |
|:--------------|:--------------------|---------------:|----------------------:|
| sp100_sample  | roe                 |         0.9655 |                1.0000 |
| sp100_sample  | eps_growth_yoy      |         0.9161 |                1.0000 |
| sp100_sample  | pe_ratio            |         0.9655 |                1.0000 |
| sp100_sample  | pb_ratio            |         0.9655 |                1.0000 |
| sp100_sample  | beta_to_spy_63d     |         0.9675 |                1.0000 |
| sp100_sample  | downside_vol_63d    |         0.9675 |                1.0000 |
| sp100_sample  | max_drawdown_63d    |         0.9677 |                1.0000 |
| sp100_sample  | mom_stability_3m    |         0.9877 |                1.0000 |
| sp100_sample  | debt_to_equity      |         0.0000 |                0.0000 |
| sp100_sample  | debt_to_assets      |         0.0000 |                0.0000 |
| sp100_sample  | interest_coverage   |         0.0000 |                0.0000 |
| sp100_sample  | operating_cash_flow |         0.0000 |                0.0000 |
| sp100_sample  | accruals            |         0.0000 |                0.0000 |
| sp100_sample  | gross_margin        |         0.0000 |                0.0000 |
| sp100_sample  | analyst_revisions   |         0.0000 |                0.0000 |
| sp500_dynamic | roe                 |         0.0845 |                0.0875 |
| sp500_dynamic | eps_growth_yoy      |         0.0801 |                0.0875 |
| sp500_dynamic | pe_ratio            |         0.0845 |                0.0875 |
| sp500_dynamic | pb_ratio            |         0.0845 |                0.0875 |
| sp500_dynamic | beta_to_spy_63d     |         0.9047 |                1.0000 |
| sp500_dynamic | downside_vol_63d    |         0.9047 |                1.0000 |
| sp500_dynamic | max_drawdown_63d    |         0.9049 |                1.0000 |
| sp500_dynamic | mom_stability_3m    |         0.9877 |                1.0000 |
| sp500_dynamic | debt_to_equity      |         0.0000 |                0.0000 |
| sp500_dynamic | debt_to_assets      |         0.0000 |                0.0000 |
| sp500_dynamic | interest_coverage   |         0.0000 |                0.0000 |
| sp500_dynamic | operating_cash_flow |         0.0000 |                0.0000 |
| sp500_dynamic | accruals            |         0.0000 |                0.0000 |
| sp500_dynamic | gross_margin        |         0.0000 |                0.0000 |
| sp500_dynamic | analyst_revisions   |         0.0000 |                0.0000 |

## Sleeve Metrics

| universe      | sleeve                                  | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |   target_beta |   avg_realized_beta |
|:--------------|:----------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|--------------:|--------------------:|
| sp100_sample  | vol_top_10                              | volatility    | 0.2400 |   0.7948 |  -0.5088 |       0.3019 |        81.2000 |            239 |      nan      |              1.4099 |
| sp100_sample  | vol_top_20                              | volatility    | 0.2024 |   0.8225 |  -0.4939 |       0.2460 |        59.0000 |            239 |      nan      |              1.1819 |
| sp100_sample  | defensive_stability_top_30_equal_weight | defensive     | 0.1702 |   0.9012 |  -0.4213 |       0.1889 |        49.7333 |            239 |      nan      |              0.8506 |
| sp100_sample  | defensive_stability_top_50_equal_weight | defensive     | 0.1633 |   0.8756 |  -0.3861 |       0.1865 |         1.4767 |            239 |      nan      |              0.8933 |
| sp100_sample  | defensive_stability_top_30_beta_0_6     | defensive     | 0.1315 |   0.8285 |  -0.3960 |       0.1588 |       116.7422 |            239 |        0.6000 |              0.6058 |
| sp100_sample  | defensive_stability_top_50_beta_0_6     | defensive     | 0.1264 |   0.7897 |  -0.4121 |       0.1601 |        81.6602 |            239 |        0.6000 |              0.6038 |
| sp100_sample  | defensive_stability_top_30_beta_0_8     | defensive     | 0.1540 |   0.8732 |  -0.4211 |       0.1764 |        80.1242 |            239 |        0.8000 |              0.8001 |
| sp100_sample  | defensive_stability_top_50_beta_0_8     | defensive     | 0.1468 |   0.8258 |  -0.4249 |       0.1778 |        37.0824 |            239 |        0.8000 |              0.8003 |
| sp500_dynamic | vol_top_10                              | volatility    | 0.2588 |   0.5334 |  -0.7811 |       0.4852 |       145.8000 |            239 |      nan      |              2.1534 |
| sp500_dynamic | vol_top_20                              | volatility    | 0.2661 |   0.6385 |  -0.6242 |       0.4168 |       128.1000 |            239 |      nan      |              1.9672 |
| sp500_dynamic | defensive_stability_top_30_equal_weight | defensive     | 0.0783 |   0.4578 |  -0.4874 |       0.1710 |       209.8000 |            239 |      nan      |              0.7341 |
| sp500_dynamic | defensive_stability_top_50_equal_weight | defensive     | 0.0851 |   0.4873 |  -0.4878 |       0.1746 |       172.2800 |            239 |      nan      |              0.7599 |
| sp500_dynamic | defensive_stability_top_30_beta_0_6     | defensive     | 0.0732 |   0.4707 |  -0.5214 |       0.1554 |       258.0212 |            239 |        0.6000 |              0.6029 |
| sp500_dynamic | defensive_stability_top_50_beta_0_6     | defensive     | 0.0750 |   0.4679 |  -0.4717 |       0.1602 |       222.7882 |            239 |        0.6000 |              0.6006 |
| sp500_dynamic | defensive_stability_top_30_beta_0_8     | defensive     | 0.0656 |   0.3692 |  -0.4810 |       0.1777 |       246.5942 |            239 |        0.8000 |              0.7982 |
| sp500_dynamic | defensive_stability_top_50_beta_0_8     | defensive     | 0.0827 |   0.4649 |  -0.4758 |       0.1780 |       204.1995 |            239 |        0.8000 |              0.7998 |

## Blend Metrics

| universe      | sleeve                                                         | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |   target_beta |   avg_realized_beta | vol_sleeve   | defensive_sleeve                        |   vol_weight |   defensive_weight |
|:--------------|:---------------------------------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|--------------:|--------------------:|:-------------|:----------------------------------------|-------------:|-------------------:|
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2157 |   0.8610 |  -0.4671 |       0.2505 |        65.1467 |            239 |           nan |              1.1862 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.2089 |   0.8754 |  -0.4584 |       0.2386 |        61.1333 |            239 |           nan |              1.1302 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2222 |   0.8453 |  -0.4770 |       0.2628 |        69.1600 |            239 |           nan |              1.2421 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.2019 |   0.8881 |  -0.4500 |       0.2273 |        57.1200 |            239 |           nan |              1.0743 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2122 |   0.8461 |  -0.4580 |       0.2507 |        49.3023 |            239 |           nan |              1.2033 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.2046 |   0.8569 |  -0.4451 |       0.2387 |        41.3279 |            239 |           nan |              1.1516 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2195 |   0.8342 |  -0.4708 |       0.2631 |        57.2767 |            239 |           nan |              1.2549 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1968 |   0.8663 |  -0.4322 |       0.2272 |        33.3535 |            239 |           nan |              1.1000 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2030 |   0.8820 |  -0.4404 |       0.2302 |        89.3243 |            239 |           nan |              1.0883 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1925 |   0.8983 |  -0.4261 |       0.2143 |        91.8554 |            239 |           nan |              1.0078 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2130 |   0.8622 |  -0.4556 |       0.2471 |        87.2932 |            239 |           nan |              1.1687 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1814 |   0.9093 |  -0.4127 |       0.1995 |        94.5065 |            239 |           nan |              0.9274 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.2006 |   0.8688 |  -0.4456 |       0.2309 |        76.6606 |            239 |           nan |              1.0875 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1895 |   0.8808 |  -0.4326 |       0.2151 |        76.1511 |            239 |           nan |              1.0068 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2112 |   0.8529 |  -0.4593 |       0.2476 |        77.7954 |            239 |           nan |              1.1681 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1779 |   0.8870 |  -0.4217 |       0.2005 |        75.7494 |            239 |           nan |              0.9262 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.2103 |   0.8659 |  -0.4589 |       0.2429 |        75.3023 |            239 |           nan |              1.1660 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.2019 |   0.8802 |  -0.4487 |       0.2294 |        73.9707 |            239 |           nan |              1.1050 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2183 |   0.8495 |  -0.4698 |       0.2569 |        76.7767 |            239 |           nan |              1.2269 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1933 |   0.8917 |  -0.4404 |       0.2167 |        72.7614 |            239 |           nan |              1.0440 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2068 |   0.8479 |  -0.4597 |       0.2438 |        61.4302 |            239 |           nan |              1.1661 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1976 |   0.8570 |  -0.4496 |       0.2306 |        56.5366 |            239 |           nan |              1.1051 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2156 |   0.8366 |  -0.4709 |       0.2577 |        66.3727 |            239 |           nan |              1.2270 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_10_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1881 |   0.8628 |  -0.4413 |       0.2181 |        51.7887 |            239 |           nan |              1.0441 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.1909 |   0.8650 |  -0.4585 |       0.2207 |        51.1067 |            239 |           nan |              1.0494 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.1879 |   0.8744 |  -0.4494 |       0.2148 |        49.1333 |            239 |           nan |              1.0163 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.1939 |   0.8550 |  -0.4675 |       0.2268 |        53.0800 |            239 |           nan |              1.0825 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1847 |   0.8830 |  -0.4405 |       0.2092 |        47.1600 |            239 |           nan |              0.9831 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.1875 |   0.8501 |  -0.4506 |       0.2206 |        35.9807 |            239 |           nan |              1.0665 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.1836 |   0.8561 |  -0.4393 |       0.2145 |        30.2259 |            239 |           nan |              1.0376 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.1913 |   0.8437 |  -0.4617 |       0.2268 |        41.7355 |            239 |           nan |              1.0953 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1797 |   0.8616 |  -0.4280 |       0.2086 |        24.4711 |            239 |           nan |              1.0088 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.1776 |   0.8790 |  -0.4308 |       0.2020 |        74.0184 |            239 |           nan |              0.9515 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1707 |   0.8869 |  -0.4214 |       0.1925 |        78.6102 |            239 |           nan |              0.8939 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.1842 |   0.8680 |  -0.4408 |       0.2122 |        69.5315 |            239 |           nan |              1.0091 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1636 |   0.8905 |  -0.4125 |       0.1837 |        83.2543 |            239 |           nan |              0.8362 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.1750 |   0.8633 |  -0.4367 |       0.2027 |        63.7015 |            239 |           nan |              0.9507 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1676 |   0.8667 |  -0.4288 |       0.1933 |        65.3903 |            239 |           nan |              0.8929 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.1822 |   0.8565 |  -0.4450 |       0.2128 |        62.0761 |            239 |           nan |              1.0085 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1599 |   0.8656 |  -0.4214 |       0.1847 |        67.1388 |            239 |           nan |              0.8350 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.1852 |   0.8659 |  -0.4527 |       0.2138 |        61.6566 |            239 |           nan |              1.0292 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1805 |   0.8740 |  -0.4440 |       0.2065 |        62.5806 |            239 |           nan |              0.9910 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.1897 |   0.8565 |  -0.4632 |       0.2215 |        60.8177 |            239 |           nan |              1.0674 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1757 |   0.8803 |  -0.4389 |       0.1996 |        63.5935 |            239 |           nan |              0.9528 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.1817 |   0.8459 |  -0.4540 |       0.2147 |        48.8181 |            239 |           nan |              1.0293 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1762 |   0.8485 |  -0.4459 |       0.2076 |        46.4724 |            239 |           nan |              0.9911 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.1870 |   0.8418 |  -0.4641 |       0.2222 |        51.2128 |            239 |           nan |              1.0674 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp100_sample  | blend_vol_top_20_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1706 |   0.8493 |  -0.4412 |       0.2008 |        44.1386 |            239 |           nan |              0.9530 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2055 |   0.6054 |  -0.6642 |       0.3395 |       171.4000 |            239 |           nan |              1.5857 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.1879 |   0.6160 |  -0.6312 |       0.3051 |       177.8000 |            239 |           nan |              1.4437 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2215 |   0.5907 |  -0.6959 |       0.3750 |       165.0000 |            239 |           nan |              1.7276 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1688 |   0.6203 |  -0.5971 |       0.2721 |       184.2000 |            239 |           nan |              1.3018 | vol_top_10   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2081 |   0.6092 |  -0.6628 |       0.3415 |       156.1840 |            239 |           nan |              1.5960 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.1912 |   0.6215 |  -0.6291 |       0.3076 |       158.7800 |            239 |           nan |              1.4566 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2233 |   0.5932 |  -0.6950 |       0.3765 |       153.5880 |            239 |           nan |              1.7353 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1727 |   0.6280 |  -0.5964 |       0.2751 |       161.3760 |            239 |           nan |              1.3173 | vol_top_10   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2058 |   0.6234 |  -0.6729 |       0.3301 |       190.6885 |            239 |           nan |              1.5332 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1877 |   0.6398 |  -0.6438 |       0.2934 |       201.9106 |            239 |           nan |              1.3781 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2220 |   0.6034 |  -0.7015 |       0.3679 |       179.4664 |            239 |           nan |              1.6882 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1679 |   0.6501 |  -0.6144 |       0.2583 |       213.1327 |            239 |           nan |              1.2231 | vol_top_10   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.2063 |   0.6216 |  -0.6599 |       0.3319 |       176.5473 |            239 |           nan |              1.5323 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1884 |   0.6372 |  -0.6261 |       0.2957 |       184.2341 |            239 |           nan |              1.3770 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2223 |   0.6022 |  -0.6926 |       0.3691 |       168.8604 |            239 |           nan |              1.6875 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1688 |   0.6464 |  -0.5914 |       0.2611 |       191.9209 |            239 |           nan |              1.2217 | vol_top_10   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.1991 |   0.5811 |  -0.6634 |       0.3426 |       186.1177 |            239 |           nan |              1.6113 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1802 |   0.5831 |  -0.6301 |       0.3090 |       196.1971 |            239 |           nan |              1.4758 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2165 |   0.5738 |  -0.6953 |       0.3773 |       176.0383 |            239 |           nan |              1.7468 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1598 |   0.5773 |  -0.5958 |       0.2768 |       206.2765 |            239 |           nan |              1.3403 | vol_top_10   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2065 |   0.6011 |  -0.6594 |       0.3435 |       169.0157 |            239 |           nan |              1.6120 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1893 |   0.6107 |  -0.6247 |       0.3100 |       174.8197 |            239 |           nan |              1.4766 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2221 |   0.5875 |  -0.6926 |       0.3780 |       163.2118 |            239 |           nan |              1.7473 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_10_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1707 |   0.6141 |  -0.5889 |       0.2779 |       180.6236 |            239 |           nan |              1.3412 | vol_top_10   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_60_40 | blend         | 0.2020 |   0.6682 |  -0.5500 |       0.3022 |       160.3800 |            239 |           nan |              1.4739 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_50_50 | blend         | 0.1834 |   0.6659 |  -0.5350 |       0.2755 |       168.4500 |            239 |           nan |              1.3506 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_70_30 | blend         | 0.2195 |   0.6654 |  -0.5658 |       0.3299 |       152.3100 |            239 |           nan |              1.5973 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_equal_weight_40_60 | blend         | 0.1640 |   0.6562 |  -0.5209 |       0.2499 |       176.5200 |            239 |           nan |              1.2273 | vol_top_20   | defensive_stability_top_30_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_60_40 | blend         | 0.2045 |   0.6722 |  -0.5502 |       0.3043 |       145.1640 |            239 |           nan |              1.4842 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_50_50 | blend         | 0.1867 |   0.6716 |  -0.5351 |       0.2780 |       149.4300 |            239 |           nan |              1.3635 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_70_30 | blend         | 0.2214 |   0.6680 |  -0.5660 |       0.3315 |       140.8980 |            239 |           nan |              1.6050 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_equal_weight_40_60 | blend         | 0.1680 |   0.6643 |  -0.5212 |       0.2529 |       153.6960 |            239 |           nan |              1.2428 | vol_top_20   | defensive_stability_top_50_equal_weight |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_60_40     | blend         | 0.2019 |   0.6904 |  -0.5468 |       0.2924 |       179.9222 |            239 |           nan |              1.4215 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_50_50     | blend         | 0.1829 |   0.6944 |  -0.5351 |       0.2634 |       192.8777 |            239 |           nan |              1.2850 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_70_30     | blend         | 0.2198 |   0.6815 |  -0.5628 |       0.3225 |       166.9666 |            239 |           nan |              1.5579 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_6_40_60     | blend         | 0.1628 |   0.6905 |  -0.5254 |       0.2358 |       205.8333 |            239 |           nan |              1.1486 | vol_top_20   | defensive_stability_top_30_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_60_40     | blend         | 0.2024 |   0.6872 |  -0.5380 |       0.2945 |       165.7233 |            239 |           nan |              1.4205 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_50_50     | blend         | 0.1835 |   0.6900 |  -0.5209 |       0.2660 |       175.1541 |            239 |           nan |              1.2839 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_70_30     | blend         | 0.2201 |   0.6792 |  -0.5563 |       0.3240 |       156.2924 |            239 |           nan |              1.5572 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_6_40_60     | blend         | 0.1637 |   0.6849 |  -0.5049 |       0.2390 |       184.5849 |            239 |           nan |              1.1472 | vol_top_20   | defensive_stability_top_50_beta_0_6     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_60_40     | blend         | 0.1956 |   0.6403 |  -0.5463 |       0.3055 |       175.1085 |            239 |           nan |              1.4996 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_50_50     | blend         | 0.1758 |   0.6288 |  -0.5303 |       0.2796 |       186.8745 |            239 |           nan |              1.3827 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_70_30     | blend         | 0.2146 |   0.6457 |  -0.5631 |       0.3324 |       163.3564 |            239 |           nan |              1.6165 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_30_beta_0_8_40_60     | blend         | 0.1551 |   0.6088 |  -0.5152 |       0.2548 |       198.6494 |            239 |           nan |              1.2658 | vol_top_20   | defensive_stability_top_30_beta_0_8     |       0.4000 |             0.6000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_60_40     | blend         | 0.2030 |   0.6626 |  -0.5444 |       0.3064 |       157.8295 |            239 |           nan |              1.5002 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.6000 |             0.4000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_50_50     | blend         | 0.1849 |   0.6590 |  -0.5279 |       0.2806 |       165.3523 |            239 |           nan |              1.3835 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.5000 |             0.5000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_70_30     | blend         | 0.2202 |   0.6611 |  -0.5617 |       0.3331 |       150.3472 |            239 |           nan |              1.6170 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.7000 |             0.3000 |
| sp500_dynamic | blend_vol_top_20_defensive_stability_top_50_beta_0_8_40_60     | blend         | 0.1660 |   0.6486 |  -0.5126 |       0.2559 |       172.8827 |            239 |           nan |              1.2668 | vol_top_20   | defensive_stability_top_50_beta_0_8     |       0.4000 |             0.6000 |

## Cross-Sleeve Correlation

| universe      | vol_sleeve   | defensive_sleeve                        |   full_correlation |   avg_rolling_252d_correlation |   crisis_correlation |
|:--------------|:-------------|:----------------------------------------|-------------------:|-------------------------------:|---------------------:|
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_6     |             0.7014 |                         0.6752 |               0.7520 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_8     |             0.8286 |                         0.8084 |               0.8626 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_equal_weight |             0.8849 |                         0.8481 |               0.9282 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_6     |             0.7069 |                         0.6840 |               0.7528 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_8     |             0.8376 |                         0.8253 |               0.8631 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_equal_weight |             0.9062 |                         0.8843 |               0.9346 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_6     |             0.7992 |                         0.7810 |               0.8339 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_8     |             0.9096 |                         0.8985 |               0.9311 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_equal_weight |             0.9512 |                         0.9298 |               0.9745 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_6     |             0.8043 |                         0.7895 |               0.8349 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_8     |             0.9174 |                         0.9129 |               0.9317 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_equal_weight |             0.9670 |                         0.9567 |               0.9796 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_6     |             0.5633 |                         0.5462 |               0.6447 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_8     |             0.6682 |                         0.6531 |               0.7360 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_equal_weight |             0.6500 |                         0.6277 |               0.7302 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_6     |             0.5711 |                         0.5583 |               0.6429 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_8     |             0.6807 |                         0.6705 |               0.7388 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_equal_weight |             0.6653 |                         0.6467 |               0.7389 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_6     |             0.6153 |                         0.5966 |               0.7003 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_8     |             0.7255 |                         0.7085 |               0.7970 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_equal_weight |             0.7060 |                         0.6831 |               0.7907 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_6     |             0.6270 |                         0.6107 |               0.7042 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_8     |             0.7390 |                         0.7272 |               0.8002 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_equal_weight |             0.7215 |                         0.7027 |               0.7991 |

## Overlap

| universe      | vol_sleeve   | defensive_sleeve                        |   ticker_overlap_pct |   sector_overlap_pct |   n_rebalances |
|:--------------|:-------------|:----------------------------------------|---------------------:|---------------------:|---------------:|
| sp100_sample  | vol_top_10   | defensive_stability_top_30_equal_weight |               0.5577 |               0.9986 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_equal_weight |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_6     |               0.5577 |               0.9986 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_6     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_30_beta_0_8     |               0.5577 |               0.9986 |            239 |
| sp100_sample  | vol_top_10   | defensive_stability_top_50_beta_0_8     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_equal_weight |               0.6554 |               0.9985 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_equal_weight |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_6     |               0.6554 |               0.9985 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_6     |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_30_beta_0_8     |               0.6554 |               0.9985 |            239 |
| sp100_sample  | vol_top_20   | defensive_stability_top_50_beta_0_8     |               1.0000 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_equal_weight |               0.0004 |               0.9993 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_equal_weight |               0.0021 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_6     |               0.0004 |               0.9993 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_6     |               0.0021 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_30_beta_0_8     |               0.0004 |               0.9993 |            239 |
| sp500_dynamic | vol_top_10   | defensive_stability_top_50_beta_0_8     |               0.0021 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_equal_weight |               0.0023 |               0.9982 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_equal_weight |               0.0109 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_6     |               0.0023 |               0.9982 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_6     |               0.0109 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_30_beta_0_8     |               0.0023 |               0.9982 |            239 |
| sp500_dynamic | vol_top_20   | defensive_stability_top_50_beta_0_8     |               0.0109 |               1.0000 |            239 |

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
