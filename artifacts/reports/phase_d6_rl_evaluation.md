# Phase D.6 — RL vs B.5 Four-Way Comparison

- Run date: 2026-05-02 09:27:33 UTC
- Holdout window: 2019-01-01 → 2026-04-24
- B.5 holdout benchmark (D.0): Sharpe 1.270, MaxDD -32.98%
- Primary comparison cost: 10 bps (same basis for all policies)
- Cost methodology: B.5 locked via compute_net_returns; RL policies via post-hoc
  turnover-based deduction. RL env trained at cost_bps=0 (tilt penalty approximates cost).

## Verdict: **REJECT trained RL — keep B.5 as production system**

## Sanity Check: No-op ≈ B.5 Locked

| Check | B.5 Sharpe | No-op Sharpe | Diff | Status |
|---|---|---|---|---|
| No-op should reproduce B.5 at same cost | 1.270 | 1.245 | 0.025 | PASS |

> If diff > 0.05, the env's return simulation diverges from compute_net_returns.
> Expected small diff due to: daily price differences, B.4 single-date vs full-period
> application. Diff > 0.10 would indicate a bug.

## Policy Comparison (10 bps, holdout 2019–2026)

| Policy                    | CAGR   |   Sharpe | MaxDD   |   Avg |tilt| |
|:--------------------------|:-------|---------:|:--------|-------------:|
| B.5 locked                | 20.69% |    1.27  | -32.98% |       0      |
| RL no-op                  | 20.33% |    1.245 | -32.98% |       0      |
| Random bounded (50 seeds) | 17.72% |    1.321 | -27.04% |       0.0141 |
| Trained RL                | 17.40% |    1.295 | -24.90% |       0.0116 |

## Cost Sensitivity (all policies, post-hoc cost adjustment)

> B.5 locked: exact costs from compute_net_returns.
> RL policies: costs applied post-hoc from turnover recorded during episode.

|   cost_bps |   B.5 locked |   No-op |   Random |   Trained RL |
|-----------:|-------------:|--------:|---------:|-------------:|
|    10.0000 |       1.2701 |  1.2449 |   1.3209 |       1.2951 |
|    25.0000 |       1.2195 |  1.2154 |   1.2817 |       1.2606 |
|    50.0000 |       1.1349 |  1.1660 |   1.2161 |       1.2029 |

## Regime Breakdown

| regime             |   B.5 locked Sharpe |   B.5 locked MaxDD |   RL no-op Sharpe |   RL no-op MaxDD |   Trained RL Sharpe |   Trained RL MaxDD |
|:-------------------|--------------------:|-------------------:|------------------:|-----------------:|--------------------:|-------------------:|
| 2019 bull market   |              2.6491 |            -0.0570 |            2.8783 |          -0.0568 |              2.8228 |            -0.0495 |
| 2020 COVID crash   |              0.4353 |            -0.3298 |            0.4414 |          -0.3298 |              0.8116 |            -0.2490 |
| 2021 recovery      |              2.4201 |            -0.0657 |            2.4361 |          -0.0657 |              2.0099 |            -0.0594 |
| 2022 bear market   |             -0.7278 |            -0.1711 |           -0.7216 |          -0.1704 |             -0.7214 |            -0.1448 |
| 2023–2026 recovery |              2.4733 |            -0.1055 |            2.3783 |          -0.1052 |              2.2740 |            -0.0970 |

## Promotion Gate Evaluation

| gate                                       | value                       | pass   |
|:-------------------------------------------|:----------------------------|:-------|
| Path A: Sharpe ≥ 1.270 AND MaxDD ≥ -32.98% | Sharpe=1.295, MaxDD=-24.90% | True   |
| Path B: Sharpe ≥ 1.240 AND MaxDD ≥ -31.48% | Sharpe=1.295, MaxDD=-24.90% | True   |
| 50 bps Sharpe ≥ 0.90                       | 1.203                       | True   |
| Beats RL no-op Sharpe (1.245)              | 1.295                       | True   |
| Beats random bounded Sharpe (1.321)        | 1.295                       | False  |
| Hard rejection: MaxDD ≥ -35% (no blowup)   | -24.90%                     | True   |

## Notes

- Path A = clear Sharpe win: Sharpe ≥ B.5 holdout AND MaxDD ≥ B.5 holdout MaxDD.
- Path B = tail improvement: Sharpe ≥ B.5 − 0.03 AND MaxDD at least 1.5pp better.
- Both paths require 50 bps Sharpe ≥ 0.90, beat no-op (same cost basis), beat random.
- Hard rejections: MaxDD < −35%, or any beta violation, or max gross > 1.50.
- B.5 holdout Sharpe (1.270) is higher than full-period (1.078) — 2019+ is a strong
  regime; RL must add genuine value beyond the no-op baseline to be promoted.

## Artifacts

- `artifacts/reports/phase_d6_rl_evaluation.md` — this file
- `artifacts/reports/d6_policy_comparison.csv`
- `artifacts/reports/d6_regime_breakdown.csv`
