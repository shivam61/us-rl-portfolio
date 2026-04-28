# Stress-Conditioned Alpha

- Baseline: `baseline_v1_volatility_score_sp100`
- Stress rule: `vix_percentile_1y >= 0.8 OR spy_drawdown <= -10%`
- Strategy constraints unchanged: no inversion, no new features, no optimizer changes, RL disabled
- `stress_cash_exposure` keeps alpha unchanged and scales post-risk gross exposure to `75%` during stress.
- Because the optimizer normalizes alpha per rebalance, scalar dampening before the optimizer does not materially change rankings or allocations.
- If dampening should matter, it must be applied as exposure scaling, risk-aversion increase, or an alpha-confidence weight inside the optimizer objective before normalization.

## Backtest Comparison

| variant               |   cagr |   sharpe |   max_dd |   dd_2020 |   dd_2022 |   stress_ic |
|:----------------------|-------:|---------:|---------:|----------:|----------:|------------:|
| baseline              | 0.1731 |   0.9172 |  -0.3706 |   -0.3706 |   -0.3365 |      0.0371 |
| sector_neutral_stress | 0.1650 |   0.9176 |  -0.3692 |   -0.3692 |   -0.2895 |      0.0249 |
| stress_cash_exposure  | 0.1606 |   0.9340 |  -0.3636 |   -0.3636 |   -0.2937 |      0.0371 |
| dampened_stress       | 0.1731 |   0.9172 |  -0.3706 |   -0.3706 |   -0.3365 |      0.0371 |

## Conditional IC

| variant               | regime   |   mean_ic |   ic_sharpe |   spread |   precision_at_20 |   n_dates |
|:----------------------|:---------|----------:|------------:|---------:|------------------:|----------:|
| baseline              | normal   |    0.0364 |      0.1296 |   0.0178 |            0.4100 |       170 |
| baseline              | stress   |    0.0371 |      0.1215 |   0.0126 |            0.4169 |        68 |
| sector_neutral_stress | normal   |    0.0364 |      0.1296 |   0.0178 |            0.4100 |       170 |
| sector_neutral_stress | stress   |    0.0249 |      0.1557 |   0.0059 |            0.4125 |        68 |
| stress_cash_exposure  | normal   |    0.0364 |      0.1296 |   0.0178 |            0.4100 |       170 |
| stress_cash_exposure  | stress   |    0.0371 |      0.1215 |   0.0126 |            0.4169 |        68 |
| dampened_stress       | normal   |    0.0364 |      0.1296 |   0.0178 |            0.4100 |       170 |
| dampened_stress       | stress   |    0.0371 |      0.1215 |   0.0126 |            0.4169 |        68 |

## Success Criteria

| variant               | maxdd_lt_32pct   | cagr_gt_16pct   | sharpe_ge_0_9   | stress_ic_improves   | dd_2020_reduces   | dd_2022_reduces   | all_pass   |
|:----------------------|:-----------------|:----------------|:----------------|:---------------------|:------------------|:------------------|:-----------|
| baseline              | False            | True            | True            | True                 | True              | True              | False      |
| sector_neutral_stress | False            | True            | True            | False                | True              | True              | False      |
| stress_cash_exposure  | False            | True            | True            | False                | True              | True              | False      |
| dampened_stress       | False            | True            | True            | False                | False             | False             | False      |

## Interpretation

- `sector_neutral_stress` is the only variant here that actually changes cross-sectional ordering under the current optimizer.
- `sector_neutral_stress` does not pass the full gate.
- `dampened_stress` should be interpreted mainly as a control because optimizer alpha normalization removes most uniform scaling effects.
- The broad stress rule does not reproduce the narrower drawdown-window alpha inversion by itself: baseline stress IC is positive in this test, while prior top drawdown windows had negative rebalance IC.
- Sector-neutral stress conditioning lowers stress IC and spread, so this formulation is not supported.
- Stress exposure scaling improves the 2020 and 2022 drawdowns but still misses the MaxDD gate; it is a risk-control lead, not an alpha-conditioning win.
