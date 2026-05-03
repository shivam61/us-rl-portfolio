# Phase F.1 — Top-N Sensitivity Under E.7 RL

- Run date: 2026-05-03 19:06:07 UTC
- Holdout window: 2019-01-01 → 2026-04-24
- E.7 published result (Top-20): Sharpe 1.296, MaxDD -24.48%, CAGR 17.79%
- E.7 random p75: 1.280
- **Model note:** The current `rl_e_ppo_best.zip` is the E.8 training checkpoint (trained
  with rolling 252d peak reward before E.8 was REJECTED and `reward_v2.py` was reverted).
  E.7's original checkpoint was overwritten. Top-20 internal baseline here is **1.277**
  (matches E.8's published evaluation), not 1.296. All four Top-N variants are evaluated
  with the same checkpoint, so the cross-variant comparison is internally consistent.
  Promotion gates use the published E.7 bar (Sharpe ≥ 1.270) as the standard.

## Step F.1a — Top-N Comparison (E.7 RL checkpoint, 10 bps holdout)

| Top-N         | CAGR   |   Sharpe | MaxDD   |   50bps Sharpe |   Avg equity |   RL turnover |   Beta violations |   Max gross |   Rand p75 |
|:--------------|:-------|---------:|:--------|---------------:|-------------:|--------------:|------------------:|------------:|-----------:|
| 10            | 18.39% |    1.217 | -25.69% |          1.119 |        0.396 |          23.9 |                 0 |         1.5 |      1.194 |
| 15            | 17.43% |    1.199 | -27.48% |          1.095 |        0.395 |          24.6 |                 0 |         1.5 |      1.196 |
| 20 (baseline) | 17.72% |    1.277 | -24.54% |          1.165 |        0.396 |          25.2 |                 0 |         1.5 |      1.275 |
| 30            | 16.19% |    1.209 | -24.14% |          1.093 |        0.396 |          25.6 |                 0 |         1.5 |      1.204 |

### B.5 No-RL Baseline by Top-N (10 bps)

| Top-N         | CAGR   |   Sharpe | MaxDD   |
|:--------------|:-------|---------:|:--------|
| 10            | 21.02% |    1.191 | -33.93% |
| 15            | 19.84% |    1.158 | -36.58% |
| 20 (baseline) | 20.69% |    1.27  | -32.98% |
| 30            | 19.60% |    1.242 | -32.67% |

## Promotion Gate Evaluation (non-Top-20 only)

|   top_n | verdict   | all_gates_pass   | retrain_recommended   | gate_sharpe   | gate_maxdd   | gate_cagr   | gate_50bps   | gate_rand_p75   | material_vs_top20   |
|--------:|:----------|:-----------------|:----------------------|:--------------|:-------------|:------------|:-------------|:----------------|:--------------------|
|      10 | REJECT    | False            | False                 | False         | True         | True        | True         | True            | True                |
|      15 | REJECT    | False            | False                 | False         | False        | False       | True         | True            | False               |
|      30 | REJECT    | False            | False                 | False         | True         | False       | True         | True            | False               |

## Step F.1b — Retrain Recommendation

**No retrain required.** No non-20 Top-N variant beats Top-20 materially while passing all
promotion gates. Top-20 remains the recommended breadth for the current RL policy.

Key findings:
- **Top-10** has the best CAGR (+0.67pp vs Top-20) and beats its own random p75 (1.217 > 1.194),
  but Sharpe (1.217) falls below the 1.270 gate. The concentrated 10-stock book improves CAGR
  but adds idiosyncratic volatility that the RL cannot fully hedge.
- **Top-15** just misses the MaxDD gate (-27.48% vs -27.00% threshold) and fails Sharpe.
  Not material vs Top-20 on either metric.
- **Top-30** has lower CAGR (16.19%) and lower Sharpe (1.209) vs Top-20. Dilution hurts alpha
  without proportional drawdown improvement.
- **Avg equity is stable (~0.396) across all Top-N** — the RL posture (how aggressively
  it allocates to equities) is insensitive to breadth, as expected for a fixed trained policy.
- **RL drawdown advantage over B.5 no-RL is preserved across all Top-N** (~8–10pp improvement).

## Methodology

- RL checkpoint used as-is (no retraining). Only the equity sleeve breadth (Top-N) changes.
- Trend sleeve, reward definition, beta constraints, every-2-rebalance cadence: all unchanged.
- Random baselines re-run per Top-N (20 seeds each) for per-variant p75 reference.
- Promotion gates: Sharpe ≥ 1.270, MaxDD ≥ −27%, CAGR > 17.79%, 50 bps Sharpe ≥ 1.0,
  beats per-variant random p75.
- Material threshold for F.1b retrain flag: Sharpe delta ≥ +0.010 OR CAGR delta ≥ +0.5pp vs Top-20.

## Artifacts

- `artifacts/reports/phase_f1_topn_sensitivity.md` — this file
- `artifacts/reports/f1_topn_comparison.csv`
- `artifacts/reports/f1_regime_breakdown.csv`
- `artifacts/reports/f1_sector_concentration.csv`
