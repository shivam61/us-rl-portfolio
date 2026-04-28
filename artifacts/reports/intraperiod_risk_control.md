# Intraperiod Risk Control

- Baseline: `baseline_v1_volatility_score_sp100`
- Alpha rankings unchanged
- Optimizer unchanged
- No regime switching
- RL disabled
- Implementation note: daily return overlay reduces exposure by 40% on SPY/VIX shocks, applies portfolio drawdown brakes on adjusted NAV, and tests entry smoothing as 70/80/90/100% exposure over the first four trading days after each rebalance.
- `entry_smoothing` is reported separately because it is a capital-deployment control, not a hedge trigger.

## Backtest Comparison

| variant                                 |   cagr |   sharpe |   max_dd |   dd_2020 |   dd_2022 |   avg_hedge_usage |   avg_exposure_multiplier |
|:----------------------------------------|-------:|---------:|---------:|----------:|----------:|------------------:|--------------------------:|
| baseline_v1                             | 0.1728 |   0.9151 |  -0.3706 |   -0.3706 |   -0.3365 |            0.0000 |                    1.0000 |
| intraperiod_overlay                     | 0.2353 |   1.3342 |  -0.3042 |   -0.2227 |   -0.3042 |            0.0252 |                    0.9899 |
| drawdown_brake                          | 0.1281 |   0.9205 |  -0.2549 |   -0.2549 |   -0.2332 |            0.0000 |                    0.8160 |
| intraperiod_overlay_plus_drawdown_brake | 0.1686 |   1.1676 |  -0.2327 |   -0.2220 |   -0.2327 |            0.0252 |                    0.8630 |
| entry_smoothing                         | 0.1708 |   0.9294 |  -0.3435 |   -0.3435 |   -0.3208 |            0.0000 |                    0.9689 |
| all_controls                            | 0.1619 |   1.1417 |  -0.2287 |   -0.2216 |   -0.2287 |            0.0252 |                    0.8385 |

## Hedge Timing

- First hedge activation lag vs 2020 crash start: `5` days
- First hedge activation lag vs 2022 drawdown start: `41` days

## Success Criteria

| variant                                 | maxdd_lt_32pct   | cagr_gt_16pct   | sharpe_ge_0_9   | dd_2020_reduces   | all_pass   |
|:----------------------------------------|:-----------------|:----------------|:----------------|:------------------|:-----------|
| baseline_v1                             | False            | True            | True            | True              | False      |
| intraperiod_overlay                     | True             | True            | True            | True              | True       |
| drawdown_brake                          | True             | False           | True            | True              | False      |
| intraperiod_overlay_plus_drawdown_brake | True             | True            | True            | True              | True       |
| entry_smoothing                         | False            | True            | True            | True              | False      |
| all_controls                            | True             | True            | True            | True              | True       |

## Interpretation

- Best MaxDD variant: `all_controls` at `-22.87%`.
- At least one intraperiod overlay passes the full gate.
- This is an overlay test on daily realized baseline returns; it does not change portfolio construction.
