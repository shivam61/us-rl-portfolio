# Multi-Sleeve Alpha Results

- Run date: 2026-04-29 03:19:00 UTC
- Sleeve 1 unchanged: existing `volatility_score`.
- Sleeve 2 independent: defensive `quality_score`.
- RL disabled.
- Scores are not merged into one model; sleeves are selected and blended as separate portfolios.

## Goal

Test whether strong but risky volatility alpha plus weaker defensive quality alpha can become an investable non-RL system.

## Sleeve Metrics

| universe      | sleeve                         | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances |
|:--------------|:-------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|
| sp100_sample  | vol_top_10                     | volatility    | 0.2400 |   0.7948 |  -0.5088 |       0.3019 |        81.2000 |            239 |
| sp100_sample  | vol_top_20                     | volatility    | 0.2024 |   0.8225 |  -0.4939 |       0.2460 |        59.0000 |            239 |
| sp100_sample  | quality_sector_balanced_top_30 | quality       | 0.1682 |   0.8973 |  -0.3943 |       0.1875 |        47.1333 |            239 |
| sp100_sample  | quality_sector_balanced_top_50 | quality       | 0.1633 |   0.8756 |  -0.3861 |       0.1865 |         1.4767 |            239 |
| sp500_dynamic | vol_top_10                     | volatility    | 0.2588 |   0.5334 |  -0.7811 |       0.4852 |       145.8000 |            239 |
| sp500_dynamic | vol_top_20                     | volatility    | 0.2661 |   0.6385 |  -0.6242 |       0.4168 |       128.1000 |            239 |
| sp500_dynamic | quality_sector_balanced_top_30 | quality       | 0.0916 |   0.5287 |  -0.4843 |       0.1733 |       188.2667 |            239 |
| sp500_dynamic | quality_sector_balanced_top_50 | quality       | 0.0982 |   0.5555 |  -0.4842 |       0.1769 |       152.3200 |            239 |

## Blend Metrics

| universe      | sleeve                                                | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   n_rebalances | vol_sleeve   | quality_sleeve                 |   vol_weight |   quality_weight |
|:--------------|:------------------------------------------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|---------------:|:-------------|:-------------------------------|-------------:|-----------------:|
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_30_60_40 | blend         | 0.2150 |   0.8616 |  -0.4625 |       0.2495 |        64.0533 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.6000 |           0.4000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_30_50_50 | blend         | 0.2080 |   0.8760 |  -0.4509 |       0.2375 |        59.7667 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.5000 |           0.5000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_30_70_30 | blend         | 0.2217 |   0.8459 |  -0.4741 |       0.2621 |        68.3400 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.7000 |           0.3000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_30_40_60 | blend         | 0.2008 |   0.8885 |  -0.4392 |       0.2260 |        55.4800 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.4000 |           0.6000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_50_60_40 | blend         | 0.2122 |   0.8461 |  -0.4580 |       0.2507 |        49.3023 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.6000 |           0.4000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_50_50_50 | blend         | 0.2046 |   0.8569 |  -0.4451 |       0.2387 |        41.3279 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.5000 |           0.5000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_50_70_30 | blend         | 0.2195 |   0.8342 |  -0.4708 |       0.2631 |        57.2767 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.7000 |           0.3000 |
| sp100_sample  | blend_vol_top_10_quality_sector_balanced_top_50_40_60 | blend         | 0.1968 |   0.8663 |  -0.4322 |       0.2272 |        33.3535 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.4000 |           0.6000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_30_60_40 | blend         | 0.1902 |   0.8648 |  -0.4544 |       0.2200 |        49.6400 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.6000 |           0.4000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_30_50_50 | blend         | 0.1870 |   0.8740 |  -0.4443 |       0.2139 |        47.3000 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.5000 |           0.5000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_30_70_30 | blend         | 0.1934 |   0.8549 |  -0.4645 |       0.2262 |        51.9800 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.7000 |           0.3000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_30_40_60 | blend         | 0.1836 |   0.8823 |  -0.4343 |       0.2081 |        44.9600 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.4000 |           0.6000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_50_60_40 | blend         | 0.1875 |   0.8501 |  -0.4506 |       0.2206 |        35.9807 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.6000 |           0.4000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_50_50_50 | blend         | 0.1836 |   0.8561 |  -0.4393 |       0.2145 |        30.2259 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.5000 |           0.5000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_50_70_30 | blend         | 0.1913 |   0.8437 |  -0.4617 |       0.2268 |        41.7355 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.7000 |           0.3000 |
| sp100_sample  | blend_vol_top_20_quality_sector_balanced_top_50_40_60 | blend         | 0.1797 |   0.8616 |  -0.4280 |       0.2086 |        24.4711 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.4000 |           0.6000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_30_60_40 | blend         | 0.2118 |   0.6243 |  -0.6659 |       0.3392 |       162.6533 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.6000 |           0.4000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_30_50_50 | blend         | 0.1956 |   0.6416 |  -0.6336 |       0.3049 |       166.8667 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.5000 |           0.5000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_30_70_30 | blend         | 0.2263 |   0.6039 |  -0.6971 |       0.3747 |       158.4400 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.7000 |           0.3000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_30_40_60 | blend         | 0.1778 |   0.6535 |  -0.6001 |       0.2721 |       171.0800 |            239 | vol_top_10   | quality_sector_balanced_top_30 |       0.4000 |           0.6000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_50_60_40 | blend         | 0.2141 |   0.6272 |  -0.6655 |       0.3414 |       148.2000 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.6000 |           0.4000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_50_50_50 | blend         | 0.1986 |   0.6457 |  -0.6328 |       0.3076 |       148.8000 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.5000 |           0.5000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_50_70_30 | blend         | 0.2280 |   0.6058 |  -0.6968 |       0.3763 |       147.6000 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.7000 |           0.3000 |
| sp500_dynamic | blend_vol_top_10_quality_sector_balanced_top_50_40_60 | blend         | 0.1815 |   0.6594 |  -0.5989 |       0.2752 |       149.4000 |            239 | vol_top_10   | quality_sector_balanced_top_50 |       0.4000 |           0.6000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_30_60_40 | blend         | 0.2082 |   0.6894 |  -0.5477 |       0.3020 |       151.6333 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.6000 |           0.4000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_30_50_50 | blend         | 0.1910 |   0.6940 |  -0.5319 |       0.2753 |       157.5167 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.5000 |           0.5000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_30_70_30 | blend         | 0.2243 |   0.6804 |  -0.5641 |       0.3297 |       145.7500 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.7000 |           0.3000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_30_40_60 | blend         | 0.1729 |   0.6919 |  -0.5171 |       0.2499 |       163.4000 |            239 | vol_top_20   | quality_sector_balanced_top_30 |       0.4000 |           0.6000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_50_60_40 | blend         | 0.2106 |   0.6922 |  -0.5503 |       0.3042 |       136.9720 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.6000 |           0.4000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_50_50_50 | blend         | 0.1941 |   0.6982 |  -0.5353 |       0.2781 |       139.1900 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.5000 |           0.5000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_50_70_30 | blend         | 0.2261 |   0.6822 |  -0.5661 |       0.3314 |       134.7540 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.7000 |           0.3000 |
| sp500_dynamic | blend_vol_top_20_quality_sector_balanced_top_50_40_60 | blend         | 0.1767 |   0.6981 |  -0.5211 |       0.2531 |       141.4080 |            239 | vol_top_20   | quality_sector_balanced_top_50 |       0.4000 |           0.6000 |

## Cross-Sleeve Correlation

| universe      | vol_sleeve   | quality_sleeve                 |   full_correlation |   avg_rolling_252d_correlation |   crisis_correlation |
|:--------------|:-------------|:-------------------------------|-------------------:|-------------------------------:|---------------------:|
| sp100_sample  | vol_top_10   | quality_sector_balanced_top_30 |             0.8770 |                         0.8409 |               0.9224 |
| sp100_sample  | vol_top_10   | quality_sector_balanced_top_50 |             0.9062 |                         0.8843 |               0.9346 |
| sp100_sample  | vol_top_20   | quality_sector_balanced_top_30 |             0.9473 |                         0.9252 |               0.9729 |
| sp100_sample  | vol_top_20   | quality_sector_balanced_top_50 |             0.9670 |                         0.9567 |               0.9796 |
| sp500_dynamic | vol_top_10   | quality_sector_balanced_top_30 |             0.6333 |                         0.6118 |               0.7278 |
| sp500_dynamic | vol_top_10   | quality_sector_balanced_top_50 |             0.6517 |                         0.6321 |               0.7373 |
| sp500_dynamic | vol_top_20   | quality_sector_balanced_top_30 |             0.6882 |                         0.6654 |               0.7900 |
| sp500_dynamic | vol_top_20   | quality_sector_balanced_top_50 |             0.7075 |                         0.6881 |               0.7985 |

## Overlap

| universe      | vol_sleeve   | quality_sleeve                 |   ticker_overlap_pct |   sector_overlap_pct |   n_rebalances |
|:--------------|:-------------|:-------------------------------|---------------------:|---------------------:|---------------:|
| sp100_sample  | vol_top_10   | quality_sector_balanced_top_30 |               0.5176 |               0.9972 |            239 |
| sp100_sample  | vol_top_10   | quality_sector_balanced_top_50 |               1.0000 |               1.0000 |            239 |
| sp100_sample  | vol_top_20   | quality_sector_balanced_top_30 |               0.6333 |               0.9981 |            239 |
| sp100_sample  | vol_top_20   | quality_sector_balanced_top_50 |               1.0000 |               1.0000 |            239 |
| sp500_dynamic | vol_top_10   | quality_sector_balanced_top_30 |               0.0004 |               0.9980 |            239 |
| sp500_dynamic | vol_top_10   | quality_sector_balanced_top_50 |               0.0054 |               1.0000 |            239 |
| sp500_dynamic | vol_top_20   | quality_sector_balanced_top_30 |               0.0050 |               0.9974 |            239 |
| sp500_dynamic | vol_top_20   | quality_sector_balanced_top_50 |               0.0157 |               0.9994 |            239 |

## Benchmarks

| universe      | benchmark                   |   cagr |   sharpe |   max_dd |   volatility |
|:--------------|:----------------------------|-------:|---------:|---------:|-------------:|
| sp100_sample  | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |
| sp100_sample  | equal_weight_universe_daily | 0.1620 |   0.8302 |  -0.4318 |       0.1952 |
| sp500_dynamic | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |       0.1987 |
| sp500_dynamic | equal_weight_universe_daily | 0.1649 |   0.7787 |  -0.4912 |       0.2117 |

## Success Criteria

- sp500 CAGR >= equal-weight, Sharpe > equal-weight, MaxDD < 40%: FAIL
- sp500 vol-quality full correlation < 0.5: FAIL
- No sp500 blend met all hard gates.

## Implementation Notes

- `low_leverage_proxy` uses low `pb_ratio` because true debt/leverage is not currently available in cached fundamentals.
- Defensive quality is intentionally an independent sleeve; it is not merged into `volatility_score`.
