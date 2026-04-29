# Portfolio Expression Results

- Run date: 2026-04-28 19:52:40 UTC
- Alpha definition unchanged: `volatility_score` high-vol/risk-premium direction.
- RL disabled.
- High-beta stocks are not removed; crash regimes scale exposure but do not disable the alpha.

## Goal

Convert the validated volatility alpha into an investable portfolio by testing beta-targeted weights, volatility-scaled weights, regime-aware exposure scaling, and explicit SPY hedges.

## Expected Decision

If a sp500 configuration reaches MaxDD < 40%, Sharpe above equal-weight, and CAGR close to simple Top-N, keep the standalone volatility sleeve as production-candidate. Otherwise move to multi-factor blending.

## Best Variants

| variant                                                   | selection              |   top_n | sector_balanced   | construction   | vol_method     |   target_beta | use_exposure_scaling   | universe      |   cagr |   sharpe |   max_dd |   volatility |   avg_realized_beta |   avg_abs_beta_error |   avg_exposure_multiplier |   turnover_sum |   n_rebalances | solver_statuses                       |
|:----------------------------------------------------------|:-----------------------|--------:|:------------------|:---------------|:---------------|--------------:|:-----------------------|:--------------|-------:|---------:|---------:|-------------:|--------------------:|---------------------:|--------------------------:|---------------:|---------------:|:--------------------------------------|
| sector_balanced_top_30_spy_hedge_beta_0.5_exposure_scaled | sector_balanced_top_30 |      30 | True              | spy_hedge      | equal_weight   |        0.5000 | True                   | sp100_sample  | 0.1010 |   1.1634 |  -0.1720 |       0.0868 |              0.4314 |               0.0000 |                    0.8628 |        62.5696 |            239 | not_applicable=239                    |
| sector_balanced_top_20_spy_hedge_beta_0.5_exposure_scaled | sector_balanced_top_20 |      20 | True              | spy_hedge      | equal_weight   |        0.5000 | True                   | sp100_sample  | 0.1033 |   1.1332 |  -0.1559 |       0.0912 |              0.4314 |               0.0000 |                    0.8628 |        86.3137 |            239 | not_applicable=239                    |
| top_30_spy_hedge_beta_0.5_exposure_scaled                 | top_30                 |      30 | False             | spy_hedge      | equal_weight   |        0.5000 | True                   | sp100_sample  | 0.0962 |   1.1063 |  -0.1535 |       0.0869 |              0.4314 |               0.0000 |                    0.8628 |        57.3598 |            239 | not_applicable=239                    |
| top_20_spy_hedge_beta_0.5_exposure_scaled                 | top_20                 |      20 | False             | spy_hedge      | equal_weight   |        0.5000 | True                   | sp100_sample  | 0.1022 |   1.0740 |  -0.1762 |       0.0952 |              0.4314 |               0.0000 |                    0.8628 |        84.1301 |            239 | not_applicable=239                    |
| sector_balanced_top_30_spy_hedge_beta_0.7_exposure_scaled | sector_balanced_top_30 |      30 | True              | spy_hedge      | equal_weight   |        0.7000 | True                   | sp100_sample  | 0.1215 |   1.0651 |  -0.2230 |       0.1141 |              0.6039 |               0.0000 |                    0.8628 |        59.8642 |            239 | not_applicable=239                    |
| sector_balanced_top_20_spy_hedge_beta_0.7_exposure_scaled | sector_balanced_top_20 |      20 | True              | spy_hedge      | equal_weight   |        0.7000 | True                   | sp100_sample  | 0.1240 |   1.0606 |  -0.2205 |       0.1169 |              0.6039 |               0.0000 |                    0.8628 |        83.4229 |            239 | not_applicable=239                    |
| top_20_spy_hedge_beta_0.7_exposure_scaled                 | top_20                 |      20 | False             | spy_hedge      | equal_weight   |        0.7000 | True                   | sp100_sample  | 0.1229 |   1.0311 |  -0.2200 |       0.1192 |              0.6039 |               0.0000 |                    0.8628 |        81.2035 |            239 | not_applicable=239                    |
| top_30_spy_hedge_beta_0.7_exposure_scaled                 | top_30                 |      30 | False             | spy_hedge      | equal_weight   |        0.7000 | True                   | sp100_sample  | 0.1166 |   1.0246 |  -0.2077 |       0.1138 |              0.6039 |               0.0000 |                    0.8628 |        54.4162 |            239 | not_applicable=239                    |
| sector_balanced_top_20_beta_target_0.7_exposure_scaled    | sector_balanced_top_20 |      20 | True              | beta_target    | not_applicable |        0.7000 | True                   | sp500_dynamic | 0.1629 |   0.7529 |  -0.4632 |       0.2164 |              0.8674 |               0.2635 |                    0.8628 |       229.2662 |            239 | optimal=238;user_limit_equal_weight=1 |
| sector_balanced_top_20_equal_weight_exposure_scaled       | sector_balanced_top_20 |      20 | True              | vol_scaling    | equal_weight   |      nan      | True                   | sp500_dynamic | 0.1942 |   0.7503 |  -0.4501 |       0.2588 |              1.4175 |             nan      |                    0.8628 |       144.5100 |            239 | not_applicable=239                    |
| sector_balanced_top_20_beta_target_0.5_exposure_scaled    | sector_balanced_top_20 |      20 | True              | beta_target    | not_applicable |        0.5000 | True                   | sp500_dynamic | 0.1621 |   0.7500 |  -0.4676 |       0.2161 |              0.8622 |               0.4308 |                    0.8628 |       227.4654 |            239 | optimal=239                           |
| sector_balanced_top_20_inverse_vol_exposure_scaled        | sector_balanced_top_20 |      20 | True              | vol_scaling    | inverse_vol    |      nan      | True                   | sp500_dynamic | 0.1728 |   0.7276 |  -0.4335 |       0.2375 |              1.3145 |             nan      |                    0.8628 |       164.0477 |            239 | not_applicable=239                    |
| sector_balanced_top_20_spy_hedge_beta_1.0_exposure_scaled | sector_balanced_top_20 |      20 | True              | spy_hedge      | equal_weight   |        1.0000 | True                   | sp500_dynamic | 0.1358 |   0.7273 |  -0.3588 |       0.1867 |              0.8628 |               0.0000 |                    0.8628 |       174.6039 |            239 | not_applicable=239                    |
| sector_balanced_top_20_alpha_over_vol_exposure_scaled     | sector_balanced_top_20 |      20 | True              | vol_scaling    | alpha_over_vol |      nan      | True                   | sp500_dynamic | 0.1776 |   0.7174 |  -0.4471 |       0.2476 |              1.3783 |             nan      |                    0.8628 |       157.9228 |            239 | not_applicable=239                    |
| top_30_equal_weight_exposure_scaled                       | top_30                 |      30 | False             | vol_scaling    | equal_weight   |      nan      | True                   | sp500_dynamic | 0.2064 |   0.7072 |  -0.5140 |       0.2919 |              1.5842 |             nan      |                    0.8628 |       113.2667 |            239 | not_applicable=239                    |
| top_30_spy_hedge_beta_1.0_exposure_scaled                 | top_30                 |      30 | False             | spy_hedge      | equal_weight   |        1.0000 | True                   | sp500_dynamic | 0.1389 |   0.7039 |  -0.3942 |       0.1974 |              0.8628 |               0.0000 |                    0.8628 |       149.3384 |            239 | not_applicable=239                    |

## Benchmarks

| universe      | variant                     |   cagr |   sharpe |   max_dd |
|:--------------|:----------------------------|-------:|---------:|---------:|
| sp100_sample  | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |
| sp100_sample  | equal_weight_universe_daily | 0.1620 |   0.8302 |  -0.4318 |
| sp500_dynamic | spy_buy_hold                | 0.1114 |   0.5609 |  -0.5187 |
| sp500_dynamic | equal_weight_universe_daily | 0.1649 |   0.7787 |  -0.4912 |

## Success Criteria

- sp500 MaxDD < 40% and Sharpe > equal-weight: FAIL
- No sp500 variant met both hard gates in this run.

## Interpretation

- Phase A.2 did not find an investable standalone `volatility_score` portfolio on sp500.
- Best sp500 Sharpe was `0.753` from `sector_balanced_top_20_beta_target_0.7_exposure_scaled`, but MaxDD remained `-46.32%` and Sharpe stayed below equal-weight (`0.779`).
- Best sp500 CAGR among strong volatility-alpha expressions was `22.08%` from `top_20_equal_weight_exposure_scaled`, but MaxDD was `-52.73%` and Sharpe was only `0.700`.
- SPY hedging successfully reduced drawdown: `sector_balanced_top_20_spy_hedge_beta_1.0_exposure_scaled` reached MaxDD `-35.88%`, but CAGR fell to `13.58%` and Sharpe to `0.727`, still below equal-weight.
- Lower beta hedge targets reduced drawdown further (`~ -26.6%`) but cut CAGR to `6.35-8.44%`, so the alpha is not strong enough as a standalone hedged sleeve.
- Long-only beta targeting is not reliable for low-beta targets: the best beta-targeted sp500 variants had realized beta around `0.86-0.87` even when target beta was `0.5-0.7`.
- Conclusion: `volatility_score` is real cross-sectional alpha, but not directly investable as a standalone production sleeve under the tested constructions. Move next to multi-factor blending rather than RL or further standalone optimizer tuning.

## Notes

- Long-only beta targeting reports realized beta error; do not accept a nominal target if realized beta misses materially.
- SPY hedge variants allow negative benchmark exposure and are research-only until execution assumptions are finalized.
