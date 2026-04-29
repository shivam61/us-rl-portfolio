# Phase A.5 Data Feature Audit

## Summary

| universe      |   requested_tickers |   fundamental_tickers |   fundamental_ticker_coverage_pct | raw_columns                                                                                                                                                        | engineered_columns                                                                                                                                                   | provider   |   min_ticker_coverage | coverage_pass   | canonical_required_columns_present   |
|:--------------|--------------------:|----------------------:|----------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------|----------------------:|:----------------|:-------------------------------------|
| sp100_sample  |                  44 |                    44 |                            1.0000 | filing_date,ticker,eps,book_value,net_income,shares_outstanding,revenue,gross_profit,total_assets,total_debt,operating_income,interest_expense,operating_cash_flow | pe_ratio,pb_ratio,roe,eps_growth_yoy,debt_to_assets,debt_to_equity,asset_turnover,accruals_proxy,net_debt_to_assets,interest_coverage,ocf_to_net_income,gross_margin | simulated  |                0.8000 | True            | True                                 |
| sp500_dynamic |                 503 |                   503 |                            1.0000 | filing_date,ticker,eps,book_value,net_income,shares_outstanding,revenue,gross_profit,total_assets,total_debt,operating_income,interest_expense,operating_cash_flow | pe_ratio,pb_ratio,roe,eps_growth_yoy,debt_to_assets,debt_to_equity,asset_turnover,accruals_proxy,net_debt_to_assets,interest_coverage,ocf_to_net_income,gross_margin | simulated  |                0.8000 | True            | True                                 |

## Coverage

| source              | field               |   row_coverage_pct |   ticker_coverage_pct | available   | universe      |
|:--------------------|:--------------------|-------------------:|----------------------:|:------------|:--------------|
| raw_fundamentals    | eps                 |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | book_value          |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | net_income          |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | shares_outstanding  |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | revenue             |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | gross_profit        |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | total_assets        |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | total_debt          |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | operating_income    |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | interest_expense    |             1.0000 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | operating_cash_flow |             1.0000 |                1.0000 | True        | sp100_sample  |
| engineered_features | pe_ratio            |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | pb_ratio            |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | roe                 |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | eps_growth_yoy      |             0.9347 |                1.0000 | True        | sp100_sample  |
| engineered_features | debt_to_assets      |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | debt_to_equity      |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | asset_turnover      |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | accruals_proxy      |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | net_debt_to_assets  |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | interest_coverage   |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | ocf_to_net_income   |             0.9851 |                1.0000 | True        | sp100_sample  |
| engineered_features | gross_margin        |             0.9851 |                1.0000 | True        | sp100_sample  |
| raw_fundamentals    | eps                 |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | book_value          |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | net_income          |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | shares_outstanding  |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | revenue             |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | gross_profit        |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | total_assets        |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | total_debt          |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | operating_income    |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | interest_expense    |             1.0000 |                1.0000 | True        | sp500_dynamic |
| raw_fundamentals    | operating_cash_flow |             1.0000 |                1.0000 | True        | sp500_dynamic |
| engineered_features | pe_ratio            |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | pb_ratio            |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | roe                 |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | eps_growth_yoy      |             0.9327 |                0.9980 | True        | sp500_dynamic |
| engineered_features | debt_to_assets      |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | debt_to_equity      |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | asset_turnover      |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | accruals_proxy      |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | net_debt_to_assets  |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | interest_coverage   |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | ocf_to_net_income   |             0.9864 |                1.0000 | True        | sp500_dynamic |
| engineered_features | gross_margin        |             0.9864 |                1.0000 | True        | sp500_dynamic |

## Interpretation

- Fundamental caches are universe-scoped through `cache_key=universe_config.name`.
- Engineered survivability features are produced only when their raw fields exist.
- This audit is a plumbing and coverage gate; synthetic provider output is not a substitute for real point-in-time fundamentals.
