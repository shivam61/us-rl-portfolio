# Phase E.6 — RL Regime Controller v2 vs B.5 Five-Way Comparison

- Run date: 2026-05-04 09:44:35 UTC
- Holdout window: 2019-01-01 → 2026-04-24
- B.5 holdout benchmark (D.0): Sharpe 1.270, MaxDD -32.98%
- Primary comparison cost: 10 bps (same basis for all policies)
- Cost methodology: B.5 locked via compute_net_returns; RL policies via post-hoc turnover.
- Phase E no-op note: no-op removes trend sleeve (equity=1, trend=0). Expect Sharpe
  below B.5 locked (which keeps TLT/GLD/UUP ~20–30% of portfolio).

## Verdict: **REJECT trained Phase E RL — keep B.5 as production system**

## Policy Comparison (10 bps, holdout 2019–2026)

| Policy                    | CAGR   | Sharpe                             | MaxDD   | Avg equity   |
|:--------------------------|:-------|:-----------------------------------|:--------|:-------------|
| B.5 locked                | 20.69% | 1.270                              | -32.98% | N/A          |
| RL no-op                  | N/A    | N/A                                | N/A     | N/A          |
| Rule-based controller     | N/A    | N/A                                | N/A     | N/A          |
| Random bounded (50 seeds) | N/A    | N/A (mean) / N/A (med) / N/A (p75) | N/A     | —            |
| Trained Phase E RL        | 17.79% | 1.296                              | -24.48% | 0.406        |

## Random Baseline Distribution (50 seeds, 10 bps)

| Stat    | Sharpe   |
|:--------|:---------|
| Mean    | N/A      |
| Median  | N/A      |
| p25     | N/A      |
| p75     | N/A      |
| p90     | N/A      |
| p95     | N/A      |
| Std dev | N/A      |

> Promotion uses **median** as hard minimum and **p75** as preferred.
> p90/p95 are reported for context only.

## Cost Sensitivity (all policies, post-hoc cost adjustment)

|   cost_bps |   B.5 locked |   Trained RL |
|-----------:|-------------:|-------------:|
|    10.0000 |       1.2701 |       1.2957 |
|    25.0000 |       1.2195 |       1.2521 |
|    50.0000 |       1.1349 |       1.1790 |

## Regime Breakdown

| regime             |   B.5 locked Sharpe |   B.5 locked MaxDD |   RL no-op Sharpe |   RL no-op MaxDD |   Trained RL Sharpe |   Trained RL MaxDD |
|:-------------------|--------------------:|-------------------:|------------------:|-----------------:|--------------------:|-------------------:|
| 2019 bull market   |              2.6491 |            -0.0570 |               nan |              nan |              3.1835 |            -0.0542 |
| 2020 COVID crash   |              0.4353 |            -0.3298 |               nan |              nan |              0.6316 |            -0.2448 |
| 2021 recovery      |              2.4201 |            -0.0657 |               nan |              nan |              1.5930 |            -0.0693 |
| 2022 bear market   |             -0.7278 |            -0.1711 |               nan |              nan |             -0.6058 |            -0.1289 |
| 2023–2026 recovery |              2.4733 |            -0.1055 |               nan |              nan |              2.2556 |            -0.0918 |

## Promotion Gate Evaluation

| gate                                            | value                       | pass   | required    |
|:------------------------------------------------|:----------------------------|:-------|:------------|
| Path A: Sharpe ≥ 1.270 AND MaxDD ≥ -32.98%      | Sharpe=1.296, MaxDD=-24.48% | True   | either path |
| Path B: Sharpe ≥ 1.240 AND MaxDD ≥ -31.48%      | Sharpe=1.296, MaxDD=-24.48% | True   | either path |
| 50 bps Sharpe ≥ 0.90                            | 1.179                       | True   | yes         |
| Beats RL no-op Sharpe (N/A)                     | 1.296                       | False  | yes         |
| Beats random median Sharpe (N/A) [hard minimum] | 1.296                       | False  | yes         |
| Beats random p75 Sharpe (N/A) [preferred]       | 1.296                       | False  | preferred   |
| Beats rule-based controller Sharpe (N/A)        | 1.296                       | False  | yes         |
| Hard rejection: MaxDD ≥ -35% (no blowup)        | -24.48%                     | True   | yes         |

## Notes

- Path A = clear win: Sharpe ≥ B.5 holdout (1.270) AND MaxDD ≥ B.5 holdout MaxDD (-32.98%).
- Path B = tail improvement: Sharpe ≥ 1.240 AND MaxDD ≥ −31.48% (1.5pp better than B.5).
- Both paths require 50 bps Sharpe ≥ 0.90, beat no-op, beat random median, beat rule-based.
- Random p75 gate: preferred; conditional-pass if RL beats median but not p75.
- Hard rejections: MaxDD < −35%.

## Artifacts

- `artifacts/reports/phase_e6_rl_evaluation.md` — this file
- `artifacts/reports/e6_policy_comparison.csv`
- `artifacts/reports/e6_regime_breakdown.csv`
- `artifacts/reports/e6_promotion_gates.csv`
- `artifacts/reports/e6_random_distribution.csv`
