# Phase A.7 Trend Overlay Results

- Run date: 2026-04-29 17:37:04 UTC
- Objective: introduce a true orthogonal hedge/trend sleeve for the volatility alpha.
- `volatility_score` is unchanged.
- Quality sleeve is not revisited.
- RL disabled.
- Trend assets available: `GLD, SPY, TLT, UUP`

## Standalone Metrics

| universe      | sleeve                 | sleeve_type   |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   avg_gross |   max_gross |   n_rebalances |
|:--------------|:-----------------------|:--------------|-------:|---------:|---------:|-------------:|---------------:|------------:|------------:|---------------:|
| sp100_sample  | vol_top_10             | volatility    | 0.2429 |   0.8060 |  -0.5221 |       0.3013 |        80.8000 |      0.9993 |      1.0000 |            239 |
| sp100_sample  | vol_top_20             | volatility    | 0.2028 |   0.8252 |  -0.4939 |       0.2458 |        59.5000 |      0.9993 |      1.0000 |            239 |
| sp100_sample  | trend_3m_long_cash     | trend         | 0.1006 |   1.0558 |  -0.2048 |       0.0953 |       135.9194 |      1.2360 |      1.5000 |            239 |
| sp100_sample  | trend_6m_long_cash     | trend         | 0.0937 |   0.9791 |  -0.1481 |       0.0957 |       104.3861 |      1.2405 |      1.5000 |            239 |
| sp100_sample  | trend_3m_6m_long_cash  | trend         | 0.1144 |   1.1862 |  -0.1456 |       0.0964 |       110.8484 |      1.2442 |      1.5000 |            239 |
| sp100_sample  | trend_3m_long_short    | trend         | 0.0564 |   0.6006 |  -0.2606 |       0.0939 |       157.7167 |      1.3649 |      1.5000 |            239 |
| sp100_sample  | trend_6m_long_short    | trend         | 0.0478 |   0.5215 |  -0.1443 |       0.0917 |       116.9193 |      1.3622 |      1.5000 |            239 |
| sp100_sample  | trend_3m_6m_long_short | trend         | 0.0719 |   0.7733 |  -0.1835 |       0.0930 |       122.1199 |      1.3695 |      1.5000 |            239 |
| sp500_dynamic | vol_top_10             | volatility    | 0.2603 |   0.5364 |  -0.7811 |       0.4852 |       145.8000 |      0.9993 |      1.0000 |            239 |
| sp500_dynamic | vol_top_20             | volatility    | 0.2664 |   0.6392 |  -0.6242 |       0.4167 |       128.0000 |      0.9993 |      1.0000 |            239 |
| sp500_dynamic | trend_3m_long_cash     | trend         | 0.1006 |   1.0558 |  -0.2048 |       0.0953 |       135.9194 |      1.2360 |      1.5000 |            239 |
| sp500_dynamic | trend_6m_long_cash     | trend         | 0.0937 |   0.9791 |  -0.1481 |       0.0957 |       104.3861 |      1.2405 |      1.5000 |            239 |
| sp500_dynamic | trend_3m_6m_long_cash  | trend         | 0.1144 |   1.1862 |  -0.1456 |       0.0964 |       110.8484 |      1.2442 |      1.5000 |            239 |
| sp500_dynamic | trend_3m_long_short    | trend         | 0.0564 |   0.6006 |  -0.2606 |       0.0939 |       157.7167 |      1.3649 |      1.5000 |            239 |
| sp500_dynamic | trend_6m_long_short    | trend         | 0.0478 |   0.5215 |  -0.1443 |       0.0917 |       116.9193 |      1.3622 |      1.5000 |            239 |
| sp500_dynamic | trend_3m_6m_long_short | trend         | 0.0719 |   0.7733 |  -0.1835 |       0.0930 |       122.1199 |      1.3695 |      1.5000 |            239 |

## Blend Metrics

| universe      | sleeve                                        | sleeve_type   | vol_sleeve   | trend_sleeve           |   vol_weight |   trend_weight |   cagr |   sharpe |   max_dd |   volatility |
|:--------------|:----------------------------------------------|:--------------|:-------------|:-----------------------|-------------:|---------------:|-------:|---------:|---------:|-------------:|
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | blend         | vol_top_10   | trend_3m_long_cash     |       0.8000 |         0.2000 | 0.2316 |   0.9533 |  -0.4252 |       0.2430 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | blend         | vol_top_10   | trend_3m_long_cash     |       0.7000 |         0.3000 | 0.2202 |   1.0262 |  -0.3728 |       0.2146 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | blend         | vol_top_10   | trend_3m_long_cash     |       0.6000 |         0.4000 | 0.2078 |   1.1107 |  -0.3201 |       0.1871 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | blend         | vol_top_10   | trend_6m_long_cash     |       0.8000 |         0.2000 | 0.2293 |   0.9407 |  -0.4225 |       0.2437 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | blend         | vol_top_10   | trend_6m_long_cash     |       0.7000 |         0.3000 | 0.2167 |   1.0049 |  -0.3685 |       0.2157 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | blend         | vol_top_10   | trend_6m_long_cash     |       0.6000 |         0.4000 | 0.2032 |   1.0782 |  -0.3201 |       0.1885 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.8000 |         0.2000 | 0.2342 |   0.9633 |  -0.4231 |       0.2431 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.7000 |         0.3000 | 0.2240 |   1.0429 |  -0.3695 |       0.2148 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.6000 |         0.4000 | 0.2128 |   1.1357 |  -0.3201 |       0.1874 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | blend         | vol_top_10   | trend_3m_long_short    |       0.8000 |         0.2000 | 0.2228 |   0.9274 |  -0.4226 |       0.2402 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | blend         | vol_top_10   | trend_3m_long_short    |       0.7000 |         0.3000 | 0.2070 |   0.9834 |  -0.3687 |       0.2105 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | blend         | vol_top_10   | trend_3m_long_short    |       0.6000 |         0.4000 | 0.1901 |   1.0471 |  -0.3137 |       0.1816 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | blend         | vol_top_10   | trend_6m_long_short    |       0.8000 |         0.2000 | 0.2197 |   0.9108 |  -0.4187 |       0.2412 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | blend         | vol_top_10   | trend_6m_long_short    |       0.7000 |         0.3000 | 0.2024 |   0.9554 |  -0.3625 |       0.2119 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | blend         | vol_top_10   | trend_6m_long_short    |       0.6000 |         0.4000 | 0.1842 |   1.0047 |  -0.3137 |       0.1833 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.8000 |         0.2000 | 0.2255 |   0.9372 |  -0.4199 |       0.2406 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.7000 |         0.3000 | 0.2110 |   0.9999 |  -0.3644 |       0.2110 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.6000 |         0.4000 | 0.1955 |   1.0723 |  -0.3137 |       0.1823 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | blend         | vol_top_20   | trend_3m_long_cash     |       0.8000 |         0.2000 | 0.1952 |   0.9814 |  -0.4002 |       0.1989 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | blend         | vol_top_20   | trend_3m_long_cash     |       0.7000 |         0.3000 | 0.1874 |   1.0617 |  -0.3505 |       0.1765 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | blend         | vol_top_20   | trend_3m_long_cash     |       0.6000 |         0.4000 | 0.1788 |   1.1532 |  -0.2982 |       0.1550 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | blend         | vol_top_20   | trend_6m_long_cash     |       0.8000 |         0.2000 | 0.1929 |   0.9658 |  -0.3985 |       0.1998 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | blend         | vol_top_20   | trend_6m_long_cash     |       0.7000 |         0.3000 | 0.1840 |   1.0353 |  -0.3479 |       0.1777 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | blend         | vol_top_20   | trend_6m_long_cash     |       0.6000 |         0.4000 | 0.1743 |   1.1130 |  -0.2945 |       0.1566 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.8000 |         0.2000 | 0.1977 |   0.9927 |  -0.3992 |       0.1992 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.7000 |         0.3000 | 0.1910 |   1.0804 |  -0.3489 |       0.1768 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.6000 |         0.4000 | 0.1836 |   1.1809 |  -0.2961 |       0.1555 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | blend         | vol_top_20   | trend_3m_long_short    |       0.8000 |         0.2000 | 0.1866 |   0.9522 |  -0.3967 |       0.1959 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | blend         | vol_top_20   | trend_3m_long_short    |       0.7000 |         0.3000 | 0.1744 |   1.0138 |  -0.3446 |       0.1720 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | blend         | vol_top_20   | trend_3m_long_short    |       0.6000 |         0.4000 | 0.1614 |   1.0827 |  -0.2900 |       0.1491 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | blend         | vol_top_20   | trend_6m_long_short    |       0.8000 |         0.2000 | 0.1836 |   0.9317 |  -0.3951 |       0.1970 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | blend         | vol_top_20   | trend_6m_long_short    |       0.7000 |         0.3000 | 0.1699 |   0.9792 |  -0.3415 |       0.1736 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | blend         | vol_top_20   | trend_6m_long_short    |       0.6000 |         0.4000 | 0.1557 |   1.0304 |  -0.2849 |       0.1511 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.8000 |         0.2000 | 0.1892 |   0.9631 |  -0.3957 |       0.1965 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.7000 |         0.3000 | 0.1783 |   1.0321 |  -0.3426 |       0.1727 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.6000 |         0.4000 | 0.1666 |   1.1105 |  -0.2872 |       0.1501 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | blend         | vol_top_10   | trend_3m_long_cash     |       0.8000 |         0.2000 | 0.2652 |   0.6809 |  -0.6659 |       0.3895 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | blend         | vol_top_10   | trend_3m_long_cash     |       0.7000 |         0.3000 | 0.2556 |   0.7470 |  -0.5974 |       0.3422 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | blend         | vol_top_10   | trend_3m_long_cash     |       0.6000 |         0.4000 | 0.2430 |   0.8230 |  -0.5201 |       0.2953 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | blend         | vol_top_10   | trend_6m_long_cash     |       0.8000 |         0.2000 | 0.2628 |   0.6739 |  -0.6651 |       0.3900 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | blend         | vol_top_10   | trend_6m_long_cash     |       0.7000 |         0.3000 | 0.2520 |   0.7351 |  -0.5961 |       0.3428 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | blend         | vol_top_10   | trend_6m_long_cash     |       0.6000 |         0.4000 | 0.2384 |   0.8048 |  -0.5182 |       0.2962 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.8000 |         0.2000 | 0.2679 |   0.6878 |  -0.6651 |       0.3895 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.7000 |         0.3000 | 0.2596 |   0.7587 |  -0.5961 |       0.3421 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend         | vol_top_10   | trend_3m_6m_long_cash  |       0.6000 |         0.4000 | 0.2483 |   0.8408 |  -0.5183 |       0.2953 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | blend         | vol_top_10   | trend_3m_long_short    |       0.8000 |         0.2000 | 0.2565 |   0.6625 |  -0.6639 |       0.3872 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | blend         | vol_top_10   | trend_3m_long_short    |       0.7000 |         0.3000 | 0.2424 |   0.7159 |  -0.5939 |       0.3386 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | blend         | vol_top_10   | trend_3m_long_short    |       0.6000 |         0.4000 | 0.2254 |   0.7757 |  -0.5149 |       0.2905 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | blend         | vol_top_10   | trend_6m_long_short    |       0.8000 |         0.2000 | 0.2532 |   0.6531 |  -0.6628 |       0.3878 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | blend         | vol_top_10   | trend_6m_long_short    |       0.7000 |         0.3000 | 0.2377 |   0.7001 |  -0.5920 |       0.3395 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | blend         | vol_top_10   | trend_6m_long_short    |       0.6000 |         0.4000 | 0.2192 |   0.7517 |  -0.5122 |       0.2917 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.8000 |         0.2000 | 0.2593 |   0.6694 |  -0.6627 |       0.3874 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.7000 |         0.3000 | 0.2466 |   0.7276 |  -0.5919 |       0.3389 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend         | vol_top_10   | trend_3m_6m_long_short |       0.6000 |         0.4000 | 0.2309 |   0.7937 |  -0.5120 |       0.2909 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | blend         | vol_top_20   | trend_3m_long_cash     |       0.8000 |         0.2000 | 0.2623 |   0.7829 |  -0.5440 |       0.3350 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | blend         | vol_top_20   | trend_3m_long_cash     |       0.7000 |         0.3000 | 0.2504 |   0.8493 |  -0.4993 |       0.2948 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | blend         | vol_top_20   | trend_3m_long_cash     |       0.6000 |         0.4000 | 0.2363 |   0.9262 |  -0.4509 |       0.2551 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | blend         | vol_top_20   | trend_6m_long_cash     |       0.8000 |         0.2000 | 0.2599 |   0.7747 |  -0.5440 |       0.3355 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | blend         | vol_top_20   | trend_6m_long_cash     |       0.7000 |         0.3000 | 0.2468 |   0.8353 |  -0.4993 |       0.2955 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | blend         | vol_top_20   | trend_6m_long_cash     |       0.6000 |         0.4000 | 0.2317 |   0.9048 |  -0.4509 |       0.2561 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.8000 |         0.2000 | 0.2650 |   0.7910 |  -0.5440 |       0.3350 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.7000 |         0.3000 | 0.2543 |   0.8629 |  -0.4993 |       0.2947 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend         | vol_top_20   | trend_3m_6m_long_cash  |       0.6000 |         0.4000 | 0.2415 |   0.9468 |  -0.4509 |       0.2551 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | blend         | vol_top_20   | trend_3m_long_short    |       0.8000 |         0.2000 | 0.2535 |   0.7626 |  -0.5418 |       0.3325 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | blend         | vol_top_20   | trend_3m_long_short    |       0.7000 |         0.3000 | 0.2371 |   0.8151 |  -0.4956 |       0.2909 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | blend         | vol_top_20   | trend_3m_long_short    |       0.6000 |         0.4000 | 0.2186 |   0.8746 |  -0.4457 |       0.2499 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | blend         | vol_top_20   | trend_6m_long_short    |       0.8000 |         0.2000 | 0.2503 |   0.7514 |  -0.5418 |       0.3331 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | blend         | vol_top_20   | trend_6m_long_short    |       0.7000 |         0.3000 | 0.2324 |   0.7963 |  -0.4956 |       0.2919 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | blend         | vol_top_20   | trend_6m_long_short    |       0.6000 |         0.4000 | 0.2125 |   0.8461 |  -0.4457 |       0.2512 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.8000 |         0.2000 | 0.2563 |   0.7705 |  -0.5418 |       0.3327 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.7000 |         0.3000 | 0.2413 |   0.8286 |  -0.4956 |       0.2912 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend         | vol_top_20   | trend_3m_6m_long_short |       0.6000 |         0.4000 | 0.2241 |   0.8953 |  -0.4457 |       0.2503 |

## Gate

| universe      | sleeve                                        | vol_sleeve   | trend_sleeve           |   sharpe |   max_dd |   equal_weight_sharpe |   trend_crisis_corr_vs_vol |   blend_crisis_corr_vs_vol | passes_gate   |
|:--------------|:----------------------------------------------|:-------------|:-----------------------|---------:|---------:|----------------------:|---------------------------:|---------------------------:|:--------------|
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | vol_top_10   | trend_3m_long_cash     |   0.9533 |  -0.4252 |                0.8299 |                    -0.1294 |                     0.9981 | False         |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | vol_top_10   | trend_3m_long_cash     |   1.0262 |  -0.3728 |                0.8299 |                    -0.1294 |                     0.9945 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | vol_top_10   | trend_3m_long_cash     |   1.1107 |  -0.3201 |                0.8299 |                    -0.1294 |                     0.9866 | True          |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | vol_top_10   | trend_6m_long_cash     |   0.9407 |  -0.4225 |                0.8299 |                    -0.1166 |                     0.9982 | False         |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | vol_top_10   | trend_6m_long_cash     |   1.0049 |  -0.3685 |                0.8299 |                    -0.1166 |                     0.9948 | True          |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | vol_top_10   | trend_6m_long_cash     |   1.0782 |  -0.3201 |                0.8299 |                    -0.1166 |                     0.9874 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | vol_top_10   | trend_3m_6m_long_cash  |   0.9633 |  -0.4231 |                0.8299 |                    -0.1355 |                     0.9982 | False         |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | vol_top_10   | trend_3m_6m_long_cash  |   1.0429 |  -0.3695 |                0.8299 |                    -0.1355 |                     0.9945 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | vol_top_10   | trend_3m_6m_long_cash  |   1.1357 |  -0.3201 |                0.8299 |                    -0.1355 |                     0.9867 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | vol_top_10   | trend_3m_long_short    |   0.9274 |  -0.4226 |                0.8299 |                    -0.2668 |                     0.9981 | False         |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | vol_top_10   | trend_3m_long_short    |   0.9834 |  -0.3687 |                0.8299 |                    -0.2668 |                     0.9944 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | vol_top_10   | trend_3m_long_short    |   1.0471 |  -0.3137 |                0.8299 |                    -0.2668 |                     0.9861 | True          |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | vol_top_10   | trend_6m_long_short    |   0.9108 |  -0.4187 |                0.8299 |                    -0.2477 |                     0.9983 | False         |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | vol_top_10   | trend_6m_long_short    |   0.9554 |  -0.3625 |                0.8299 |                    -0.2477 |                     0.9949 | True          |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | vol_top_10   | trend_6m_long_short    |   1.0047 |  -0.3137 |                0.8299 |                    -0.2477 |                     0.9873 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | vol_top_10   | trend_3m_6m_long_short |   0.9372 |  -0.4199 |                0.8299 |                    -0.2539 |                     0.9981 | False         |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | vol_top_10   | trend_3m_6m_long_short |   0.9999 |  -0.3644 |                0.8299 |                    -0.2539 |                     0.9945 | True          |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | vol_top_10   | trend_3m_6m_long_short |   1.0723 |  -0.3137 |                0.8299 |                    -0.2539 |                     0.9864 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | vol_top_20   | trend_3m_long_cash     |   0.9814 |  -0.4002 |                0.8299 |                    -0.1382 |                     0.9973 | False         |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | vol_top_20   | trend_3m_long_cash     |   1.0617 |  -0.3505 |                0.8299 |                    -0.1382 |                     0.9920 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | vol_top_20   | trend_3m_long_cash     |   1.1532 |  -0.2982 |                0.8299 |                    -0.1382 |                     0.9807 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | vol_top_20   | trend_6m_long_cash     |   0.9658 |  -0.3985 |                0.8299 |                    -0.1205 |                     0.9975 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | vol_top_20   | trend_6m_long_cash     |   1.0353 |  -0.3479 |                0.8299 |                    -0.1205 |                     0.9925 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | vol_top_20   | trend_6m_long_cash     |   1.1130 |  -0.2945 |                0.8299 |                    -0.1205 |                     0.9818 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | vol_top_20   | trend_3m_6m_long_cash  |   0.9927 |  -0.3992 |                0.8299 |                    -0.1381 |                     0.9973 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | vol_top_20   | trend_3m_6m_long_cash  |   1.0804 |  -0.3489 |                0.8299 |                    -0.1381 |                     0.9921 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | vol_top_20   | trend_3m_6m_long_cash  |   1.1809 |  -0.2961 |                0.8299 |                    -0.1381 |                     0.9809 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | vol_top_20   | trend_3m_long_short    |   0.9522 |  -0.3967 |                0.8299 |                    -0.2892 |                     0.9973 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | vol_top_20   | trend_3m_long_short    |   1.0138 |  -0.3446 |                0.8299 |                    -0.2892 |                     0.9919 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | vol_top_20   | trend_3m_long_short    |   1.0827 |  -0.2900 |                0.8299 |                    -0.2892 |                     0.9799 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | vol_top_20   | trend_6m_long_short    |   0.9317 |  -0.3951 |                0.8299 |                    -0.2655 |                     0.9975 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | vol_top_20   | trend_6m_long_short    |   0.9792 |  -0.3415 |                0.8299 |                    -0.2655 |                     0.9926 | True          |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | vol_top_20   | trend_6m_long_short    |   1.0304 |  -0.2849 |                0.8299 |                    -0.2655 |                     0.9817 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | vol_top_20   | trend_3m_6m_long_short |   0.9631 |  -0.3957 |                0.8299 |                    -0.2691 |                     0.9973 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | vol_top_20   | trend_3m_6m_long_short |   1.0321 |  -0.3426 |                0.8299 |                    -0.2691 |                     0.9920 | True          |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | vol_top_20   | trend_3m_6m_long_short |   1.1105 |  -0.2872 |                0.8299 |                    -0.2691 |                     0.9803 | True          |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | vol_top_10   | trend_3m_long_cash     |   0.6809 |  -0.6659 |                0.7784 |                    -0.1076 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | vol_top_10   | trend_3m_long_cash     |   0.7470 |  -0.5974 |                0.7784 |                    -0.1076 |                     0.9978 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | vol_top_10   | trend_3m_long_cash     |   0.8230 |  -0.5201 |                0.7784 |                    -0.1076 |                     0.9947 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | vol_top_10   | trend_6m_long_cash     |   0.6739 |  -0.6651 |                0.7784 |                    -0.1031 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | vol_top_10   | trend_6m_long_cash     |   0.7351 |  -0.5961 |                0.7784 |                    -0.1031 |                     0.9979 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | vol_top_10   | trend_6m_long_cash     |   0.8048 |  -0.5182 |                0.7784 |                    -0.1031 |                     0.9950 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | vol_top_10   | trend_3m_6m_long_cash  |   0.6878 |  -0.6651 |                0.7784 |                    -0.1168 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | vol_top_10   | trend_3m_6m_long_cash  |   0.7587 |  -0.5961 |                0.7784 |                    -0.1168 |                     0.9979 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | vol_top_10   | trend_3m_6m_long_cash  |   0.8408 |  -0.5183 |                0.7784 |                    -0.1168 |                     0.9948 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | vol_top_10   | trend_3m_long_short    |   0.6625 |  -0.6639 |                0.7784 |                    -0.2227 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | vol_top_10   | trend_3m_long_short    |   0.7159 |  -0.5939 |                0.7784 |                    -0.2227 |                     0.9978 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | vol_top_10   | trend_3m_long_short    |   0.7757 |  -0.5149 |                0.7784 |                    -0.2227 |                     0.9946 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | vol_top_10   | trend_6m_long_short    |   0.6531 |  -0.6628 |                0.7784 |                    -0.2183 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | vol_top_10   | trend_6m_long_short    |   0.7001 |  -0.5920 |                0.7784 |                    -0.2183 |                     0.9980 | False         |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | vol_top_10   | trend_6m_long_short    |   0.7517 |  -0.5122 |                0.7784 |                    -0.2183 |                     0.9950 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | vol_top_10   | trend_3m_6m_long_short |   0.6694 |  -0.6627 |                0.7784 |                    -0.2189 |                     0.9993 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | vol_top_10   | trend_3m_6m_long_short |   0.7276 |  -0.5919 |                0.7784 |                    -0.2189 |                     0.9978 | False         |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | vol_top_10   | trend_3m_6m_long_short |   0.7937 |  -0.5120 |                0.7784 |                    -0.2189 |                     0.9947 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | vol_top_20   | trend_3m_long_cash     |   0.7829 |  -0.5440 |                0.7784 |                    -0.1032 |                     0.9990 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | vol_top_20   | trend_3m_long_cash     |   0.8493 |  -0.4993 |                0.7784 |                    -0.1032 |                     0.9970 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | vol_top_20   | trend_3m_long_cash     |   0.9262 |  -0.4509 |                0.7784 |                    -0.1032 |                     0.9927 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | vol_top_20   | trend_6m_long_cash     |   0.7747 |  -0.5440 |                0.7784 |                    -0.0999 |                     0.9990 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | vol_top_20   | trend_6m_long_cash     |   0.8353 |  -0.4993 |                0.7784 |                    -0.0999 |                     0.9972 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | vol_top_20   | trend_6m_long_cash     |   0.9048 |  -0.4509 |                0.7784 |                    -0.0999 |                     0.9932 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | vol_top_20   | trend_3m_6m_long_cash  |   0.7910 |  -0.5440 |                0.7784 |                    -0.1151 |                     0.9990 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | vol_top_20   | trend_3m_6m_long_cash  |   0.8629 |  -0.4993 |                0.7784 |                    -0.1151 |                     0.9970 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | vol_top_20   | trend_3m_6m_long_cash  |   0.9468 |  -0.4509 |                0.7784 |                    -0.1151 |                     0.9928 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | vol_top_20   | trend_3m_long_short    |   0.7626 |  -0.5418 |                0.7784 |                    -0.2308 |                     0.9990 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | vol_top_20   | trend_3m_long_short    |   0.8151 |  -0.4956 |                0.7784 |                    -0.2308 |                     0.9969 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | vol_top_20   | trend_3m_long_short    |   0.8746 |  -0.4457 |                0.7784 |                    -0.2308 |                     0.9925 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | vol_top_20   | trend_6m_long_short    |   0.7514 |  -0.5418 |                0.7784 |                    -0.2265 |                     0.9991 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | vol_top_20   | trend_6m_long_short    |   0.7963 |  -0.4956 |                0.7784 |                    -0.2265 |                     0.9972 | False         |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | vol_top_20   | trend_6m_long_short    |   0.8461 |  -0.4457 |                0.7784 |                    -0.2265 |                     0.9932 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | vol_top_20   | trend_3m_6m_long_short |   0.7705 |  -0.5418 |                0.7784 |                    -0.2282 |                     0.9990 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | vol_top_20   | trend_3m_6m_long_short |   0.8286 |  -0.4956 |                0.7784 |                    -0.2282 |                     0.9970 | False         |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | vol_top_20   | trend_3m_6m_long_short |   0.8953 |  -0.4457 |                0.7784 |                    -0.2282 |                     0.9927 | False         |

Gate counts by universe:

| universe      |   passing_variants |
|:--------------|-------------------:|
| sp100_sample  |                 29 |
| sp500_dynamic |                  0 |

Validation gate result: FAIL

## Correlation

| universe      | vol_sleeve   | other_sleeve                                  | other_type   |   full_correlation |   avg_rolling_252d_correlation |
|:--------------|:-------------|:----------------------------------------------|:-------------|-------------------:|-------------------------------:|
| sp100_sample  | vol_top_10   | trend_3m_long_cash                            | trend        |             0.0622 |                         0.1600 |
| sp100_sample  | vol_top_10   | trend_6m_long_cash                            | trend        |             0.0990 |                         0.2138 |
| sp100_sample  | vol_top_10   | trend_3m_6m_long_cash                         | trend        |             0.0668 |                         0.1717 |
| sp100_sample  | vol_top_10   | trend_3m_long_short                           | trend        |            -0.0832 |                         0.0164 |
| sp100_sample  | vol_top_10   | trend_6m_long_short                           | trend        |            -0.0318 |                         0.0920 |
| sp100_sample  | vol_top_10   | trend_3m_6m_long_short                        | trend        |            -0.0623 |                         0.0539 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |             0.9969 |                         0.9959 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |             0.9911 |                         0.9885 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |             0.9791 |                         0.9740 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |             0.9969 |                         0.9961 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |             0.9912 |                         0.9891 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |             0.9793 |                         0.9755 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |             0.9969 |                         0.9959 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |             0.9909 |                         0.9885 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |             0.9787 |                         0.9743 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |             0.9970 |                         0.9958 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |             0.9911 |                         0.9880 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |             0.9786 |                         0.9721 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |             0.9971 |                         0.9961 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |             0.9915 |                         0.9891 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |             0.9798 |                         0.9751 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |             0.9970 |                         0.9960 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |             0.9913 |                         0.9887 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |             0.9791 |                         0.9740 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |             0.9632 |                         0.9524 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |             0.9542 |                         0.9410 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |             0.9366 |                         0.9205 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |             0.9627 |                         0.9522 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |             0.9536 |                         0.9414 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |             0.9360 |                         0.9223 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |             0.9626 |                         0.9520 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |             0.9533 |                         0.9406 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |             0.9350 |                         0.9203 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |             0.9639 |                         0.9529 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |             0.9553 |                         0.9410 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |             0.9371 |                         0.9185 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |             0.9636 |                         0.9531 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |             0.9551 |                         0.9423 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |             0.9377 |                         0.9224 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |             0.9634 |                         0.9527 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |             0.9545 |                         0.9414 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |             0.9364 |                         0.9203 |
| sp100_sample  | vol_top_20   | trend_3m_long_cash                            | trend        |             0.0744 |                         0.1871 |
| sp100_sample  | vol_top_20   | trend_6m_long_cash                            | trend        |             0.1172 |                         0.2467 |
| sp100_sample  | vol_top_20   | trend_3m_6m_long_cash                         | trend        |             0.0836 |                         0.2018 |
| sp100_sample  | vol_top_20   | trend_3m_long_short                           | trend        |            -0.0839 |                         0.0305 |
| sp100_sample  | vol_top_20   | trend_6m_long_short                           | trend        |            -0.0251 |                         0.1139 |
| sp100_sample  | vol_top_20   | trend_3m_6m_long_short                        | trend        |            -0.0559 |                         0.0738 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |             0.9667 |                         0.9606 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |             0.9618 |                         0.9561 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |             0.9512 |                         0.9453 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |             0.9672 |                         0.9617 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |             0.9628 |                         0.9582 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |             0.9528 |                         0.9490 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |             0.9670 |                         0.9611 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |             0.9623 |                         0.9570 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |             0.9518 |                         0.9469 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |             0.9653 |                         0.9585 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |             0.9594 |                         0.9524 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |             0.9471 |                         0.9388 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |             0.9662 |                         0.9598 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |             0.9611 |                         0.9551 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |             0.9501 |                         0.9442 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |             0.9660 |                         0.9595 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |             0.9606 |                         0.9543 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |             0.9491 |                         0.9425 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |             0.9954 |                         0.9941 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |             0.9869 |                         0.9837 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |             0.9695 |                         0.9639 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |             0.9955 |                         0.9944 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |             0.9870 |                         0.9848 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |             0.9701 |                         0.9669 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |             0.9953 |                         0.9941 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |             0.9866 |                         0.9839 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |             0.9690 |                         0.9648 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |             0.9954 |                         0.9937 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |             0.9866 |                         0.9823 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |             0.9680 |                         0.9598 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |             0.9957 |                         0.9943 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |             0.9874 |                         0.9842 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |             0.9701 |                         0.9648 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |             0.9955 |                         0.9941 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |             0.9869 |                         0.9835 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |             0.9689 |                         0.9630 |
| sp500_dynamic | vol_top_10   | trend_3m_long_cash                            | trend        |             0.0448 |                         0.1292 |
| sp500_dynamic | vol_top_10   | trend_6m_long_cash                            | trend        |             0.0662 |                         0.1686 |
| sp500_dynamic | vol_top_10   | trend_3m_6m_long_cash                         | trend        |             0.0418 |                         0.1392 |
| sp500_dynamic | vol_top_10   | trend_3m_long_short                           | trend        |            -0.0814 |                         0.0011 |
| sp500_dynamic | vol_top_10   | trend_6m_long_short                           | trend        |            -0.0494 |                         0.0562 |
| sp500_dynamic | vol_top_10   | trend_3m_6m_long_short                        | trend        |            -0.0705 |                         0.0336 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |             0.9988 |                         0.9981 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |             0.9965 |                         0.9945 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |             0.9917 |                         0.9873 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |             0.9988 |                         0.9981 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |             0.9965 |                         0.9946 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |             0.9916 |                         0.9876 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |             0.9988 |                         0.9981 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |             0.9964 |                         0.9945 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |             0.9915 |                         0.9874 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |             0.9988 |                         0.9981 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |             0.9966 |                         0.9945 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |             0.9917 |                         0.9869 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |             0.9989 |                         0.9982 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |             0.9967 |                         0.9948 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |             0.9921 |                         0.9879 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |             0.9989 |                         0.9982 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |             0.9966 |                         0.9948 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |             0.9918 |                         0.9878 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |             0.9717 |                         0.9620 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |             0.9682 |                         0.9570 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |             0.9613 |                         0.9475 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |             0.9717 |                         0.9621 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |             0.9681 |                         0.9574 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |             0.9611 |                         0.9484 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |             0.9717 |                         0.9622 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |             0.9682 |                         0.9574 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |             0.9611 |                         0.9482 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |             0.9722 |                         0.9621 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |             0.9689 |                         0.9570 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |             0.9622 |                         0.9470 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |             0.9721 |                         0.9623 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |             0.9689 |                         0.9576 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |             0.9623 |                         0.9486 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |             0.9722 |                         0.9623 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |             0.9690 |                         0.9576 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |             0.9624 |                         0.9485 |
| sp500_dynamic | vol_top_20   | trend_3m_long_cash                            | trend        |             0.0591 |                         0.1484 |
| sp500_dynamic | vol_top_20   | trend_6m_long_cash                            | trend        |             0.0824 |                         0.1878 |
| sp500_dynamic | vol_top_20   | trend_3m_6m_long_cash                         | trend        |             0.0552 |                         0.1562 |
| sp500_dynamic | vol_top_20   | trend_3m_long_short                           | trend        |            -0.0776 |                         0.0134 |
| sp500_dynamic | vol_top_20   | trend_6m_long_short                           | trend        |            -0.0416 |                         0.0701 |
| sp500_dynamic | vol_top_20   | trend_3m_6m_long_short                        | trend        |            -0.0663 |                         0.0457 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |             0.9736 |                         0.9653 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |             0.9719 |                         0.9632 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |             0.9679 |                         0.9579 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |             0.9738 |                         0.9656 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |             0.9721 |                         0.9637 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |             0.9682 |                         0.9587 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |             0.9736 |                         0.9654 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |             0.9718 |                         0.9633 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |             0.9676 |                         0.9580 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |             0.9730 |                         0.9646 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |             0.9708 |                         0.9619 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |             0.9662 |                         0.9556 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |             0.9733 |                         0.9649 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |             0.9714 |                         0.9627 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |             0.9671 |                         0.9572 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |             0.9730 |                         0.9648 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |             0.9710 |                         0.9624 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |             0.9664 |                         0.9568 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |             0.9984 |                         0.9975 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |             0.9953 |                         0.9930 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |             0.9888 |                         0.9838 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |             0.9984 |                         0.9975 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |             0.9953 |                         0.9931 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |             0.9888 |                         0.9844 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |             0.9983 |                         0.9975 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |             0.9952 |                         0.9930 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |             0.9886 |                         0.9841 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |             0.9984 |                         0.9975 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |             0.9953 |                         0.9928 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |             0.9887 |                         0.9831 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |             0.9985 |                         0.9976 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |             0.9956 |                         0.9933 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |             0.9893 |                         0.9845 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |             0.9984 |                         0.9976 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |             0.9954 |                         0.9932 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |             0.9890 |                         0.9843 |

## Crisis Correlation

| universe      | vol_sleeve   | other_sleeve                                  | other_type   |   crisis_correlation |   crisis_observations |
|:--------------|:-------------|:----------------------------------------------|:-------------|---------------------:|----------------------:|
| sp100_sample  | vol_top_10   | trend_3m_long_cash                            | trend        |              -0.1294 |                   902 |
| sp100_sample  | vol_top_10   | trend_6m_long_cash                            | trend        |              -0.1166 |                   902 |
| sp100_sample  | vol_top_10   | trend_3m_6m_long_cash                         | trend        |              -0.1355 |                   902 |
| sp100_sample  | vol_top_10   | trend_3m_long_short                           | trend        |              -0.2668 |                   902 |
| sp100_sample  | vol_top_10   | trend_6m_long_short                           | trend        |              -0.2477 |                   902 |
| sp100_sample  | vol_top_10   | trend_3m_6m_long_short                        | trend        |              -0.2539 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |               0.9981 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |               0.9945 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |               0.9866 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |               0.9982 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |               0.9948 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |               0.9874 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |               0.9982 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |               0.9945 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |               0.9867 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |               0.9981 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |               0.9944 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |               0.9861 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |               0.9983 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |               0.9949 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |               0.9873 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |               0.9981 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |               0.9945 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |               0.9864 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |               0.9749 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |               0.9700 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |               0.9594 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |               0.9747 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |               0.9699 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |               0.9596 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |               0.9745 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |               0.9694 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |               0.9584 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |               0.9757 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |               0.9713 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |               0.9608 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |               0.9755 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |               0.9713 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |               0.9615 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |               0.9752 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |               0.9705 |                   902 |
| sp100_sample  | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |               0.9597 |                   902 |
| sp100_sample  | vol_top_20   | trend_3m_long_cash                            | trend        |              -0.1382 |                   902 |
| sp100_sample  | vol_top_20   | trend_6m_long_cash                            | trend        |              -0.1205 |                   902 |
| sp100_sample  | vol_top_20   | trend_3m_6m_long_cash                         | trend        |              -0.1381 |                   902 |
| sp100_sample  | vol_top_20   | trend_3m_long_short                           | trend        |              -0.2892 |                   902 |
| sp100_sample  | vol_top_20   | trend_6m_long_short                           | trend        |              -0.2655 |                   902 |
| sp100_sample  | vol_top_20   | trend_3m_6m_long_short                        | trend        |              -0.2691 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |               0.9746 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |               0.9705 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |               0.9621 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |               0.9750 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |               0.9714 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |               0.9637 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |               0.9750 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |               0.9712 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |               0.9632 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |               0.9735 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |               0.9685 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |               0.9586 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |               0.9740 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |               0.9696 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |               0.9609 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |               0.9740 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |               0.9694 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |               0.9602 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |               0.9973 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |               0.9920 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |               0.9807 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |               0.9975 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |               0.9925 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |               0.9818 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |               0.9973 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |               0.9921 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |               0.9809 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |               0.9973 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |               0.9919 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |               0.9799 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |               0.9975 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |               0.9926 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |               0.9817 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |               0.9973 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |               0.9920 |                   902 |
| sp100_sample  | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |               0.9803 |                   902 |
| sp500_dynamic | vol_top_10   | trend_3m_long_cash                            | trend        |              -0.1076 |                   902 |
| sp500_dynamic | vol_top_10   | trend_6m_long_cash                            | trend        |              -0.1031 |                   902 |
| sp500_dynamic | vol_top_10   | trend_3m_6m_long_cash                         | trend        |              -0.1168 |                   902 |
| sp500_dynamic | vol_top_10   | trend_3m_long_short                           | trend        |              -0.2227 |                   902 |
| sp500_dynamic | vol_top_10   | trend_6m_long_short                           | trend        |              -0.2183 |                   902 |
| sp500_dynamic | vol_top_10   | trend_3m_6m_long_short                        | trend        |              -0.2189 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |               0.9978 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |               0.9947 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |               0.9979 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |               0.9950 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |               0.9979 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |               0.9948 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |               0.9978 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |               0.9946 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |               0.9980 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |               0.9950 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |               0.9993 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |               0.9978 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |               0.9947 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |               0.9810 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |               0.9789 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |               0.9744 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |               0.9811 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |               0.9791 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |               0.9750 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |               0.9811 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |               0.9791 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |               0.9748 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |               0.9815 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |               0.9796 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |               0.9754 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |               0.9816 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |               0.9799 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |               0.9761 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |               0.9815 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |               0.9798 |                   902 |
| sp500_dynamic | vol_top_10   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |               0.9757 |                   902 |
| sp500_dynamic | vol_top_20   | trend_3m_long_cash                            | trend        |              -0.1032 |                   902 |
| sp500_dynamic | vol_top_20   | trend_6m_long_cash                            | trend        |              -0.0999 |                   902 |
| sp500_dynamic | vol_top_20   | trend_3m_6m_long_cash                         | trend        |              -0.1151 |                   902 |
| sp500_dynamic | vol_top_20   | trend_3m_long_short                           | trend        |              -0.2308 |                   902 |
| sp500_dynamic | vol_top_20   | trend_6m_long_short                           | trend        |              -0.2265 |                   902 |
| sp500_dynamic | vol_top_20   | trend_3m_6m_long_short                        | trend        |              -0.2282 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_80_20     | blend        |               0.9817 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_70_30     | blend        |               0.9803 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_cash_60_40     | blend        |               0.9773 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_80_20     | blend        |               0.9817 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_70_30     | blend        |               0.9804 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_cash_60_40     | blend        |               0.9775 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | blend        |               0.9816 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | blend        |               0.9802 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | blend        |               0.9771 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_80_20    | blend        |               0.9811 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_70_30    | blend        |               0.9793 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_long_short_60_40    | blend        |               0.9756 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_80_20    | blend        |               0.9812 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_70_30    | blend        |               0.9795 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_6m_long_short_60_40    | blend        |               0.9762 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_80_20 | blend        |               0.9810 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_70_30 | blend        |               0.9793 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_10_trend_3m_6m_long_short_60_40 | blend        |               0.9756 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_80_20     | blend        |               0.9990 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_70_30     | blend        |               0.9970 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_cash_60_40     | blend        |               0.9927 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_80_20     | blend        |               0.9990 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_70_30     | blend        |               0.9972 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_cash_60_40     | blend        |               0.9932 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | blend        |               0.9990 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | blend        |               0.9970 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | blend        |               0.9928 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_80_20    | blend        |               0.9990 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_70_30    | blend        |               0.9969 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_long_short_60_40    | blend        |               0.9925 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_80_20    | blend        |               0.9991 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_70_30    | blend        |               0.9972 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_6m_long_short_60_40    | blend        |               0.9932 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_80_20 | blend        |               0.9990 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_70_30 | blend        |               0.9970 |                   902 |
| sp500_dynamic | vol_top_20   | blend_vol_top_20_trend_3m_6m_long_short_60_40 | blend        |               0.9927 |                   902 |

## Period Drawdowns

| universe      | sleeve                                        | period         |    cagr |   sharpe |   max_dd |
|:--------------|:----------------------------------------------|:---------------|--------:|---------:|---------:|
| sp100_sample  | vol_top_10                                    | gfc            |  0.1751 |   0.3190 |  -0.5221 |
| sp100_sample  | vol_top_10                                    | covid          | -0.3398 |  -0.4504 |  -0.4565 |
| sp100_sample  | vol_top_10                                    | inflation_2022 | -0.2939 |  -0.7917 |  -0.3592 |
| sp100_sample  | vol_top_10                                    | recent         |  0.5184 |   2.4353 |  -0.1644 |
| sp100_sample  | vol_top_20                                    | gfc            |  0.0852 |   0.1914 |  -0.4939 |
| sp100_sample  | vol_top_20                                    | covid          | -0.2651 |  -0.3950 |  -0.4109 |
| sp100_sample  | vol_top_20                                    | inflation_2022 | -0.1889 |  -0.6410 |  -0.2717 |
| sp100_sample  | vol_top_20                                    | recent         |  0.3481 |   2.0806 |  -0.1655 |
| sp100_sample  | trend_3m_long_cash                            | gfc            |  0.0869 |   0.8213 |  -0.1349 |
| sp100_sample  | trend_3m_long_cash                            | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp100_sample  | trend_3m_long_cash                            | inflation_2022 |  0.0650 |   0.6119 |  -0.0917 |
| sp100_sample  | trend_3m_long_cash                            | recent         |  0.1217 |   1.4873 |  -0.0572 |
| sp100_sample  | trend_6m_long_cash                            | gfc            |  0.0740 |   0.6788 |  -0.1237 |
| sp100_sample  | trend_6m_long_cash                            | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp100_sample  | trend_6m_long_cash                            | inflation_2022 |  0.0120 |   0.1135 |  -0.0996 |
| sp100_sample  | trend_6m_long_cash                            | recent         |  0.1319 |   1.6183 |  -0.0882 |
| sp100_sample  | trend_3m_6m_long_cash                         | gfc            |  0.0725 |   0.6487 |  -0.1288 |
| sp100_sample  | trend_3m_6m_long_cash                         | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp100_sample  | trend_3m_6m_long_cash                         | inflation_2022 |  0.1100 |   1.0387 |  -0.0834 |
| sp100_sample  | trend_3m_6m_long_cash                         | recent         |  0.1409 |   1.6354 |  -0.0631 |
| sp100_sample  | trend_3m_long_short                           | gfc            |  0.0803 |   0.7246 |  -0.1465 |
| sp100_sample  | trend_3m_long_short                           | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp100_sample  | trend_3m_long_short                           | inflation_2022 |  0.1309 |   1.2118 |  -0.0820 |
| sp100_sample  | trend_3m_long_short                           | recent         |  0.0401 |   0.4884 |  -0.1059 |
| sp100_sample  | trend_6m_long_short                           | gfc            |  0.0490 |   0.4269 |  -0.1281 |
| sp100_sample  | trend_6m_long_short                           | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp100_sample  | trend_6m_long_short                           | inflation_2022 |  0.0698 |   0.6574 |  -0.0920 |
| sp100_sample  | trend_6m_long_short                           | recent         |  0.0468 |   0.5824 |  -0.1014 |
| sp100_sample  | trend_3m_6m_long_short                        | gfc            |  0.0519 |   0.4358 |  -0.1369 |
| sp100_sample  | trend_3m_6m_long_short                        | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp100_sample  | trend_3m_6m_long_short                        | inflation_2022 |  0.1677 |   1.5308 |  -0.0791 |
| sp100_sample  | trend_3m_6m_long_short                        | recent         |  0.0598 |   0.7004 |  -0.0881 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | gfc            |  0.1950 |   0.4483 |  -0.4252 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | covid          | -0.2243 |  -0.3644 |  -0.3908 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | inflation_2022 | -0.2164 |  -0.7489 |  -0.2781 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_80_20     | recent         |  0.4462 |   2.5322 |  -0.1400 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | gfc            |  0.1963 |   0.5184 |  -0.3728 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | covid          | -0.1688 |  -0.3085 |  -0.3561 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | inflation_2022 | -0.1798 |  -0.7230 |  -0.2366 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_70_30     | recent         |  0.4050 |   2.5536 |  -0.1287 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | gfc            |  0.1936 |   0.5995 |  -0.3175 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | covid          | -0.1138 |  -0.2374 |  -0.3201 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | inflation_2022 | -0.1430 |  -0.6835 |  -0.1965 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_cash_60_40     | recent         |  0.3643 |   2.5722 |  -0.1175 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | gfc            |  0.1920 |   0.4428 |  -0.4225 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | covid          | -0.2243 |  -0.3644 |  -0.3908 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | inflation_2022 | -0.2251 |  -0.7728 |  -0.2866 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_80_20     | recent         |  0.4481 |   2.5329 |  -0.1473 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | gfc            |  0.1917 |   0.5089 |  -0.3685 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | covid          | -0.1688 |  -0.3085 |  -0.3561 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | inflation_2022 | -0.1932 |  -0.7664 |  -0.2500 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_70_30     | recent         |  0.4078 |   2.5549 |  -0.1397 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | gfc            |  0.1872 |   0.5848 |  -0.3114 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | covid          | -0.1138 |  -0.2374 |  -0.3201 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | inflation_2022 | -0.1615 |  -0.7552 |  -0.2121 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_cash_60_40     | recent         |  0.3681 |   2.5748 |  -0.1321 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | gfc            |  0.1921 |   0.4435 |  -0.4231 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | covid          | -0.2243 |  -0.3644 |  -0.3908 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | inflation_2022 | -0.2100 |  -0.7293 |  -0.2782 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | recent         |  0.4511 |   2.5647 |  -0.1386 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | gfc            |  0.1918 |   0.5100 |  -0.3695 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | covid          | -0.1688 |  -0.3085 |  -0.3561 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | inflation_2022 | -0.1698 |  -0.6869 |  -0.2368 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | recent         |  0.4120 |   2.6048 |  -0.1266 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | gfc            |  0.1873 |   0.5864 |  -0.3129 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | covid          | -0.1138 |  -0.2374 |  -0.3201 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | inflation_2022 | -0.1291 |  -0.6231 |  -0.1965 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | recent         |  0.3734 |   2.6434 |  -0.1146 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | gfc            |  0.1960 |   0.4540 |  -0.4226 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | covid          | -0.2359 |  -0.3886 |  -0.3878 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | inflation_2022 | -0.2060 |  -0.7211 |  -0.2709 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_80_20    | recent         |  0.4266 |   2.4875 |  -0.1353 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | gfc            |  0.1974 |   0.5284 |  -0.3687 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | covid          | -0.1882 |  -0.3518 |  -0.3515 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | inflation_2022 | -0.1636 |  -0.6713 |  -0.2252 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_70_30    | recent         |  0.3763 |   2.4812 |  -0.1217 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | gfc            |  0.1946 |   0.6155 |  -0.3117 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | covid          | -0.1423 |  -0.3072 |  -0.3137 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | inflation_2022 | -0.1205 |  -0.5955 |  -0.1796 |
| sp100_sample  | blend_vol_top_10_trend_3m_long_short_60_40    | recent         |  0.3271 |   2.4648 |  -0.1080 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | gfc            |  0.1887 |   0.4383 |  -0.4187 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | covid          | -0.2359 |  -0.3886 |  -0.3878 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | inflation_2022 | -0.2154 |  -0.7489 |  -0.2782 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_80_20    | recent         |  0.4268 |   2.4601 |  -0.1433 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | gfc            |  0.1864 |   0.5010 |  -0.3625 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | covid          | -0.1882 |  -0.3518 |  -0.3515 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | inflation_2022 | -0.1783 |  -0.7228 |  -0.2368 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_70_30    | recent         |  0.3767 |   2.4368 |  -0.1338 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | gfc            |  0.1798 |   0.5724 |  -0.3029 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | covid          | -0.1423 |  -0.3072 |  -0.3137 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | inflation_2022 | -0.1410 |  -0.6827 |  -0.1937 |
| sp100_sample  | blend_vol_top_10_trend_6m_long_short_60_40    | recent         |  0.3277 |   2.4017 |  -0.1258 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | gfc            |  0.1899 |   0.4416 |  -0.4199 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | covid          | -0.2359 |  -0.3886 |  -0.3878 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | inflation_2022 | -0.2012 |  -0.7062 |  -0.2713 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_80_20 | recent         |  0.4312 |   2.5114 |  -0.1303 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | gfc            |  0.1881 |   0.5067 |  -0.3644 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | covid          | -0.1882 |  -0.3518 |  -0.3515 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | inflation_2022 | -0.1559 |  -0.6433 |  -0.2259 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_70_30 | recent         |  0.3830 |   2.5189 |  -0.1141 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | gfc            |  0.1820 |   0.5812 |  -0.3056 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | covid          | -0.1423 |  -0.3072 |  -0.3137 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | inflation_2022 | -0.1099 |  -0.5475 |  -0.1796 |
| sp100_sample  | blend_vol_top_10_trend_3m_6m_long_short_60_40 | recent         |  0.3357 |   2.5177 |  -0.0996 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | gfc            |  0.1114 |   0.3167 |  -0.4002 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | covid          | -0.1625 |  -0.2957 |  -0.3406 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | inflation_2022 | -0.1303 |  -0.5731 |  -0.2082 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_80_20     | recent         |  0.3104 |   2.2115 |  -0.1421 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | gfc            |  0.1186 |   0.3881 |  -0.3505 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | covid          | -0.1146 |  -0.2340 |  -0.3090 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | inflation_2022 | -0.1032 |  -0.5303 |  -0.1767 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_70_30     | recent         |  0.2881 |   2.2558 |  -0.1308 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | gfc            |  0.1233 |   0.4737 |  -0.2982 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | covid          | -0.0677 |  -0.1571 |  -0.2778 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | inflation_2022 | -0.0764 |  -0.4688 |  -0.1471 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_cash_60_40     | recent         |  0.2659 |   2.2944 |  -0.1194 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | gfc            |  0.1084 |   0.3096 |  -0.3985 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | covid          | -0.1625 |  -0.2957 |  -0.3406 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | inflation_2022 | -0.1398 |  -0.6082 |  -0.2154 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_80_20     | recent         |  0.3122 |   2.2128 |  -0.1493 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | gfc            |  0.1141 |   0.3759 |  -0.3479 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | covid          | -0.1146 |  -0.2340 |  -0.3090 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | inflation_2022 | -0.1177 |  -0.5933 |  -0.1877 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_70_30     | recent         |  0.2908 |   2.2581 |  -0.1416 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | gfc            |  0.1171 |   0.4546 |  -0.2945 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | covid          | -0.0677 |  -0.1571 |  -0.2778 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | inflation_2022 | -0.0962 |  -0.5719 |  -0.1595 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_cash_60_40     | recent         |  0.2694 |   2.2989 |  -0.1339 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | gfc            |  0.1085 |   0.3101 |  -0.3992 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | covid          | -0.1625 |  -0.2957 |  -0.3406 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | inflation_2022 | -0.1233 |  -0.5444 |  -0.2082 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | recent         |  0.3148 |   2.2481 |  -0.1407 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | gfc            |  0.1141 |   0.3767 |  -0.3489 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | covid          | -0.1146 |  -0.2340 |  -0.3090 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | inflation_2022 | -0.0923 |  -0.4779 |  -0.1766 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | recent         |  0.2945 |   2.3129 |  -0.1287 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | gfc            |  0.1171 |   0.4558 |  -0.2961 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | covid          | -0.0677 |  -0.1571 |  -0.2778 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | inflation_2022 | -0.0615 |  -0.3818 |  -0.1471 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | recent         |  0.2743 |   2.3729 |  -0.1165 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | gfc            |  0.1121 |   0.3223 |  -0.3967 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | covid          | -0.1755 |  -0.3243 |  -0.3385 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | inflation_2022 | -0.1188 |  -0.5314 |  -0.1986 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_80_20    | recent         |  0.2925 |   2.1609 |  -0.1375 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | gfc            |  0.1194 |   0.3982 |  -0.3446 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | covid          | -0.1358 |  -0.2845 |  -0.3041 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | inflation_2022 | -0.0856 |  -0.4529 |  -0.1617 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_70_30    | recent         |  0.2616 |   2.1724 |  -0.1238 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | gfc            |  0.1240 |   0.4907 |  -0.2900 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | covid          | -0.0984 |  -0.2372 |  -0.2711 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | inflation_2022 | -0.0524 |  -0.3371 |  -0.1264 |
| sp100_sample  | blend_vol_top_20_trend_3m_long_short_60_40    | recent         |  0.2311 |   2.1678 |  -0.1101 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | gfc            |  0.1052 |   0.3035 |  -0.3951 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | covid          | -0.1755 |  -0.3243 |  -0.3385 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | inflation_2022 | -0.1292 |  -0.5721 |  -0.2056 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_80_20    | recent         |  0.2928 |   2.1286 |  -0.1454 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | gfc            |  0.1090 |   0.3654 |  -0.3415 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | covid          | -0.1358 |  -0.2845 |  -0.3041 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | inflation_2022 | -0.1016 |  -0.5282 |  -0.1726 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_70_30    | recent         |  0.2621 |   2.1206 |  -0.1356 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | gfc            |  0.1099 |   0.4386 |  -0.2849 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | covid          | -0.0984 |  -0.2372 |  -0.2711 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | inflation_2022 | -0.0743 |  -0.4645 |  -0.1387 |
| sp100_sample  | blend_vol_top_20_trend_6m_long_short_60_40    | recent         |  0.2318 |   2.0958 |  -0.1259 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | gfc            |  0.1063 |   0.3070 |  -0.3957 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | covid          | -0.1755 |  -0.3243 |  -0.3385 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | inflation_2022 | -0.1135 |  -0.5092 |  -0.1994 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_80_20 | recent         |  0.2967 |   2.1860 |  -0.1325 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | gfc            |  0.1105 |   0.3714 |  -0.3426 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | covid          | -0.1358 |  -0.2845 |  -0.3041 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | inflation_2022 | -0.0773 |  -0.4116 |  -0.1630 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_70_30 | recent         |  0.2677 |   2.2117 |  -0.1162 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | gfc            |  0.1119 |   0.4479 |  -0.2872 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | covid          | -0.0984 |  -0.2372 |  -0.2711 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | inflation_2022 | -0.0410 |  -0.2664 |  -0.1264 |
| sp100_sample  | blend_vol_top_20_trend_3m_6m_long_short_60_40 | recent         |  0.2390 |   2.2224 |  -0.0998 |
| sp500_dynamic | vol_top_10                                    | gfc            |  0.0897 |   0.1029 |  -0.7811 |
| sp500_dynamic | vol_top_10                                    | covid          | -0.3565 |  -0.3182 |  -0.6452 |
| sp500_dynamic | vol_top_10                                    | inflation_2022 | -0.5625 |  -0.7829 |  -0.5903 |
| sp500_dynamic | vol_top_10                                    | recent         |  0.6218 |   1.4768 |  -0.4061 |
| sp500_dynamic | vol_top_20                                    | gfc            |  0.1646 |   0.2247 |  -0.6176 |
| sp500_dynamic | vol_top_20                                    | covid          | -0.4707 |  -0.4567 |  -0.6242 |
| sp500_dynamic | vol_top_20                                    | inflation_2022 | -0.4708 |  -0.7910 |  -0.4975 |
| sp500_dynamic | vol_top_20                                    | recent         |  0.7240 |   1.9595 |  -0.3764 |
| sp500_dynamic | trend_3m_long_cash                            | gfc            |  0.0869 |   0.8213 |  -0.1349 |
| sp500_dynamic | trend_3m_long_cash                            | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp500_dynamic | trend_3m_long_cash                            | inflation_2022 |  0.0650 |   0.6119 |  -0.0917 |
| sp500_dynamic | trend_3m_long_cash                            | recent         |  0.1217 |   1.4873 |  -0.0572 |
| sp500_dynamic | trend_6m_long_cash                            | gfc            |  0.0740 |   0.6788 |  -0.1237 |
| sp500_dynamic | trend_6m_long_cash                            | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp500_dynamic | trend_6m_long_cash                            | inflation_2022 |  0.0120 |   0.1135 |  -0.0996 |
| sp500_dynamic | trend_6m_long_cash                            | recent         |  0.1319 |   1.6183 |  -0.0882 |
| sp500_dynamic | trend_3m_6m_long_cash                         | gfc            |  0.0725 |   0.6487 |  -0.1288 |
| sp500_dynamic | trend_3m_6m_long_cash                         | covid          |  0.1624 |   0.9789 |  -0.0825 |
| sp500_dynamic | trend_3m_6m_long_cash                         | inflation_2022 |  0.1100 |   1.0387 |  -0.0834 |
| sp500_dynamic | trend_3m_6m_long_cash                         | recent         |  0.1409 |   1.6354 |  -0.0631 |
| sp500_dynamic | trend_3m_long_short                           | gfc            |  0.0803 |   0.7246 |  -0.1465 |
| sp500_dynamic | trend_3m_long_short                           | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp500_dynamic | trend_3m_long_short                           | inflation_2022 |  0.1309 |   1.2118 |  -0.0820 |
| sp500_dynamic | trend_3m_long_short                           | recent         |  0.0401 |   0.4884 |  -0.1059 |
| sp500_dynamic | trend_6m_long_short                           | gfc            |  0.0490 |   0.4269 |  -0.1281 |
| sp500_dynamic | trend_6m_long_short                           | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp500_dynamic | trend_6m_long_short                           | inflation_2022 |  0.0698 |   0.6574 |  -0.0920 |
| sp500_dynamic | trend_6m_long_short                           | recent         |  0.0468 |   0.5824 |  -0.1014 |
| sp500_dynamic | trend_3m_6m_long_short                        | gfc            |  0.0519 |   0.4358 |  -0.1369 |
| sp500_dynamic | trend_3m_6m_long_short                        | covid          |  0.0521 |   0.3294 |  -0.0825 |
| sp500_dynamic | trend_3m_6m_long_short                        | inflation_2022 |  0.1677 |   1.5308 |  -0.0791 |
| sp500_dynamic | trend_3m_6m_long_short                        | recent         |  0.0598 |   0.7004 |  -0.0881 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | gfc            |  0.1730 |   0.2492 |  -0.6659 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | covid          | -0.1940 |  -0.2140 |  -0.5639 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | inflation_2022 | -0.4486 |  -0.7900 |  -0.4905 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_80_20     | recent         |  0.5458 |   1.5959 |  -0.3348 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | gfc            |  0.1961 |   0.3236 |  -0.5974 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | covid          | -0.1203 |  -0.1501 |  -0.5182 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | inflation_2022 | -0.3886 |  -0.7881 |  -0.4353 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_70_30     | recent         |  0.4956 |   1.6373 |  -0.2979 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | gfc            |  0.2100 |   0.4054 |  -0.5201 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | covid          | -0.0511 |  -0.0734 |  -0.4685 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | inflation_2022 | -0.3258 |  -0.7784 |  -0.3760 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_cash_60_40     | recent         |  0.4448 |   1.6858 |  -0.2596 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | gfc            |  0.1705 |   0.2461 |  -0.6651 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | covid          | -0.1940 |  -0.2140 |  -0.5639 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | inflation_2022 | -0.4547 |  -0.7991 |  -0.4954 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_80_20     | recent         |  0.5477 |   1.5991 |  -0.3436 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | gfc            |  0.1920 |   0.3180 |  -0.5961 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | covid          | -0.1203 |  -0.1501 |  -0.5182 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | inflation_2022 | -0.3986 |  -0.8056 |  -0.4434 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_70_30     | recent         |  0.4985 |   1.6426 |  -0.3118 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | gfc            |  0.2042 |   0.3963 |  -0.5182 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | covid          | -0.0511 |  -0.0734 |  -0.4685 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | inflation_2022 | -0.3404 |  -0.8086 |  -0.3877 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_cash_60_40     | recent         |  0.4486 |   1.6937 |  -0.2788 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | gfc            |  0.1707 |   0.2464 |  -0.6651 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | covid          | -0.1940 |  -0.2140 |  -0.5639 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | inflation_2022 | -0.4440 |  -0.7831 |  -0.4906 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_80_20  | recent         |  0.5511 |   1.6132 |  -0.3364 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | gfc            |  0.1922 |   0.3186 |  -0.5961 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | covid          | -0.1203 |  -0.1501 |  -0.5182 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | inflation_2022 | -0.3809 |  -0.7747 |  -0.4355 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_70_30  | recent         |  0.5033 |   1.6655 |  -0.3005 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | gfc            |  0.2044 |   0.3972 |  -0.5183 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | covid          | -0.0511 |  -0.0734 |  -0.4685 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | inflation_2022 | -0.3146 |  -0.7550 |  -0.3763 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_cash_60_40  | recent         |  0.4545 |   1.7269 |  -0.2632 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | gfc            |  0.1747 |   0.2527 |  -0.6639 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | covid          | -0.2057 |  -0.2284 |  -0.5618 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | inflation_2022 | -0.4409 |  -0.7805 |  -0.4839 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_80_20    | recent         |  0.5256 |   1.5547 |  -0.3337 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | gfc            |  0.1982 |   0.3295 |  -0.5939 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | covid          | -0.1401 |  -0.1770 |  -0.5148 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | inflation_2022 | -0.3758 |  -0.7693 |  -0.4245 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_70_30    | recent         |  0.4661 |   1.5699 |  -0.2964 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | gfc            |  0.2121 |   0.4144 |  -0.5149 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | covid          | -0.0808 |  -0.1182 |  -0.4636 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | inflation_2022 | -0.3074 |  -0.7450 |  -0.3602 |
| sp500_dynamic | blend_vol_top_10_trend_3m_long_short_60_40    | recent         |  0.4064 |   1.5863 |  -0.2576 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | gfc            |  0.1680 |   0.2435 |  -0.6628 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | covid          | -0.2057 |  -0.2284 |  -0.5618 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | inflation_2022 | -0.4475 |  -0.7908 |  -0.4889 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_80_20    | recent         |  0.5254 |   1.5458 |  -0.3448 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | gfc            |  0.1877 |   0.3132 |  -0.5920 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | covid          | -0.1401 |  -0.1770 |  -0.5148 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | inflation_2022 | -0.3869 |  -0.7894 |  -0.4326 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_70_30    | recent         |  0.4660 |   1.5555 |  -0.3136 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | gfc            |  0.1978 |   0.3882 |  -0.5122 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | covid          | -0.0808 |  -0.1182 |  -0.4636 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | inflation_2022 | -0.3235 |  -0.7802 |  -0.3721 |
| sp500_dynamic | blend_vol_top_10_trend_6m_long_short_60_40    | recent         |  0.4065 |   1.5653 |  -0.2814 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | gfc            |  0.1693 |   0.2455 |  -0.6627 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | covid          | -0.2057 |  -0.2284 |  -0.5618 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | inflation_2022 | -0.4374 |  -0.7752 |  -0.4847 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_80_20 | recent         |  0.5305 |   1.5677 |  -0.3345 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | gfc            |  0.1896 |   0.3166 |  -0.5919 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | covid          | -0.1401 |  -0.1770 |  -0.5148 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | inflation_2022 | -0.3700 |  -0.7591 |  -0.4257 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_70_30 | recent         |  0.4731 |   1.5910 |  -0.2975 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | gfc            |  0.2002 |   0.3935 |  -0.5120 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | covid          | -0.0808 |  -0.1182 |  -0.4636 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | inflation_2022 | -0.2988 |  -0.7268 |  -0.3620 |
| sp500_dynamic | blend_vol_top_10_trend_3m_6m_long_short_60_40 | recent         |  0.4154 |   1.6171 |  -0.2592 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | gfc            |  0.2135 |   0.3661 |  -0.4960 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | covid          | -0.3212 |  -0.3844 |  -0.5440 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | inflation_2022 | -0.3667 |  -0.7822 |  -0.4031 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_80_20     | recent         |  0.6145 |   2.0404 |  -0.3093 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | gfc            |  0.2225 |   0.4373 |  -0.4305 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | covid          | -0.2480 |  -0.3356 |  -0.4993 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | inflation_2022 | -0.3138 |  -0.7724 |  -0.3531 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_70_30     | recent         |  0.5515 |   2.0630 |  -0.2747 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | gfc            |  0.2245 |   0.5164 |  -0.3614 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | covid          | -0.1752 |  -0.2724 |  -0.4509 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | inflation_2022 | -0.2595 |  -0.7538 |  -0.3005 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_cash_60_40     | recent         |  0.4892 |   2.0907 |  -0.2388 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | gfc            |  0.2109 |   0.3625 |  -0.4937 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | covid          | -0.3212 |  -0.3844 |  -0.5440 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | inflation_2022 | -0.3738 |  -0.7945 |  -0.4088 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_80_20     | recent         |  0.6165 |   2.0429 |  -0.3185 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | gfc            |  0.2182 |   0.4309 |  -0.4273 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | covid          | -0.2480 |  -0.3356 |  -0.4993 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | inflation_2022 | -0.3251 |  -0.7956 |  -0.3623 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_70_30     | recent         |  0.5545 |   2.0669 |  -0.2890 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | gfc            |  0.2185 |   0.5062 |  -0.3573 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | covid          | -0.1752 |  -0.2724 |  -0.4509 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | inflation_2022 | -0.2755 |  -0.7932 |  -0.3136 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_cash_60_40     | recent         |  0.4931 |   2.0966 |  -0.2586 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | gfc            |  0.2110 |   0.3630 |  -0.4937 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | covid          | -0.3212 |  -0.3844 |  -0.5440 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | inflation_2022 | -0.3615 |  -0.7724 |  -0.4032 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_80_20  | recent         |  0.6200 |   2.0612 |  -0.3110 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | gfc            |  0.2184 |   0.4316 |  -0.4274 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | covid          | -0.2480 |  -0.3356 |  -0.4993 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | inflation_2022 | -0.3053 |  -0.7539 |  -0.3534 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_70_30  | recent         |  0.5594 |   2.0964 |  -0.2773 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | gfc            |  0.2187 |   0.5072 |  -0.3574 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | covid          | -0.1752 |  -0.2724 |  -0.4509 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | inflation_2022 | -0.2473 |  -0.7222 |  -0.3009 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_cash_60_40  | recent         |  0.4992 |   2.1388 |  -0.2425 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | gfc            |  0.2151 |   0.3708 |  -0.4945 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | covid          | -0.3310 |  -0.3994 |  -0.5418 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | inflation_2022 | -0.3579 |  -0.7689 |  -0.3954 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_80_20    | recent         |  0.5932 |   1.9969 |  -0.3082 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | gfc            |  0.2243 |   0.4452 |  -0.4282 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | covid          | -0.2650 |  -0.3635 |  -0.4956 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | inflation_2022 | -0.2997 |  -0.7469 |  -0.3408 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_70_30    | recent         |  0.5207 |   1.9926 |  -0.2731 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | gfc            |  0.2264 |   0.5285 |  -0.3583 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | covid          | -0.2010 |  -0.3192 |  -0.4457 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | inflation_2022 | -0.2394 |  -0.7094 |  -0.2829 |
| sp500_dynamic | blend_vol_top_20_trend_3m_long_short_60_40    | recent         |  0.4494 |   1.9880 |  -0.2368 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | gfc            |  0.2081 |   0.3596 |  -0.4915 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | covid          | -0.3310 |  -0.3994 |  -0.5418 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | inflation_2022 | -0.3656 |  -0.7830 |  -0.4012 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_80_20    | recent         |  0.5931 |   1.9833 |  -0.3197 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | gfc            |  0.2136 |   0.4256 |  -0.4233 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | covid          | -0.2650 |  -0.3635 |  -0.4956 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | inflation_2022 | -0.3121 |  -0.7738 |  -0.3501 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_70_30    | recent         |  0.5206 |   1.9707 |  -0.2909 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | gfc            |  0.2117 |   0.4976 |  -0.3512 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | covid          | -0.2010 |  -0.3192 |  -0.4457 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | inflation_2022 | -0.2571 |  -0.7558 |  -0.2961 |
| sp500_dynamic | blend_vol_top_20_trend_6m_long_short_60_40    | recent         |  0.4496 |   1.9562 |  -0.2613 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | gfc            |  0.2093 |   0.3621 |  -0.4914 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | covid          | -0.3310 |  -0.3994 |  -0.5418 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | inflation_2022 | -0.3539 |  -0.7614 |  -0.3963 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_80_20 | recent         |  0.5983 |   2.0122 |  -0.3090 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | gfc            |  0.2154 |   0.4297 |  -0.4232 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | covid          | -0.2650 |  -0.3635 |  -0.4956 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | inflation_2022 | -0.2932 |  -0.7326 |  -0.3422 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_70_30 | recent         |  0.5280 |   2.0172 |  -0.2742 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | gfc            |  0.2141 |   0.5039 |  -0.3511 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | covid          | -0.2010 |  -0.3192 |  -0.4457 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | inflation_2022 | -0.2300 |  -0.6846 |  -0.2849 |
| sp500_dynamic | blend_vol_top_20_trend_3m_6m_long_short_60_40 | recent         |  0.4587 |   2.0233 |  -0.2384 |

## Benchmarks

| universe      | benchmark                   |   cagr |   sharpe |   max_dd |   volatility |
|:--------------|:----------------------------|-------:|---------:|---------:|-------------:|
| sp100_sample  | spy_buy_hold                | 0.1114 |   0.5607 |  -0.5187 |       0.1986 |
| sp100_sample  | equal_weight_universe_daily | 0.1619 |   0.8299 |  -0.4318 |       0.1951 |
| sp500_dynamic | spy_buy_hold                | 0.1114 |   0.5607 |  -0.5187 |       0.1986 |
| sp500_dynamic | equal_weight_universe_daily | 0.1648 |   0.7784 |  -0.4912 |       0.2117 |

## Decision

The trend overlay passed on the research universe but failed the validation universe. Do not promote it yet; improve drawdown control and rerun validation.
