# Phase A.6.1 SEC POC A.4 Summary

## Scope

- Universe: `sp100_sample`
- Fundamentals provider: `canonical_local`
- Fundamentals file: `data/fundamentals/sec_poc_canonical_fundamentals.parquet`
- Date range in SEC POC file: 2015-01-26 to 2026-04-29
- Rows: 1,965
- Tickers: 44 / 44

This was a scale/no-scale test for whether real SEC point-in-time survivability fundamentals justify building a larger SEC fundamentals platform.

## A.5 Audit Result

- Provider: `canonical_local`
- Ticker coverage: 44 / 44
- Required canonical columns: present
- Engineered survivability features: generated
- Important caveat: original SEC `gross_profit` tag coverage was sparse in the raw POC report, even though A.5 forward-filled canonical rows provide high downstream feature coverage.

## A.4 Result

Best standalone defensive sleeves:

| Sleeve | CAGR | Sharpe | MaxDD | Realized beta |
|---|---:|---:|---:|---:|
| defensive_stability_top_50_equal_weight | 16.33% | 0.876 | -38.61% | 0.893 |
| defensive_stability_top_30_equal_weight | 16.03% | 0.838 | -41.55% | 0.872 |
| defensive_stability_top_30_beta_0_6 | 12.52% | 0.781 | -39.08% | 0.605 |

Best blends:

| Blend | CAGR | Sharpe | MaxDD | Realized beta |
|---|---:|---:|---:|---:|
| vol_top_10 + defensive_top_50_beta_0_6, 40/60 | 17.79% | 0.887 | -42.17% | 0.926 |
| vol_top_10 + defensive_top_30_beta_0_6, 40/60 | 17.74% | 0.885 | -41.62% | 0.927 |
| vol_top_10 + defensive_top_50_equal_weight, 40/60 | 19.68% | 0.866 | -43.22% | 1.100 |

Cross-sleeve correlation remained too high:

| Pair | Full corr | Rolling 252d corr | Crisis corr |
|---|---:|---:|---:|
| vol_top_10 vs defensive_top_30_beta_0_6 | 0.702 | 0.669 | 0.755 |
| vol_top_10 vs defensive_top_50_beta_0_6 | 0.707 | 0.684 | 0.753 |

Benchmark:

| Benchmark | CAGR | Sharpe | MaxDD |
|---|---:|---:|---:|
| equal_weight_universe_daily | 16.20% | 0.830 | -43.18% |
| SPY buy hold | 11.14% | 0.561 | -51.87% |

## Decision

Do not scale directly to a full SP500 SEC build yet.

The real SEC PIT defensive sleeve is economically useful on SP100: it improves drawdown versus equal weight as a standalone sleeve and produces a higher Sharpe blend than equal weight. But it still fails the core objective of creating an uncorrelated alpha stream. The best vol-defensive correlation is around 0.70 full-sample and around 0.75 in crisis windows, above the target of `<0.5` full and `<0.6` crisis.

## Next Step

Before expanding SEC ingestion to SP500/2006+, run a smaller feature-level improvement pass:

1. Remove or downweight price-risk features inside the defensive sleeve so it is less mechanically tied to the volatility sleeve.
2. Treat SEC fundamentals as standalone sub-scores: balance-sheet strength, cash-flow quality, profitability stability, and valuation buffer.
3. Re-test SP100 with a stricter no-price defensive score and beta target 0.6.
4. Scale SEC to SP500 only if correlation falls materially while standalone defensive Sharpe remains competitive.
