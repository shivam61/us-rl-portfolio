# Phase C.3 — Portfolio Validation of simple_mean_rank

- Run date: 2026-05-01 12:19:56 UTC
- Candidate signal: `simple_mean_rank_14` — equal-weight rank percentile composite
  of 14 positive-IC features (from C.2 holdout analysis).
- Baseline signal: `vol_score` — Phase B.5 production signal.
- Portfolio harness: `b4_stress_cap_trend_boost` — unchanged from Phase B.5.
  every_2_rebalances, dynamic beta cap (0.90 − 0.20×stress), beta floor 0.50.
- Universe: sp500, evaluation 2008–2026-04-24.

## Verdict: FAIL — keep vol_score as production signal

## Phase C.3 Acceptance Gates

| gate                                | value   | target   | b5_value   | pass   |
|:------------------------------------|:--------|:---------|:-----------|:-------|
| Sharpe ≥ 1.078 (match B.5)          | 1.050   | ≥ 1.078  | 1.078      | False  |
| Sharpe ≥ 1.05 (maintain floor)      | 1.050   | ≥ 1.05   | 1.078      | False  |
| MaxDD ≥ -35% (maintain)             | -33.94% | ≥ -35%   | -32.98%    | True   |
| MaxDD ≥ -40% (hard floor)           | -33.94% | ≥ -40%   | -32.98%    | True   |
| 50 bps Sharpe ≥ 0.884               | 0.895   | ≥ 0.884  | 0.934      | True   |
| Turnover sum ≤ 100                  | 90.5    | ≤ 100    | 84.1       | True   |
| Zero rebalance-date beta violations | 0       | 0        | 0          | True   |

## Signal IC Context (from C.2)

| Signal | IC Sharpe (holdout) | Notes |
|---|---|---|
| `vol_score` | 1.6682 | Production baseline (4 low-vol features) |
| `simple_mean_rank_14` | 1.8559 | 14-feature rank composite, no model |

## Full-Period Performance Comparison (10 bps)

| Metric | simple_mean_rank | vol_score (B.5) | Delta |
|---|---|---|---|
| CAGR | 15.65% | 16.04% | -0.39% |
| Sharpe | 1.050 | 1.078 | -0.028 |
| MaxDD | -33.94% | -32.98% | -0.96% |
| Turnover sum | 90.5 | 84.1 | +6.4 |

## Cost Sensitivity (simple_mean_rank)

|   cost_bps |   cagr |   sharpe |   max_dd |
|-----------:|-------:|---------:|---------:|
|    10.0000 | 0.1565 |   1.0498 |  -0.3394 |
|    25.0000 | 0.1480 |   0.9920 |  -0.3455 |
|    50.0000 | 0.1338 |   0.8954 |  -0.3555 |

## Cost Sensitivity (vol_score B.5)

|   cost_bps |   cagr |   sharpe |   max_dd |
|-----------:|-------:|---------:|---------:|
|    10.0000 | 0.1604 |   1.0780 |  -0.3298 |
|    25.0000 | 0.1524 |   1.0240 |  -0.3298 |
|    50.0000 | 0.1392 |   0.9339 |  -0.3298 |

## Regime Breakdown (10 bps, simple_mean_rank vs vol_score)

| regime                |   cagr_smr |   sharpe_smr |   max_dd_smr |   n_days |   cagr_vol |   sharpe_vol |   max_dd_vol |   delta_sharpe |
|:----------------------|-----------:|-------------:|-------------:|---------:|-----------:|-------------:|-------------:|---------------:|
| 2008 financial crisis |    -0.0561 |      -0.2696 |      -0.3394 |      505 |     0.1099 |       0.5417 |      -0.1801 |        -0.8112 |
| 2015-16 vol stress    |     0.0988 |       0.7612 |      -0.1161 |      402 |     0.0763 |       0.5675 |      -0.1627 |         0.1937 |
| 2020 COVID            |     0.2820 |       1.0891 |      -0.2268 |      253 |     0.1240 |       0.4353 |      -0.3298 |         0.6538 |
| 2022 bear market      |    -0.0404 |      -0.2534 |      -0.1174 |      251 |    -0.1375 |      -0.7278 |      -0.1711 |         0.4744 |
| 2023-2026 recovery    |     0.3114 |       2.3388 |      -0.1286 |      830 |     0.3094 |       2.4733 |      -0.1055 |        -0.1345 |
| full 2008-2026        |     0.1565 |       1.0498 |      -0.3394 |     4607 |     0.1604 |       1.0780 |      -0.3298 |        -0.0281 |

## Beta Compliance (simple_mean_rank, rebalance dates)

- n_rebalance_dates: 120
- n_gate_violations: 0
- avg_beta_after: 0.7079
- avg_dynamic_cap: 0.8294
- min_dynamic_cap: 0.7006
- compliance_rate: 1.0000

## Attribution: Selected Names Overlap (simple_mean_rank vs vol_score)

- Average overlap (% of SMR selection shared with vol_score): 22.1%
- Average Jaccard similarity: 0.131

| date                |   n_smr |   n_vol |   overlap_count |   overlap_pct_smr |   jaccard |
|:--------------------|--------:|--------:|----------------:|------------------:|----------:|
| 2008-01-07 00:00:00 |      20 |      20 |               6 |             0.300 |     0.176 |
| 2008-03-03 00:00:00 |      20 |      20 |               7 |             0.350 |     0.212 |
| 2008-04-28 00:00:00 |      20 |      20 |               4 |             0.200 |     0.111 |
| 2008-06-23 00:00:00 |      20 |      20 |               0 |             0.000 |     0.000 |
| 2008-08-18 00:00:00 |      20 |      20 |               1 |             0.050 |     0.026 |
| 2008-10-13 00:00:00 |      20 |      20 |               3 |             0.150 |     0.081 |
| 2008-12-08 00:00:00 |      20 |      20 |               0 |             0.000 |     0.000 |
| 2009-02-02 00:00:00 |      20 |      20 |               2 |             0.100 |     0.053 |
| 2009-03-30 00:00:00 |      20 |      20 |               4 |             0.200 |     0.111 |
| 2009-05-26 00:00:00 |      20 |      20 |               5 |             0.250 |     0.143 |

## Attribution: Sector Exposure Shift (stock allocation only)

| sector   |   avg_weight_smr |   avg_weight_vol |   delta |
|:---------|-----------------:|-----------------:|--------:|
| XLV      |           0.0958 |           0.0633 |  0.0325 |
| XLC      |           0.0667 |           0.0437 |  0.0229 |
| XLI      |           0.0888 |           0.0763 |  0.0125 |
| XLK      |           0.3146 |           0.3108 |  0.0038 |
| XLP      |           0.0104 |           0.0075 |  0.0029 |
| XLY      |           0.1692 |           0.1683 |  0.0008 |
| XLU      |           0.0079 |           0.0079 |  0.0000 |
| XLRE     |           0.0054 |           0.0079 | -0.0025 |
| XLB      |           0.0529 |           0.0613 | -0.0083 |
| XLE      |           0.0721 |           0.0917 | -0.0196 |
| XLF      |           0.1163 |           0.1613 | -0.0450 |

## Features Used (simple_mean_rank_14)

  1. `beta_to_spy_63d`
  2. `downside_vol_63d`
  3. `volatility_21d`
  4. `volatility_63d`
  5. `liquidity_rank`
  6. `avg_dollar_volume_63d`
  7. `ret_12m_ex_1m`
  8. `ret_12m`
  9. `sector_rel_momentum_6m`
  10. `trend_consistency`
  11. `ma_50_200_ratio`
  12. `above_200dma`
  13. `ret_6m_adj`
  14. `ret_6m`

## Decision

- FAIL: gates not met: Sharpe ≥ 1.078 (match B.5), Sharpe ≥ 1.05 (maintain floor).
- Keep `vol_score` as production signal.
- Freeze LightGBM / feature-selection work for this alpha family.
- Proceed to Phase D with existing vol_score.

## Output Files

- `artifacts/reports/phase_c3_signal_validation.md`
- `artifacts/reports/c3_portfolio_comparison.csv`
- `artifacts/reports/c3_regime_breakdown.csv`
- `artifacts/reports/c3_selected_overlap.csv`
- `artifacts/reports/c3_cost_sensitivity.csv`
