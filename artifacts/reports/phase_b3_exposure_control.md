# Phase B.3 Exposure-Constrained Portfolio Shaping

- Run date: 2026-05-01 04:07:43 UTC
- Baseline: B.2 `every_2_rebalances` turnover-control candidate.
- Scope: no `volatility_score` changes, no trend-signal changes, no stress-formula changes, no new alpha, RL disabled.
- Method: constraint-based scalar shaping of the existing B.2 target book; when scalar scaling cannot meet the beta floor inside gross `1.5`, apply a minimal SPY beta-floor projection. No return-maximizing optimizer is used.

## Gates

- Gross exposure must stay `<=1.5`.
- Ex-ante portfolio beta must stay in `[0.5, 0.8]` using 63-day rolling beta to SPY.
- B.2 turnover improvement should be maintained.
- Sharpe and CAGR should remain within B.2 tolerance: Sharpe no worse than `B.2 - 0.10`, CAGR drop no worse than `2` percentage points.

## Summary

| universe      | runner                                                   | execution_timing    | price_mode     | start_date   | end_date   |   cagr |   sharpe |   max_dd |   volatility |   avg_turnover_per_rebalance |   peak_turnover_per_rebalance |   turnover_sum |   total_cost |    tc_drag |   slippage_drag |   avg_cash_exposure |   min_cash_exposure |   max_target_gross |   avg_target_gross |   min_selected |   n_rebalances |   n_trades | variant                    | sleeve                     |   trade_threshold | persistence_exit_rank   | update_frequency   |   partial_rebalance |   cost_bps | project_beta   |   avg_beta_before |   avg_beta_after |   min_beta_after |   max_beta_after |   control_beta_violations_after |   daily_beta_violations_after |   control_gross_violations_after |   daily_gross_violations_after |   avg_control_scale |   min_control_scale |   turnover_vs_b2_delta |   sharpe_vs_b2_delta |   cagr_vs_b2_delta |   max_dd_vs_b2_delta | passes_b3   |
|:--------------|:---------------------------------------------------------|:--------------------|:---------------|:-------------|:-----------|-------:|---------:|---------:|-------------:|-----------------------------:|------------------------------:|---------------:|-------------:|-----------:|----------------:|--------------------:|--------------------:|-------------------:|-------------------:|---------------:|---------------:|-----------:|:---------------------------|:---------------------------|------------------:|:------------------------|:-------------------|--------------------:|-----------:|:---------------|------------------:|-----------------:|-----------------:|-----------------:|--------------------------------:|------------------------------:|---------------------------------:|-------------------------------:|--------------------:|--------------------:|-----------------------:|---------------------:|-------------------:|---------------------:|:------------|
| sp500_dynamic | b2_every_2_no_projection_every_2_rebalances_cost_10bps   | next_day_weight_lag | adj_close_fast | 2008-01-02   | 2026-04-24 | 0.1833 |   1.1438 |  -0.3369 |       0.1603 |                       0.7468 |                        1.9400 |        89.6215 |   26050.8450 | 26050.8450 |          0.0000 |             -0.1329 |             -0.3462 |             1.3462 |             1.1329 |             21 |            120 |       3704 | b2_every_2_no_projection   | b2_every_2_no_projection   |            0.0000 |                         | every_2_rebalances |              1.0000 |    10.0000 | False          |            0.8619 |           0.8619 |           0.1741 |           1.4434 |                              90 |                          3323 |                                0 |                              0 |              1.0000 |              1.0000 |                -0.0000 |              -0.0000 |             0.0000 |               0.0000 | False       |
| sp500_dynamic | b3_every_2_beta_projection_every_2_rebalances_cost_10bps | next_day_weight_lag | adj_close_fast | 2008-01-02   | 2026-04-24 | 0.1550 |   1.0686 |  -0.3128 |       0.1451 |                       0.6806 |                        1.8796 |        81.6714 |   17381.2773 | 17381.2773 |          0.0000 |              0.0047 |             -0.5000 |             1.5000 |             0.9953 |             21 |            120 |       3747 | b3_every_2_beta_projection | b3_every_2_beta_projection |            0.0000 |                         | every_2_rebalances |              1.0000 |    10.0000 | True           |            0.8619 |           0.7134 |           0.3224 |           0.9828 |                               0 |                          1468 |                                0 |                              0 |              0.8875 |              0.5626 |                -7.9501 |              -0.0752 |            -0.0283 |               0.0241 | False       |

## Interpretation

- Projection satisfies rebalance-date gross and beta constraints, with Sharpe drift `-0.075` and CAGR drift `-2.83%` versus B.2.
- B.3 gate status: FAIL/WATCH because CAGR drop exceeds 2 percentage points.

## Remaining Violations

| date                | variant                  | is_control_date   |   gross_after |   beta_after |   scale | projection_reason   | gross_violation_after   | beta_violation_after   |
|:--------------------|:-------------------------|:------------------|--------------:|-------------:|--------:|:--------------------|:------------------------|:-----------------------|
| 2008-01-07 00:00:00 | b2_every_2_no_projection | True              |        0.9480 |       0.4112 |  1.0000 | none                | False                   | True                   |
| 2008-03-03 00:00:00 | b2_every_2_no_projection | True              |        0.8878 |       0.4166 |  1.0000 | none                | False                   | True                   |
| 2008-06-23 00:00:00 | b2_every_2_no_projection | True              |        0.5983 |       0.4021 |  1.0000 | none                | False                   | True                   |
| 2008-08-18 00:00:00 | b2_every_2_no_projection | True              |        1.3391 |       0.9200 |  1.0000 | none                | False                   | True                   |
| 2008-10-13 00:00:00 | b2_every_2_no_projection | True              |        0.9764 |       0.4399 |  1.0000 | none                | False                   | True                   |
| 2008-12-08 00:00:00 | b2_every_2_no_projection | True              |        0.7418 |       0.3452 |  1.0000 | none                | False                   | True                   |
| 2009-02-02 00:00:00 | b2_every_2_no_projection | True              |        0.9635 |       0.4538 |  1.0000 | none                | False                   | True                   |
| 2009-05-26 00:00:00 | b2_every_2_no_projection | True              |        0.6674 |       0.9002 |  1.0000 | none                | False                   | True                   |
| 2009-07-20 00:00:00 | b2_every_2_no_projection | True              |        0.7387 |       1.0058 |  1.0000 | none                | False                   | True                   |
| 2009-09-14 00:00:00 | b2_every_2_no_projection | True              |        1.0563 |       0.8511 |  1.0000 | none                | False                   | True                   |
| 2009-11-09 00:00:00 | b2_every_2_no_projection | True              |        1.0700 |       0.9646 |  1.0000 | none                | False                   | True                   |
| 2010-01-04 00:00:00 | b2_every_2_no_projection | True              |        0.7838 |       1.0510 |  1.0000 | none                | False                   | True                   |
| 2010-03-01 00:00:00 | b2_every_2_no_projection | True              |        1.3160 |       0.9493 |  1.0000 | none                | False                   | True                   |
| 2010-04-26 00:00:00 | b2_every_2_no_projection | True              |        1.2987 |       1.0879 |  1.0000 | none                | False                   | True                   |
| 2010-06-21 00:00:00 | b2_every_2_no_projection | True              |        1.0428 |       0.3724 |  1.0000 | none                | False                   | True                   |
| 2010-08-16 00:00:00 | b2_every_2_no_projection | True              |        0.8804 |       0.3765 |  1.0000 | none                | False                   | True                   |
| 2010-12-06 00:00:00 | b2_every_2_no_projection | True              |        0.8818 |       1.0014 |  1.0000 | none                | False                   | True                   |
| 2011-01-31 00:00:00 | b2_every_2_no_projection | True              |        0.9558 |       1.0550 |  1.0000 | none                | False                   | True                   |
| 2011-03-28 00:00:00 | b2_every_2_no_projection | True              |        1.0561 |       1.0323 |  1.0000 | none                | False                   | True                   |
| 2011-05-23 00:00:00 | b2_every_2_no_projection | True              |        1.2922 |       0.8049 |  1.0000 | none                | False                   | True                   |
| 2011-07-18 00:00:00 | b2_every_2_no_projection | True              |        1.3103 |       0.8137 |  1.0000 | none                | False                   | True                   |
| 2011-09-12 00:00:00 | b2_every_2_no_projection | True              |        0.8531 |       0.2479 |  1.0000 | none                | False                   | True                   |
| 2011-11-07 00:00:00 | b2_every_2_no_projection | True              |        1.2178 |       0.4630 |  1.0000 | none                | False                   | True                   |
| 2012-02-27 00:00:00 | b2_every_2_no_projection | True              |        1.2820 |       0.8702 |  1.0000 | none                | False                   | True                   |
| 2012-08-13 00:00:00 | b2_every_2_no_projection | True              |        1.2512 |       0.8894 |  1.0000 | none                | False                   | True                   |

## Decision

- FAIL/WATCH: projection satisfies rebalance-date exposure constraints, but no B.3 variant stays within all B.2 performance tolerances.

## Output Files

- `artifacts/reports/phase_b3_exposure_control.md`
- `artifacts/reports/constraint_violations.csv`
- `artifacts/reports/beta_tracking.csv`
- `artifacts/reports/gross_exposure.csv`
