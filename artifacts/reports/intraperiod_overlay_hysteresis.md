# Intraperiod Overlay Hysteresis

- Baseline: `baseline_v1_volatility_score_sp100`
- Alpha rankings unchanged
- Optimizer unchanged
- RL disabled
- Entry: `SPY 5d return < -6% OR VIX 3d change > +40%`
- Exit: `SPY 5d return > -2% AND VIX 3d change < +15%`
- Restore ramp after exit: `60% -> 75% -> 90% -> 100%` over three trading days
- Current production overlay reference: trade count `8237`, cost `$37,487`

## Comparison

| variant                           |   cagr |   sharpe |   max_dd |   dd_2020 |   dd_2022 |   overlay_events |   overlay_days |   trade_count |   total_cost |   avg_cash_exposure |
|:----------------------------------|-------:|---------:|---------:|----------:|----------:|-----------------:|---------------:|--------------:|-------------:|--------------------:|
| baseline_v1                       | 0.1730 |   0.9170 |  -0.3706 |   -0.3706 |   -0.3365 |                0 |              0 |          5872 |   29526.9197 |              0.1070 |
| overlay_hysteresis_3d             | 0.1664 |   0.9493 |  -0.3320 |   -0.2729 |   -0.3285 |              202 |            317 |          9808 |   37978.4296 |              0.1250 |
| overlay_hysteresis_5d             | 0.1657 |   0.9503 |  -0.3350 |   -0.2729 |   -0.3282 |              199 |            354 |          9692 |   37697.0533 |              0.1276 |
| overlay_hysteresis_10d            | 0.1695 |   1.0050 |  -0.3237 |   -0.2502 |   -0.3219 |              185 |            548 |          9264 |   37637.3371 |              0.1433 |
| overlay_hysteresis_5d_cooldown_3d | 0.1650 |   0.9454 |  -0.3350 |   -0.2729 |   -0.3282 |              198 |            348 |          9673 |   37279.3442 |              0.1273 |
| overlay_hysteresis_5d_cooldown_5d | 0.1615 |   0.9231 |  -0.3350 |   -0.3124 |   -0.3282 |              198 |            343 |          9673 |   36036.4824 |              0.1270 |

## Success Criteria

| variant                           | maxdd_below_32_or_meaningfully_below_34   | cagr_gt_16pct   | sharpe_ge_0_9   | trade_count_below_current_overlay   | cost_closer_to_baseline   | all_pass   |
|:----------------------------------|:------------------------------------------|:----------------|:----------------|:------------------------------------|:--------------------------|:-----------|
| baseline_v1                       | False                                     | True            | True            | True                                | True                      | False      |
| overlay_hysteresis_3d             | True                                      | True            | True            | False                               | False                     | False      |
| overlay_hysteresis_5d             | True                                      | True            | True            | False                               | False                     | False      |
| overlay_hysteresis_10d            | True                                      | True            | True            | False                               | False                     | False      |
| overlay_hysteresis_5d_cooldown_3d | True                                      | True            | True            | False                               | True                      | False      |
| overlay_hysteresis_5d_cooldown_5d | True                                      | True            | True            | False                               | True                      | False      |

## Interpretation

- Best gate-ranked variant: `overlay_hysteresis_10d` with CAGR `16.95%`, Sharpe `1.005`, MaxDD `-32.37%`.
- No hysteresis variant passes the full current gate.
- Hysteresis improved drawdown and Sharpe, but did not solve churn because longer holds plus the daily restore ramp create additional execution events.
- The strongest candidate is `overlay_hysteresis_10d`: it gets close to the drawdown target and passes CAGR/Sharpe, but trade count and cost remain too high for production adoption.
- Next test should remove daily full-book ramp trades or replace stock-book scaling with a SPY hedge sleeve.
- Hysteresis is implemented in the real simulator path using prior-close signals and next-open trades.
