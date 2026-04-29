# Data And Feature Engineering

This document is the operating guide for adding data sources and features. Future experiments should update it when they add, remove, or reinterpret data fields.

## Core Rules

- Keep point-in-time semantics: raw fundamental rows must use filing/availability dates, not fiscal period end dates.
- Shift engineered features by one trading day before model or portfolio use.
- Cache raw data by source and universe/ticker set. Do not reuse a small-universe cache for sp500 validation.
- Add a coverage audit before using a new feature family in an alpha experiment.
- Separate data plumbing validation from research validation. Synthetic data can test code paths, but cannot prove alpha.

## Current Data Sources

| Source | Provider | Cache | Notes |
|---|---|---|---|
| Prices / volume | `src/data/providers/yfinance_provider.py` | `data/raw/{ticker}.parquet` | Used for price, volume, beta, volatility, drawdown, labels |
| Fundamentals | `src/data/providers/fundamental_provider.py` | `data/raw/fundamentals_{universe}.parquet` | Current provider is simulated; useful for plumbing, not research-grade alpha |

## Fundamental Cache Convention

Fundamentals must be fetched with a `cache_key`, usually `universe_config.name`:

```python
fundamentals = ingestion.fetch_universe_fundamentals(
    tickers=list(universe_config.tickers.keys()),
    start_date=base_config.backtest.start_date,
    end_date=base_config.backtest.end_date,
    cache_key=universe_config.name,
)
```

This prevents `sp500_dynamic` experiments from accidentally reusing an `sp100_sample` cache.

The old global cache name `data/raw/fundamentals.parquet` is legacy and should not be used for new experiments.

## Feature Artifact Convention

`scripts/build_features.py` writes both legacy and universe-scoped artifacts:

| Artifact | Purpose |
|---|---|
| `data/features/stock_features.parquet` | Legacy default path |
| `data/features/stock_features_{universe}.parquet` | Universe-scoped feature artifact |
| `data/features/targets.parquet` | Legacy default path |
| `data/features/targets_{universe}.parquet` | Universe-scoped target artifact |

New experiments should prefer universe-scoped artifacts when reading from disk.

## Current Fundamental Schema

The current simulated provider emits:

| Raw field | Engineered feature examples |
|---|---|
| `eps` | `pe_ratio`, `eps_growth_yoy` |
| `book_value` | `pb_ratio`, `roe`, `debt_to_equity` |
| `net_income` | `roe`, `accruals_proxy`, `ocf_to_net_income` |
| `shares_outstanding` | `pb_ratio` |
| `revenue` | `gross_margin`, `asset_turnover` |
| `gross_profit` | `gross_margin` |
| `total_assets` | `debt_to_assets`, `asset_turnover`, `accruals_proxy` |
| `total_debt` | `debt_to_assets`, `debt_to_equity`, `net_debt_to_assets` |
| `operating_income` | `interest_coverage` |
| `interest_expense` | `interest_coverage` |
| `operating_cash_flow` | `ocf_to_net_income`, `accruals_proxy` |

These fields are simulated unless replaced by a real provider. Treat them as a schema and pipeline test, not an investable signal source.

## Adding A New Data Source

1. Add a provider under `src/data/providers/`.
2. Include an availability date per row. For fundamentals, this is usually `filing_date`.
3. Add or update an ingestion method in `src/data/ingestion.py`.
4. Cache by source plus universe/ticker set.
5. Add raw-field coverage checks to `scripts/run_phase_a5_data_feature_audit.py`.
6. Add engineered features in `src/features/`, with a one-day lag.
7. Add engineered-feature coverage checks to the A.5 audit.
8. Update this document with raw fields, engineered features, and known caveats.

## Adding A New Feature

Before using a feature in research:

1. Identify the raw field and availability date.
2. Confirm coverage on both `sp100_sample` and `sp500_dynamic`.
3. Confirm the feature is lagged.
4. Confirm the feature has a clear economic interpretation.
5. Add the feature to an isolated experiment first.
6. Do not merge it into a production model until its standalone diagnostics are understood.

## Phase A.5 Audit

Run:

```bash
.venv/bin/python scripts/run_phase_a5_data_feature_audit.py \
  --config config/base.yaml \
  --universes config/universes/sp100.yaml config/universes/sp500.yaml
```

Outputs:

- `artifacts/reports/phase_a5_data_feature_audit.md`
- `artifacts/reports/phase_a5_data_feature_summary.csv`
- `artifacts/reports/phase_a5_data_feature_coverage.csv`

The audit should be run before any experiment that depends on new fundamental or alternative data.
