# Phase D.0 — B.5 Holdout Baseline

- Run date: 2026-05-02 02:45:51 UTC
- System: `b4_stress_cap_trend_boost` (B.5 promoted)
- Universe: sp500
- Holdout window: 2019-01-01 → 2026-04-24
- Cost at reporting: 10.0 bps (sweep at 10/25/50 bps below)

## Purpose

This report establishes the B.5 benchmark numbers on the **holdout window only**.
The full-period Sharpe (1.078) is known from Phase B.5. This report measures the
same system on the 2019–2026-04-24 slice that RL will be evaluated on in D.6.
Any RL promotion comparison must use these numbers, not the full-period ones.

## Holdout Performance (10 bps)

| Metric | Value |
|---|---|
| CAGR | 20.69% |
| Sharpe | 1.270 |
| MaxDD | -32.98% |
| N days | 1838 |

## Cost Sensitivity (holdout window only)

|   cost_bps |   cagr |   sharpe |   max_dd |
|-----------:|-------:|---------:|---------:|
|    10.0000 | 0.2069 |   1.2701 |  -0.3298 |
|    25.0000 | 0.1986 |   1.2195 |  -0.3298 |
|    50.0000 | 0.1848 |   1.1349 |  -0.3298 |

## Regime Breakdown (10 bps, holdout sub-windows)

| regime                 | start      | end        |    cagr |   sharpe |   max_dd |   n_days |
|:-----------------------|:-----------|:-----------|--------:|---------:|---------:|---------:|
| 2019 bull market       | 2019-01-01 | 2019-12-31 |  0.2751 |   2.6491 |  -0.0570 |      252 |
| 2020 COVID crash       | 2020-01-01 | 2020-12-31 |  0.1240 |   0.4353 |  -0.3298 |      253 |
| 2021 recovery          | 2021-01-01 | 2021-12-31 |  0.2924 |   2.4201 |  -0.0657 |      252 |
| 2022 bear market       | 2022-01-01 | 2022-12-31 | -0.1375 |  -0.7278 |  -0.1711 |      251 |
| 2023–2026 recovery     | 2023-01-01 | 2026-04-24 |  0.3094 |   2.4733 |  -0.1055 |      830 |
| full holdout 2019–2026 | 2019-01-01 | 2026-04-24 |  0.2069 |   1.2701 |  -0.3298 |     1838 |

## RL Promotion Benchmarks

The following numbers are the B.5 **holdout** reference for D.6 promotion decisions:

| Metric | Holdout value | D.6 Path A gate | D.6 Path B gate |
|---|---|---|---|
| Sharpe (10 bps) | 1.270 | ≥ 1.270 | ≥ 1.240 |
| MaxDD | -32.98% | ≥ -32.98% | ≥ -31.48% |
| Sharpe (50 bps) | 1.135 | ≥ 0.900 | ≥ 0.900 |

> **Note:** Path A = clear Sharpe win (≥ B.5 holdout Sharpe AND MaxDD ≥ B.5 holdout MaxDD).
> Path B = tail improvement (Sharpe ≥ B.5 − 0.03 AND MaxDD at least 1.5pp better).
> Both paths require: 50 bps Sharpe ≥ 0.90, beats RL no-op, beats random bounded (50 seeds).

## Notes

- Full-period B.5 Sharpe (2008–2026, 10 bps): 1.078 — higher than holdout Sharpe
  because 2008 crisis weights the full period; the holdout starts in 2019 (benign)
  and includes 2020 COVID and 2022 bear. These are the hard regimes RL must navigate.
- Holdout metrics are the apples-to-apples benchmark for D.6.
- Do not use full-period B.5 metrics as D.6 comparison numbers.

## Artifacts

- `artifacts/reports/phase_d0_holdout_baseline.md` — this file
- `artifacts/reports/d0_cost_sensitivity.csv`
- `artifacts/reports/d0_regime_breakdown.csv`
