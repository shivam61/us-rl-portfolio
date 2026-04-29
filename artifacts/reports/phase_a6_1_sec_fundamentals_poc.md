# Phase A.6.1 SEC Fundamentals POC

## Purpose

Build a small real point-in-time fundamentals file from SEC company facts before investing in a full fundamentals platform.

## Output

- Canonical file: `data/fundamentals/sec_poc_canonical_fundamentals.parquet`
- Rows: `1,965`
- Tickers: `44`
- Filing date range: `2015-01-26` to `2026-04-29`

## Coverage

```csv
metric,value,covered_tickers,expected_tickers
ticker_coverage,1.0,44,44
eps_row_coverage,1.0,44,44
book_value_row_coverage,1.0,44,44
net_income_row_coverage,0.9964376590330789,44,44
shares_outstanding_row_coverage,0.9806615776081425,44,44
revenue_row_coverage,0.9541984732824428,43,44
gross_profit_row_coverage,0.3933842239185751,17,44
total_assets_row_coverage,1.0,44,44
total_debt_row_coverage,0.8661577608142493,40,44
operating_income_row_coverage,0.7989821882951654,36,44
interest_expense_row_coverage,0.8213740458015267,36,44
operating_cash_flow_row_coverage,1.0,44,44
```

## Caveats

- This is a POC, not a final fundamentals platform.
- Availability uses SEC filing dates from company facts.
- SEC company facts can include amended filings and restatements; this script keeps the latest observed value per filing date.
- Some duration fields, especially cash-flow fields, can be year-to-date in 10-Q filings. Treat A.4 results as a scale/no-scale signal, not a production decision.
- Analyst revisions and earnings-surprise fields are unavailable from SEC company facts.

## Next Step

Switch `fundamentals.provider` to `canonical_local`, point `fundamentals.path` at this file, run A.5 audit, then rerun A.4 on the same limited universe.
