# Phase B.0 Baseline Guard

- Run date: 2026-04-30 07:14:44 UTC
- Purpose: lock the Phase A.7.3 baseline before Phase B portfolio stabilization.
- Baseline expression: `vol_top_20` + `trend_3m_6m_long_cash`, `50/50 + k=0.30 + 50/50 stress`, 10 bps cost.
- Scope: no `volatility_score` changes, no new alpha, no historical membership import, RL disabled.

## Baseline Lock

| universe      | cohort                |   cagr |   sharpe |   max_dd |   volatility |   turnover_sum |   avg_gross |   max_gross |   avg_candidates |   min_candidates |   avg_score_non_null |   min_score_non_null |   avg_selected |   min_selected | passes_drawdown   | passes_sharpe   | passes_selection_depth   |
|:--------------|:----------------------|-------:|---------:|---------:|-------------:|---------------:|------------:|------------:|-----------------:|-----------------:|---------------------:|---------------------:|---------------:|---------------:|:------------------|:----------------|:-------------------------|
| sp100_sample  | baseline_current_mask | 0.1822 |   1.7393 |  -0.1700 |       0.1048 |       203.9920 |      1.1392 |      1.3750 |          41.3305 |               39 |              40.6360 |                   36 |        20.0000 |             20 | True              | True            | True                     |
| sp500_dynamic | baseline_current_mask | 0.2351 |   1.5376 |  -0.2636 |       0.1529 |       230.7480 |      1.1392 |      1.3750 |         286.9749 |              128 |             286.6360 |                  128 |        20.0000 |             20 | True              | True            | True                     |

## Data Window Guard

| universe_path               | universe      |   configured_tickers | first_price_date   | last_price_date   | first_mask_date   | last_mask_eval_date   | last_nonzero_active_date   | recommended_validation_end   |   zero_active_days |   trailing_zero_active_days |   active_min_nonzero |   active_median |   active_latest | needs_clip_or_mask_refresh   |
|:----------------------------|:--------------|---------------------:|:-------------------|:------------------|:------------------|:----------------------|:---------------------------|:-----------------------------|-------------------:|----------------------------:|---------------------:|----------------:|----------------:|:-----------------------------|
| config/universes/sp100.yaml | sp100_sample  |                   44 | 2006-01-03         | 2026-04-29        | 2008-01-02        | 2026-04-29            | 2026-04-29                 | 2026-04-29                   |                  0 |                           0 |                   39 |         41.0000 |              39 | False                        |
| config/universes/sp500.yaml | sp500_dynamic |                  503 | 2006-01-03         | 2026-04-29        | 2008-01-02        | 2026-04-29            | 2026-04-24                 | 2026-04-24                   |                  3 |                           3 |                  127 |        270.0000 |               0 | True                         |

## Decision

- WATCH: Phase B can proceed, but production validation must clip to `recommended_validation_end` or refresh the PIT mask before using trailing dates.
- Use these baseline rows as the comparison anchor for all Phase B turnover, optimizer, and risk-engine experiments.

## Output Files

- `artifacts/reports/phase_b0_baseline_guard.md`
- `artifacts/reports/phase_b0_data_window_guard.csv`
- `artifacts/reports/phase_b0_baseline_lock.csv`
