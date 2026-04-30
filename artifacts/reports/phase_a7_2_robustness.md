# Phase A.7.2 Robustness

- Run date: 2026-04-30 06:37:26 UTC
- Base alpha: unchanged `vol_top_20` volatility sleeve.
- Hedge sleeve: unchanged `trend_3m_6m_long_cash`.
- No new alpha, no `volatility_score` modification, RL disabled.
- Tested base weights `60/40`, `50/50`, `40/60`; `k` values `0.2`, `0.3`, `0.4`; VIX-only, drawdown-only, and weighted stress variants.
- Cost scenarios are modeled as all-in turnover costs of `10`, `25`, and `50` bps.
- Configurations with `max_gross > 1.5` are rejected.

## Candidate Check

| universe_path               | universe      | sleeve                         |   base_vol_weight |   base_trend_weight |   stress_k | stress_variant   |   vix_weight |   drawdown_weight |   cost_bps |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   avg_gross |   max_gross |   n_rebalances | passes_max_gross   | passes_full_period_dd   | passes_full_period_sharpe   |
|:----------------------------|:--------------|:-------------------------------|------------------:|--------------------:|-----------:|:-----------------|-------------:|------------------:|-----------:|-------:|---------:|---------:|-------------:|---------------:|------------:|------------:|---------------:|:-------------------|:------------------------|:----------------------------|
| config/universes/sp100.yaml | sp100_sample  | a7_2_weighted_50_50_50_50_k_30 |            0.5000 |              0.5000 |     0.3000 | weighted_50_50   |       0.5000 |            0.5000 |    10.0000 | 0.1822 |   1.7393 |  -0.1700 |       0.1048 |       203.9920 |      1.1392 |      1.3750 |           4407 | True               | True                    | True                        |
| config/universes/sp500.yaml | sp500_dynamic | a7_2_weighted_50_50_50_50_k_30 |            0.5000 |              0.5000 |     0.3000 | weighted_50_50   |       0.5000 |            0.5000 |    10.0000 | 0.2351 |   1.5376 |  -0.2636 |       0.1529 |       230.7480 |      1.1392 |      1.3750 |           4407 | True               | True                    | True                        |

## Best Allowed Full-Period Rows

| universe_path               | universe     | sleeve                         |   base_vol_weight |   base_trend_weight |   stress_k | stress_variant   |   vix_weight |   drawdown_weight |   cost_bps |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   avg_gross |   max_gross |   n_rebalances | passes_max_gross   | passes_full_period_dd   | passes_full_period_sharpe   |
|:----------------------------|:-------------|:-------------------------------|------------------:|--------------------:|-----------:|:-----------------|-------------:|------------------:|-----------:|-------:|---------:|---------:|-------------:|---------------:|------------:|------------:|---------------:|:-------------------|:------------------------|:----------------------------|
| config/universes/sp100.yaml | sp100_sample | a7_2_vix_only_60_40_k_40       |            0.6000 |              0.4000 |     0.4000 | vix_only         |       1.0000 |            0.0000 |    10.0000 | 0.1979 |   1.8768 |  -0.1640 |       0.1055 |       313.6081 |      1.1352 |      1.3750 |           3986 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_70_30_60_40_k_40 |            0.6000 |              0.4000 |     0.4000 | weighted_70_30   |       0.7000 |            0.3000 |    10.0000 | 0.1985 |   1.8548 |  -0.1681 |       0.1070 |       273.3995 |      1.1262 |      1.3750 |           4445 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_50_50_60_40_k_40 |            0.6000 |              0.4000 |     0.4000 | weighted_50_50   |       0.5000 |            0.5000 |    10.0000 | 0.1971 |   1.8051 |  -0.1751 |       0.1092 |       240.2260 |      1.1198 |      1.3750 |           4461 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_vix_only_50_50_k_30       |            0.5000 |              0.5000 |     0.3000 | vix_only         |       1.0000 |            0.0000 |    10.0000 | 0.1815 |   1.7700 |  -0.1636 |       0.1025 |       254.1127 |      1.1504 |      1.3750 |           3829 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_70_30_50_50_k_30 |            0.5000 |              0.5000 |     0.3000 | weighted_70_30   |       0.7000 |            0.3000 |    10.0000 | 0.1830 |   1.7697 |  -0.1656 |       0.1034 |       228.4750 |      1.1440 |      1.3750 |           4382 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_vix_only_60_40_k_30       |            0.6000 |              0.4000 |     0.3000 | vix_only         |       1.0000 |            0.0000 |    10.0000 | 0.1990 |   1.7647 |  -0.1814 |       0.1128 |       265.6057 |      1.1265 |      1.3500 |           4515 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_50_50_50_50_k_40 |            0.5000 |              0.5000 |     0.4000 | weighted_50_50   |       0.5000 |            0.5000 |    10.0000 | 0.1790 |   1.7520 |  -0.1650 |       0.1022 |       228.4921 |      1.1450 |      1.3750 |           3941 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_30_70_60_40_k_40 |            0.6000 |              0.4000 |     0.4000 | weighted_30_70   |       0.3000 |            0.7000 |    10.0000 | 0.1955 |   1.7467 |  -0.1821 |       0.1119 |       207.3435 |      1.1134 |      1.3750 |           4408 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_70_30_50_50_k_40 |            0.5000 |              0.5000 |     0.4000 | weighted_70_30   |       0.7000 |            0.3000 |    10.0000 | 0.1768 |   1.7439 |  -0.1637 |       0.1014 |       249.9724 |      1.1503 |      1.3750 |           3613 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_50_50_50_50_k_30 |            0.5000 |              0.5000 |     0.3000 | weighted_50_50   |       0.5000 |            0.5000 |    10.0000 | 0.1822 |   1.7393 |  -0.1700 |       0.1048 |       203.9920 |      1.1392 |      1.3750 |           4407 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_weighted_30_70_50_50_k_40 |            0.5000 |              0.5000 |     0.4000 | weighted_30_70   |       0.3000 |            0.7000 |    10.0000 | 0.1800 |   1.7326 |  -0.1692 |       0.1039 |       199.1103 |      1.1390 |      1.3750 |           4016 | True               | True                    | True                        |
| config/universes/sp100.yaml | sp100_sample | a7_2_vix_only_50_50_k_40       |            0.5000 |              0.5000 |     0.4000 | vix_only         |       1.0000 |            0.0000 |    10.0000 | 0.1742 |   1.7219 |  -0.1632 |       0.1012 |       262.0243 |      1.1559 |      1.3750 |           3078 | True               | True                    | True                        |

## Regime Summary

| universe      | regime      |   configs |   dd_pass_rate |   sharpe_pass_rate |   worst_max_dd |   median_sharpe |
|:--------------|:------------|----------:|---------------:|-------------------:|---------------:|----------------:|
| sp100_sample  | 2008_crisis |        45 |         1.0000 |             0.0000 |        -0.1860 |          0.0898 |
| sp100_sample  | 2010_2019   |        45 |         1.0000 |             1.0000 |        -0.1388 |          1.7125 |
| sp100_sample  | 2020        |        45 |         1.0000 |             1.0000 |        -0.2328 |          1.1001 |
| sp100_sample  | 2022        |        45 |         1.0000 |             0.0000 |        -0.1195 |          0.4557 |
| sp100_sample  | 2023_2026   |        45 |         1.0000 |             1.0000 |        -0.1065 |          2.5018 |
| sp500_dynamic | 2008_crisis |        45 |         1.0000 |             0.0000 |        -0.2227 |          0.1497 |
| sp500_dynamic | 2010_2019   |        45 |         1.0000 |             1.0000 |        -0.2507 |          1.5462 |
| sp500_dynamic | 2020        |        45 |         1.0000 |             1.0000 |        -0.3771 |          1.1936 |
| sp500_dynamic | 2022        |        45 |         1.0000 |             0.0000 |        -0.2489 |         -0.3152 |
| sp500_dynamic | 2023_2026   |        45 |         1.0000 |             1.0000 |        -0.2232 |          2.4507 |

## k Sensitivity

| universe      |   base_vol_weight |   base_trend_weight | stress_variant   |   stress_k |   avg_sharpe |   avg_max_dd |   configs |
|:--------------|------------------:|--------------------:|:-----------------|-----------:|-------------:|-------------:|----------:|
| sp100_sample  |            0.4000 |              0.6000 | drawdown_only    |     0.2000 |       1.5996 |      -0.1739 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | drawdown_only    |     0.3000 |       1.6180 |      -0.1703 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | drawdown_only    |     0.4000 |       1.6255 |      -0.1673 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | vix_only         |     0.2000 |       1.6488 |      -0.1633 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | vix_only         |     0.3000 |       1.6117 |      -0.1631 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | vix_only         |     0.4000 |       1.5882 |      -0.1631 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_30_70   |     0.2000 |       1.6320 |      -0.1686 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_30_70   |     0.3000 |       1.6350 |      -0.1650 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_30_70   |     0.4000 |       1.6264 |      -0.1637 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_50_50   |     0.2000 |       1.6519 |      -0.1659 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_50_50   |     0.3000 |       1.6286 |      -0.1636 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_50_50   |     0.4000 |       1.6015 |      -0.1632 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_70_30   |     0.2000 |       1.6624 |      -0.1638 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_70_30   |     0.3000 |       1.6140 |      -0.1632 |         1 |
| sp100_sample  |            0.4000 |              0.6000 | weighted_70_30   |     0.4000 |       1.5880 |      -0.1631 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | drawdown_only    |     0.2000 |       1.5353 |      -0.1994 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | drawdown_only    |     0.3000 |       1.6357 |      -0.1831 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | drawdown_only    |     0.4000 |       1.6777 |      -0.1773 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | vix_only         |     0.2000 |       1.6725 |      -0.1810 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | vix_only         |     0.3000 |       1.7700 |      -0.1636 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | vix_only         |     0.4000 |       1.7219 |      -0.1632 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_30_70   |     0.2000 |       1.5802 |      -0.1937 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_30_70   |     0.3000 |       1.7008 |      -0.1752 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_30_70   |     0.4000 |       1.7326 |      -0.1692 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_50_50   |     0.2000 |       1.6083 |      -0.1900 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_50_50   |     0.3000 |       1.7393 |      -0.1700 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_50_50   |     0.4000 |       1.7520 |      -0.1650 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_70_30   |     0.2000 |       1.6351 |      -0.1864 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_70_30   |     0.3000 |       1.7697 |      -0.1656 |         1 |
| sp100_sample  |            0.5000 |              0.5000 | weighted_70_30   |     0.4000 |       1.7439 |      -0.1637 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | drawdown_only    |     0.2000 |       1.4122 |      -0.2328 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | drawdown_only    |     0.3000 |       1.5486 |      -0.2094 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | drawdown_only    |     0.4000 |       1.6507 |      -0.1922 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | vix_only         |     0.2000 |       1.5408 |      -0.2146 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | vix_only         |     0.3000 |       1.7647 |      -0.1814 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | vix_only         |     0.4000 |       1.8768 |      -0.1640 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_30_70   |     0.2000 |       1.4532 |      -0.2273 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_30_70   |     0.3000 |       1.6197 |      -0.2010 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_30_70   |     0.4000 |       1.7467 |      -0.1821 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_50_50   |     0.2000 |       1.4793 |      -0.2237 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_50_50   |     0.3000 |       1.6644 |      -0.1954 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_50_50   |     0.4000 |       1.8051 |      -0.1751 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_70_30   |     0.2000 |       1.5045 |      -0.2200 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_70_30   |     0.3000 |       1.7067 |      -0.1898 |         1 |
| sp100_sample  |            0.6000 |              0.4000 | weighted_70_30   |     0.4000 |       1.8548 |      -0.1681 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | drawdown_only    |     0.2000 |       1.3930 |      -0.2703 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | drawdown_only    |     0.3000 |       1.4290 |      -0.2643 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | drawdown_only    |     0.4000 |       1.4487 |      -0.2594 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | vix_only         |     0.2000 |       1.5146 |      -0.2509 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | vix_only         |     0.3000 |       1.4843 |      -0.2507 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | vix_only         |     0.4000 |       1.4652 |      -0.2507 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_30_70   |     0.2000 |       1.4495 |      -0.2607 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_30_70   |     0.3000 |       1.4767 |      -0.2538 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_30_70   |     0.4000 |       1.4846 |      -0.2518 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_50_50   |     0.2000 |       1.4867 |      -0.2560 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_50_50   |     0.3000 |       1.4890 |      -0.2515 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_50_50   |     0.4000 |       1.4679 |      -0.2508 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_70_30   |     0.2000 |       1.5139 |      -0.2518 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_70_30   |     0.3000 |       1.4817 |      -0.2508 |         1 |
| sp500_dynamic |            0.4000 |              0.6000 | weighted_70_30   |     0.4000 |       1.4554 |      -0.2507 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | drawdown_only    |     0.2000 |       1.2710 |      -0.3191 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | drawdown_only    |     0.3000 |       1.3811 |      -0.2870 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | drawdown_only    |     0.4000 |       1.4406 |      -0.2765 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | vix_only         |     0.2000 |       1.4596 |      -0.2844 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | vix_only         |     0.3000 |       1.6207 |      -0.2517 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | vix_only         |     0.4000 |       1.5937 |      -0.2508 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_30_70   |     0.2000 |       1.3295 |      -0.3089 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_30_70   |     0.3000 |       1.4748 |      -0.2730 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_30_70   |     0.4000 |       1.5351 |      -0.2628 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_50_50   |     0.2000 |       1.3677 |      -0.3019 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_50_50   |     0.3000 |       1.5376 |      -0.2636 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_50_50   |     0.4000 |       1.5851 |      -0.2542 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_70_30   |     0.2000 |       1.4052 |      -0.2950 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_70_30   |     0.3000 |       1.5915 |      -0.2558 |         1 |
| sp500_dynamic |            0.5000 |              0.5000 | weighted_70_30   |     0.4000 |       1.6019 |      -0.2519 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | drawdown_only    |     0.2000 |       1.1371 |      -0.3771 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | drawdown_only    |     0.3000 |       1.2575 |      -0.3371 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | drawdown_only    |     0.4000 |       1.3587 |      -0.3039 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | vix_only         |     0.2000 |       1.2918 |      -0.3450 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | vix_only         |     0.3000 |       1.5350 |      -0.2856 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | vix_only         |     0.4000 |       1.7040 |      -0.2527 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_30_70   |     0.2000 |       1.1846 |      -0.3676 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_30_70   |     0.3000 |       1.3433 |      -0.3219 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_30_70   |     0.4000 |       1.4832 |      -0.2850 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_50_50   |     0.2000 |       1.2157 |      -0.3612 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_50_50   |     0.3000 |       1.3997 |      -0.3117 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_50_50   |     0.4000 |       1.5666 |      -0.2726 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_70_30   |     0.2000 |       1.2465 |      -0.3547 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_70_30   |     0.3000 |       1.4551 |      -0.3013 |         1 |
| sp500_dynamic |            0.6000 |              0.4000 | weighted_70_30   |     0.4000 |       1.6437 |      -0.2605 |         1 |

## Cost Impact Summary

| universe      |   cost_bps |   avg_sharpe |   median_sharpe |   avg_cagr |   configs |
|:--------------|-----------:|-------------:|----------------:|-----------:|----------:|
| sp100_sample  |    10.0000 |       1.6497 |          1.6351 |     0.1789 |        45 |
| sp100_sample  |    25.0000 |       1.4784 |          1.4855 |     0.1607 |        45 |
| sp100_sample  |    50.0000 |       1.1983 |          1.2024 |     0.1310 |        45 |
| sp500_dynamic |    10.0000 |       1.4457 |          1.4652 |     0.2301 |        45 |
| sp500_dynamic |    25.0000 |       1.3068 |          1.3274 |     0.2084 |        45 |
| sp500_dynamic |    50.0000 |       1.0801 |          1.0952 |     0.1730 |        45 |

## Exposure Rejections

- Rejected rows with `max_gross > 1.5`: 0

## Decision

- Full-period drawdown and Sharpe robustness: PASS
- Regime MaxDD `<40%`: PASS
- Regime Sharpe `>0.8`: FAIL
- 50 bps cost-adjusted full-period Sharpe: PASS
- Interpretation: A.7.2 supports the stress-scaled volatility/trend blend as the non-RL production alpha expression, with an explicit caveat that 2008 and 2022 are capital-preservation regimes rather than high-Sharpe regimes.

## Output Files

- `artifacts/reports/phase_a7_2_robustness.md`
- `artifacts/reports/regime_breakdown.csv`
- `artifacts/reports/parameter_sensitivity.csv`
- `artifacts/reports/cost_impact.csv`
