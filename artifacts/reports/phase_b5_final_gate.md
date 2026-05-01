# Phase B.5 — Final Phase B Gate Run

- Run date: 2026-05-01 06:09:46 UTC
- Candidate: `b4_stress_cap_trend_boost` (Phase B.4 promoted).
- Universe: sp500, clipped to `2026-04-24`, evaluation window 2008–2026.
- Cost at reporting: 10 bps (cost sweep at 10/25/50 bps below).
- Scope: no `volatility_score` changes, no new alpha, RL disabled.

## Verdict: PASS — proceed to Phase C

## Phase B Exit Gates

| gate                                             | value   | target   | pass   |
|:-------------------------------------------------|:--------|:---------|:-------|
| MaxDD < 40%                                      | -32.98% | < −40%   | True   |
| Sharpe > 0.9 at 50 bps                           | 0.934   | >= 0.90  | True   |
| Sharpe > 0.9 at 25 bps                           | 1.024   | >= 0.90  | True   |
| Sharpe > 0.9 at 10 bps                           | 1.078   | >= 0.90  | True   |
| Beats equal-weight Sharpe at 10 bps (EW = 0.619) | 1.078   | >= 0.619 | True   |
| Max gross <= 1.5                                 | 1.500   | <= 1.500 | True   |
| Zero rebalance-date beta band violations         | 0       | 0        | True   |
| Turnover stable (sum <= 90)                      | 84.12   | <= 90.0  | True   |

## Full-Period Performance (10 bps)

| Metric | Value |
|---|---|
| CAGR | 16.04% |
| Sharpe | 1.078 |
| MaxDD | -32.98% |
| Max gross | 1.500 |
| Turnover sum | 84.12 |
| Min selected names | 21 |

## Cost Sensitivity

|   cost_bps |   cagr |   sharpe |   max_dd | beats_equal_weight   | passes_sharpe_gate   |
|-----------:|-------:|---------:|---------:|:---------------------|:---------------------|
|    10.0000 | 0.1604 |   1.0780 |  -0.3298 | True                 | True                 |
|    25.0000 | 0.1524 |   1.0240 |  -0.3298 | True                 | True                 |
|    50.0000 | 0.1392 |   0.9339 |  -0.3298 | True                 | True                 |

## Regime Breakdown (10 bps)

| regime                | start      | end        |    cagr |   sharpe |   max_dd |   n_days |
|:----------------------|:-----------|:-----------|--------:|---------:|---------:|---------:|
| 2008 financial crisis | 2008-01-01 | 2009-12-31 |  0.1099 |   0.5417 |  -0.1801 |      505 |
| 2015–16 vol stress    | 2015-06-01 | 2016-12-31 |  0.0763 |   0.5675 |  -0.1627 |      402 |
| 2020 COVID            | 2020-01-01 | 2020-12-31 |  0.1240 |   0.4353 |  -0.3298 |      253 |
| 2022 bear market      | 2022-01-01 | 2022-12-31 | -0.1375 |  -0.7278 |  -0.1711 |      251 |
| 2023–2026 recovery    | 2023-01-01 | 2026-04-24 |  0.3094 |   2.4733 |  -0.1055 |      830 |
| full 2008–2026        | 2008-01-01 | 2026-04-24 |  0.1604 |   1.0780 |  -0.3298 |     4607 |

Notes:
- 2008 and 2022 Sharpe are expected to be below 1.0 (confirmed from B.3.1/B.4 history); treat as capital-preservation regimes.
- MaxDD gate applies full-period only.

## Beta Compliance (rebalance dates)

- n_rebalance_dates: 120
- n_gate_violations: 0
- avg_beta_after: 0.7701
- min_beta_after: 0.5000
- max_beta_after: 0.8992
- avg_dynamic_cap: 0.8294
- min_dynamic_cap: 0.7006
- compliance_rate: 1.0000

## Phase B Attribution Chain

| step                                           | cagr   |   sharpe | max_dd   |   turnover | note                                                            |
|:-----------------------------------------------|:-------|---------:|:---------|-----------:|:----------------------------------------------------------------|
| A.7.3 unlagged (research headline)             | 23.51% |    1.538 | -26.36%  |      nan   | same-day signal/return alignment; not a valid backtest baseline |
| B.1 production open/next-day (10 bps)          | 17.56% |    1.116 | -26.98%  |      230.7 | execution lag + realistic simulator costs                       |
| B.2 every_2_rebalances (10 bps)                | 18.33% |    1.144 | -33.69%  |       89.6 | turnover reduction −61.2% vs B.1                                |
| B.3.1 band_50_90 (10 bps)                      | 16.49% |    1.075 | -33.69%  |       85.4 | beta compliance [0.50, 0.90] at rebalance dates                 |
| B.4 stress_cap_trend_boost (10 bps) — promoted | 16.04% |    1.078 | -32.98%  |       84.1 | dynamic beta_cap = 0.90 − 0.20 × stress + trend boost           |

## Decision

- All Phase B exit criteria pass.
- Candidate `b4_stress_cap_trend_boost`: CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`, turnover `84.12`, avg dynamic beta cap `0.829` (min `0.700`).
- Proceed to Phase C — model refinement: LightGBM tuning and feature improvements.

## Output Files

- `artifacts/reports/phase_b5_final_gate.md`
- `artifacts/reports/phase_b5_cost_sensitivity.csv`
- `artifacts/reports/phase_b5_regime_breakdown.csv`
- `artifacts/reports/phase_b5_attribution.csv`
- `artifacts/reports/phase_b5_beta_compliance.csv`
