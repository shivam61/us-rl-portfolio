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
| Fundamentals | `src/data/providers/canonical_fundamental_provider.py` | canonical parquet/CSV path from `config/base.yaml` | Canonical local contract for research-grade fundamental data |
| Simulated fundamentals | `src/data/providers/fundamental_provider.py` | `data/raw/fundamentals_{universe}.parquet` | Plumbing/testing only; not research-grade alpha |

## Canonical Local Fundamentals Contract

The canonical local parquet/CSV adapter is the stable boundary between vendor data and research.

Every future source must normalize into this schema before feature generation:

```text
filing_date
ticker
eps
book_value
net_income
shares_outstanding
revenue
gross_profit
total_assets
total_debt
operating_income
interest_expense
operating_cash_flow
```

Optional columns:

```text
cash_and_equivalents
total_equity
capex
free_cash_flow
ebitda
analyst_eps_revision_1m
analyst_eps_revision_3m
earnings_surprise
```

`filing_date` must be the date the information became available to the market. Do not use fiscal period end date as a proxy unless a conservative filing lag has been applied upstream and documented.

Configure the provider in `config/base.yaml`:

```yaml
fundamentals:
  provider: "canonical_local"
  path: "data/fundamentals/canonical_fundamentals.parquet"
  min_ticker_coverage: 0.80
  require_pit_dates: true
```

Use `provider: "simulated"` only for plumbing tests.

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

## Simulated Fundamental Schema

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

These fields are simulated unless replaced by the canonical local provider. Treat them as a schema and pipeline test, not an investable signal source.

## Adding A New Data Source

1. Write a source-specific adapter that outputs the canonical local schema.
2. Include an availability date per row as `filing_date`.
3. Save the normalized file as parquet or CSV.
4. Point `fundamentals.path` at that file with `provider: "canonical_local"`.
5. Run the A.5 audit and fix coverage/schema failures before research.
6. Add engineered features in `src/features/`, with a one-day lag.
7. Add engineered-feature coverage checks to the A.5 audit.
8. Update this document with raw fields, engineered features, and known caveats.

For simple local vendor exports, use the canonical preparation utility:

```bash
.venv/bin/python scripts/prepare_canonical_fundamentals.py \
  --input data/vendor/fundamentals_export.csv \
  --output data/fundamentals/canonical_fundamentals.parquet \
  --column-map config/fundamental_column_map.json
```

The optional JSON column map should map source columns to canonical names, for example:

```json
{
  "symbol": "ticker",
  "acceptedDate": "filing_date",
  "totalDebt": "total_debt",
  "cashFlowFromOperations": "operating_cash_flow"
}
```

After preparing the canonical file, switch `fundamentals.provider` to `canonical_local`, run the A.5 audit, and only then rerun A.4.

## SEC Company Facts POC

If no vendor data is available, use the bounded SEC proof-of-concept before building a full fundamentals platform:

```bash
SEC_USER_AGENT="your-name your-email@example.com" \
.venv/bin/python scripts/build_sec_fundamentals_poc.py \
  --config config/base.yaml \
  --universe config/universes/sp100.yaml \
  --max-tickers 44 \
  --start-date 2015-01-01
```

This writes:

- `data/fundamentals/sec_poc_canonical_fundamentals.parquet`
- `artifacts/reports/phase_a6_1_sec_fundamentals_poc.md`
- `artifacts/reports/phase_a6_1_sec_fundamentals_coverage.csv`

The POC uses SEC filing dates as `filing_date` and normalizes available company-facts tags into the canonical schema. Treat it as a scale/no-scale test for the defensive sleeve, not a finished data product. Known limitations: amended/restated facts, imperfect quarterly cash-flow treatment, and no analyst revisions.

Scale SEC ingestion only if the SP100 real-PIT A.4 rerun improves sleeve correlation, Sharpe, or drawdown enough to justify the larger data-engineering effort.

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

## Phase H — Live Paper Trading Data And Features

This section documents what data and features the live `rl_e7` policy actually consumes during
Phase H paper trading. It is intentionally separate from the research/backtest sections above
because the live pipeline has tighter freshness requirements and a narrower feature scope.

### Live Data Sources

| Source | Provider | Fetch cadence | Output |
|---|---|---|---|
| Prices / volume (all tickers + SPY + TLT) | `yfinance` via `src/data/providers/yfinance_provider.py` | Daily incremental append after 16:05 ET | `data/raw/{ticker}.parquet` |
| Sector ETF prices (vol_score inputs) | Same yfinance provider | Same daily append | `data/raw/{sector_etf}.parquet` |
| Drift flags (model health) | `run_drift_monitor_g3.py` | Daily | `data/drift/flags.parquet` |

**No fundamentals in the live signal.** The `rl_e7` policy state vector is built entirely from
price-derived features. Fundamental features exist in the research pipeline
(`canonical_fundamental_provider.py`) but are not wired into `run_prod_signal.py`.

### Live Feature Build

Step 0 of the daily ops loop (`refresh_market_data.py`) appends only missing trading days to
each `data/raw/{ticker}.parquet`, then calls `build_features.py` if any ticker was updated.
Three feature files are written:

| Artifact | Generator class | Content |
|---|---|---|
| `data/features/stock_features.parquet` | `StockFeatureGenerator` | Per-ticker price features (see table below) |
| `data/features/sector_features.parquet` | `SectorFeatureGenerator` | Per-sector vol_score and momentum |
| `data/features/macro_features.parquet` | `MacroFeatureGenerator` | SPY-level regime and vol features |

All features are shifted by 1 business day inside `StockFeatureGenerator` (leakage guard).
Features built on day T use prices through T-1 and are safe for signal generation on T.

### Stock Features (`data/features/stock_features.parquet`)

| Feature | Window | Description |
|---|---|---|
| `ret_1m`, `ret_3m`, `ret_6m` | 21 / 63 / 126d | Price momentum |
| `volatility_21d`, `volatility_63d` | 21 / 63d | Annualised realised vol |
| `max_drawdown_63d` | 63d rolling | Drawdown from rolling max |
| `beta_to_spy_63d` | 63d | Rolling beta vs SPY |
| `rs_vs_spy` | 63d | Relative strength vs SPY |
| `ret_zscore_21d` | 21d | Short-term mean-reversion z-score |
| `gap_overnight` | 1d | Open-vs-prior-close gap |
| `mom_stability_3m` | 63d | Fraction of positive daily returns |
| `sector_rel_momentum_3m`, `sector_rel_momentum_6m` | 63 / 126d | Return minus sector median |

### Macro Features (`data/features/macro_features.parquet`)

| Feature | Description |
|---|---|
| `spy_ret_1m`, `spy_ret_6m` | SPY 1-month and 6-month returns |
| `spy_drawdown` | SPY drawdown from 252d rolling max |
| `realized_market_vol_63d` | SPY 63d annualised vol |
| `market_regime` | Categorical: CRASH / HIGH_VOL / TRENDING / SIDEWAYS |

### RL State Vector (42 elements — `rl_e7` policy input)

Built by `src/rl/state_builder.py::build_state_v2` at signal time. No additional fetch occurs
at state-build time — all inputs come from already-refreshed parquet files.

| Index | Feature | Source |
|---|---|---|
| 0 | `vol_score` (portfolio-level) | `data/features/stock_features.parquet` |
| 1 | SPY 252d drawdown from rolling max | Price series (computed inline) |
| 2 | Yield curve proxy: z-scored TLT−SPY 63d momentum | Price series (computed inline) |
| 3 | Stress score | `build_stress_series` (inline from prices) |
| 4–14 | Median `volatility_score` per GICS sector (11 sectors) | `data/features/sector_features.parquet` |
| 15–25 | B.5 stock-sleeve weight summed per sector, normalised (11 sectors) | Allocation state |
| 26 | Current NAV drawdown from peak | `data/paper_trading/positions_latest.parquet` |
| 27–41 | (reserved / padding to 42) | — |

### Data Freshness Requirements

| Check | Requirement | Where enforced |
|---|---|---|
| Prices must cover signal date T | `data/raw/{ticker}.parquet` max date == T | `refresh_market_data.py` Step 0 |
| Features must be rebuilt after any price append | `data/features/stock_features.parquet` mtime ≥ last price file mtime | `refresh_market_data.py` Step 0 |
| Signal must run after 16:05 ET | T close prices available | `config/paper_trading.yaml` `signal_time_et` |
| Orders submitted before 09:35 ET T+1 | Fills simulate T+1 open | `config/paper_trading.yaml` `order_submit_time_et` |

Running `scripts/run_daily_paper_ops.py --date YYYY-MM-DD` after 16:05 ET satisfies all four
requirements automatically. Do not skip Step 0 or run the signal before market close.

### What Is Not In The Live Signal

- **Fundamentals:** Not fetched during daily ops. `canonical_fundamental_provider.py` and
  `simulated_fundamental_provider.py` are research-only. Adding fundamentals to the live signal
  requires wiring a real-time source, adding lag handling, and a separate H-gate coverage audit.
- **Alternative data:** No sentiment, news, or options flow in Phase H.
- **Intraday prices:** All fills simulate at next-day adjusted close. No intraday data is used.

---

## Long-Horizon Backtests And RL Scope

Current backtests start in 2006 and use a two-year warmup, so the effective evaluated period starts around 2008. That gives exposure to the global financial crisis, 2011, 2018 Q4, COVID, 2022, and the 2023-2026 recovery/AI cycle.

For future RL work, keep these constraints in mind:

- Preserve the 2006 raw start date or earlier if data quality supports it.
- Treat the first warmup window as unavailable for scoring.
- Split RL chronologically; do not random-shuffle market history.
- Reserve a true holdout such as 2019-2026 for final policy evaluation.
- Keep A.5 coverage checks by period, not just full-sample coverage, before using fundamentals in RL state features.
- Store regime labels and crisis periods explicitly so RL evaluation can report regime-conditional performance, not only full-period Sharpe.
