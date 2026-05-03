# Phase E.6 — RL Regime Controller v2 vs B.5 Five-Way Comparison

- Run date: 2026-05-03 06:11:27 UTC
- Holdout window: 2019-01-01 → 2026-04-24
- B.5 holdout benchmark (D.0): Sharpe 1.270, MaxDD -32.98%
- Primary comparison cost: 10 bps (same basis for all policies)
- Cost methodology: B.5 locked via compute_net_returns; RL policies via post-hoc turnover.
- Phase E no-op note: no-op removes trend sleeve (equity=1, trend=0). Expect Sharpe
  below B.5 locked (which keeps TLT/GLD/UUP ~20–30% of portfolio).

## Verdict: **CONDITIONAL PROMOTE — CONDITIONAL: beats random median but not p75**

## Policy Comparison (10 bps, holdout 2019–2026)

| Policy                    | CAGR   | Sharpe                                   | MaxDD   | Avg equity   |
|:--------------------------|:-------|:-----------------------------------------|:--------|:-------------|
| B.5 locked                | 20.69% | 1.270                                    | -32.98% | N/A          |
| RL no-op                  | 17.95% | 1.058                                    | -29.28% | 1.000        |
| Rule-based controller     | 18.25% | 1.083                                    | -30.08% | 0.696        |
| Random bounded (50 seeds) | 18.46% | 1.218 (mean) / 1.206 (med) / 1.279 (p75) | -25.90% | —            |
| Trained Phase E RL        | 16.86% | 1.275                                    | -21.73% | 0.365        |

## Random Baseline Distribution (50 seeds, 10 bps)

| Stat    |   Sharpe |
|:--------|---------:|
| Mean    |    1.218 |
| Median  |    1.206 |
| p25     |    1.154 |
| p75     |    1.279 |
| p90     |    1.333 |
| p95     |    1.397 |
| Std dev |    0.111 |

> Promotion uses **median** as hard minimum and **p75** as preferred.
> p90/p95 are reported for context only.

## Cost Sensitivity (all policies, post-hoc cost adjustment)

|   cost_bps |   B.5 locked |   No-op |   Rule-based |   Random mean |   Trained RL |
|-----------:|-------------:|--------:|-------------:|--------------:|-------------:|
|    10.0000 |       1.2701 |  1.0578 |       1.0835 |        1.2178 |       1.2753 |
|    25.0000 |       1.2195 |  1.0440 |       1.0608 |        1.1857 |       1.2501 |
|    50.0000 |       1.1349 |  1.0209 |       1.0230 |        1.1322 |       1.2079 |

## Regime Breakdown

| regime             |   B.5 locked Sharpe |   B.5 locked MaxDD |   RL no-op Sharpe |   RL no-op MaxDD |   Trained RL Sharpe |   Trained RL MaxDD |
|:-------------------|--------------------:|-------------------:|------------------:|-----------------:|--------------------:|-------------------:|
| 2019 bull market   |              2.6491 |            -0.0570 |            1.9039 |          -0.0792 |              2.6786 |            -0.0448 |
| 2020 COVID crash   |              0.4353 |            -0.3298 |            0.7620 |          -0.2928 |              0.8882 |            -0.2173 |
| 2021 recovery      |              2.4201 |            -0.0657 |            2.3187 |          -0.0699 |              2.3704 |            -0.0430 |
| 2022 bear market   |             -0.7278 |            -0.1711 |           -0.8324 |          -0.2069 |             -0.6999 |            -0.1779 |
| 2023–2026 recovery |              2.4733 |            -0.1055 |            2.0842 |          -0.1055 |              2.3111 |            -0.0893 |

## Promotion Gate Evaluation

| gate                                              | value                       | pass   | required    |
|:--------------------------------------------------|:----------------------------|:-------|:------------|
| Path A: Sharpe ≥ 1.270 AND MaxDD ≥ -32.98%        | Sharpe=1.275, MaxDD=-21.73% | True   | either path |
| Path B: Sharpe ≥ 1.240 AND MaxDD ≥ -31.48%        | Sharpe=1.275, MaxDD=-21.73% | True   | either path |
| 50 bps Sharpe ≥ 0.90                              | 1.208                       | True   | yes         |
| Beats RL no-op Sharpe (1.058)                     | 1.275                       | True   | yes         |
| Beats random median Sharpe (1.206) [hard minimum] | 1.275                       | True   | yes         |
| Beats random p75 Sharpe (1.279) [preferred]       | 1.275                       | False  | preferred   |
| Beats rule-based controller Sharpe (1.083)        | 1.275                       | True   | yes         |
| Hard rejection: MaxDD ≥ -35% (no blowup)          | -21.73%                     | True   | yes         |

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
