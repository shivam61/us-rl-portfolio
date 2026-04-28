# Crash-Onset Control

- Baseline: `baseline_v1_volatility_score_sp100`
- Alpha rankings unchanged: `volatility_score` used for all variants
- Optimizer alpha normalization unchanged
- RL disabled

## Crash Trigger Summary

- Crash trigger days: `576`
- Trigger day share: `11.27%`
- False-positive rate: `75.17%`
- Missed-crash rate: `41.75%`

## Backtest Comparison

| variant                               |   cagr |   sharpe |   max_dd |   dd_2020 |   dd_2022 |   trigger_count |   avg_exposure_during_crash_triggers |   false_positive_rate |   missed_crash_rate |
|:--------------------------------------|-------:|---------:|---------:|----------:|----------:|----------------:|-------------------------------------:|----------------------:|--------------------:|
| baseline_v1                           | 0.1728 |   0.9151 |  -0.3706 |   -0.3706 |   -0.3365 |             576 |                               0.6374 |                0.7517 |              0.4175 |
| crash_onset_exposure_50               | 0.1643 |   0.8855 |  -0.3706 |   -0.3706 |   -0.3365 |             576 |                               0.5214 |                0.7517 |              0.4175 |
| crash_onset_exposure_60               | 0.1664 |   0.8953 |  -0.3706 |   -0.3706 |   -0.3365 |             576 |                               0.5454 |                0.7517 |              0.4175 |
| crash_onset_beta_cap_075              | 0.1667 |   0.8953 |  -0.3706 |   -0.3706 |   -0.3365 |             576 |                               0.5532 |                0.7517 |              0.4175 |
| crash_onset_exposure_60_plus_beta_cap | 0.1663 |   0.8943 |  -0.3706 |   -0.3706 |   -0.3365 |             576 |                               0.5450 |                0.7517 |              0.4175 |

## Success Criteria

| variant                               | maxdd_lt_32pct   | cagr_gt_16pct   | sharpe_ge_0_9   | dd_2020_reduces   | dd_2022_reduces   | sparse_trigger   | all_pass   |
|:--------------------------------------|:-----------------|:----------------|:----------------|:------------------|:------------------|:-----------------|:-----------|
| baseline_v1                           | False            | True            | True            | True              | True              | False            | False      |
| crash_onset_exposure_50               | False            | True            | False           | True              | True              | False            | False      |
| crash_onset_exposure_60               | False            | True            | False           | True              | False             | False            | False      |
| crash_onset_beta_cap_075              | False            | True            | False           | True              | True              | False            | False      |
| crash_onset_exposure_60_plus_beta_cap | False            | True            | False           | True              | False             | False            | False      |

## Interpretation

- Best MaxDD variant: `crash_onset_exposure_60` at `-37.06%`.
- No crash-onset variant reaches the MaxDD `<32%` target in this run.
- This experiment changes only crash-window exposure/beta, not alpha ranking.
- The trigger is too broad and too late as currently formulated: false positives are high, missed-crash rate is material, and 2020/2022 drawdowns do not improve.
- Do not adopt these crash-onset controls as production defaults without a narrower trigger design.
