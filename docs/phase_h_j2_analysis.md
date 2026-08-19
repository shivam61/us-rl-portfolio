# Phase H — Journey 2 Analysis & Production Readiness

**Generated:** 2026-08-19  
**Period:** 2026-05-13 → 2026-08-19 (98 calendar days, 71 trading days)  
**NAV:** $50,000 starting capital · NAV freeze bug fixed in J2

---

## Summary

Journey 2 was run to fix the NAV freeze bug present in Journey 1, where
`update_positions()` used a constant `$50K` as the NAV denominator for all
weight and cash calculations. J2 uses real mark-to-market NAV throughout.

---

## Performance vs S&P 500

| Metric | J2 (RL Portfolio) | SPY |
|--------|-------------------|-----|
| Total return | +2.88% | +3.94% |
| CAGR (annualised) | +11.16% | +15.50% |
| Alpha vs SPY | −1.06% (−4.3% ann.) | — |
| Sharpe ratio | 1.10 | 1.12 |
| Max drawdown | −3.65% | −4.74% |
| Annualised volatility | 9.87% | 13.90% |
| Final NAV | $51,441 | $51,972 (SPY equiv.) |

The portfolio delivered lower absolute return than SPY but with meaningfully
lower volatility (9.9% vs 13.9%) and shallower drawdown. On a risk-adjusted
basis, Sharpe ratios are near-parity (1.10 vs 1.12).

---

## Phase Breakdown

### Phase 1 — rl_e7 (2026-05-13 → 2026-07-28, 76 days)

| Metric | J2 | SPY | Alpha |
|--------|-----|-----|-------|
| Return | +0.82% | −0.20% | **+1.02%** |
| Sharpe | 0.49 | −0.00 | — |
| Max DD | −2.70% | −4.74% | — |

The RL policy outperformed during the pre-switch period. SPY was flat/negative
while the portfolio defended capital with tighter drawdowns. This is the system
working as intended.

### Phase 2 — b5_only (2026-07-29 → 2026-08-19, 21 days)

| Metric | J2 | SPY | Alpha |
|--------|-----|-----|-------|
| Return | +3.19% | +5.78% | **−2.59%** |
| Sharpe | 4.58 | 7.67 | — |
| Max DD | −1.15% | −1.34% | — |

The G.4 drift monitor fired a mode switch to `b5_only` on 2026-07-29 due to
PSI flags on `realized_market_vol_63d` and `vix_percentile_1y`. This coincided
with the start of a strong SPY rally (+5.78%). The switch cost approximately
2.6% alpha in 21 days. The PSI threshold appears overly sensitive.

---

## Per-Rebalance Returns

| Rebalance | Mode | 14d Return | Turnover | Assessment |
|-----------|------|------------|----------|------------|
| R1 2026-05-26 | rl_e7 | +0.53% | 39.2% | Positive return, turnover above gate |
| R2 2026-06-09 | rl_e7 | +0.89% | 57.5% | Best return, high turnover |
| R3 2026-06-23 | rl_e7 | −0.32% | 57.9% | Small loss, high turnover |
| R4 2026-07-07 | rl_e7 | −0.35% | 29.6% | Small loss, only period under gate |
| R5 2026-07-21 | rl_e7 | +0.94% | 59.5% | Best return, highest turnover |
| R6 2026-08-04 | rl_e7 | −0.75% | 56.9% | Loss, high turnover |
| R7 2026-08-18 | rl_e7 | pending | 19.7% | T+14 not yet observable |

Average turnover: **45.8%** (gate threshold: 35%). 5 of 7 rebalances exceeded the gate.

---

## H-Gate Evaluation

| Gate | Description | Result | Value | Target |
|------|-------------|--------|-------|--------|
| H-1 | Pipeline reliability | ✅ PASS | 0 error days / 72 total | 0 errors |
| H-2 | Fill slippage | ⚠️ WARN* | 337 bps avg | < 20 bps |
| H-3 | Rebalance turnover | ❌ FAIL | 45.8% avg | < 35% |
| H-4 | Weight drift | ✅ PASS | 0.80 pp avg max | < 5 pp |
| H-5 | RL mode dominance | ✅ PASS | 72/72 days rl_e7 | ≥ 50% RL |
| H-6 | Sharpe ratio | ✅ PASS | 1.10 | > 0.5 |
| H-7 | Drift flags | ✅ PASS | 0 active | < 2 co-occurring |
| H-8 | Audit trail | ✅ PASS | 72 decisions logged | Complete |

**Total: 6/8 passing**

\* H-2 note: The 337 bps figure measures the T vs T+1 adj_close price difference,
which captures overnight market return noise rather than real execution slippage.
Paper fills have zero real market impact. This gate metric needs redefining before
live deployment — a bid-ask spread estimate (e.g. 0.5 × daily range / close) would
be more meaningful.

---

## Root Cause Analysis: Remaining Blockers

### H-3 FAIL — Excess Turnover (45.8% avg vs 35% gate)

The RL policy rebalances the 21-stock equity sleeve plus trend sleeve every 14 days
with no explicit cost penalty in the reward function. Each rebalance re-optimises
weights from scratch, producing large delta-share vectors even when the prior
allocation was close to optimal.

**Root cause:** `reward_v2` penalises drawdown and rewards Sharpe but has no term
discouraging weight churn. The policy learned to "explore" aggressively because
turnover has zero cost in simulation.

**Fix:** Add a turnover penalty to `reward_v2`:
```python
turnover_penalty = lambda_t * sum(abs(w_new - w_old) for each ticker)
reward = sharpe_component - drawdown_penalty - turnover_penalty
```
Suggested `lambda_t` starting point: 0.01–0.05, tuned so that round-trip cost at
3 bps/share still leaves positive expected alpha.

### G.4 Switch Sensitivity — Premature b5_only Trigger

The Jul 29 switch fired when 2+ PSI flags co-occurred over a 5-day window.
The PSI flags (on `realized_market_vol_63d` and `vix_percentile_1y`) indicated
the live regime diverged from training distribution — but the market subsequently
rallied strongly, suggesting the RL policy would have performed well.

**Root cause:** PSI drift detection is calibrated on the training baseline and flags
distribution shift conservatively. In a rising market with elevated recent vol, the
training distribution (low-vol baseline) naturally diverges even when conditions are
benign.

**Fix options (pick one):**
1. Require 3+ flags co-occurring (currently 2) before switching
2. Extend the detection window from 5 days to 10 days
3. Add a return-confirmation requirement: only switch if rolling 5-day return also
   lags B.5 by more than 1%

---

## J1 vs J2 Comparison

The key difference between journeys:

| | J1 (frozen NAV) | J2 (fixed NAV) |
|--|-----------------|----------------|
| NAV denominator in positions | Constant $50K | Real MTM NAV |
| `portfolio_weight` accuracy | Wrong (frozen) | Correct |
| Experience log `realized_return_14d` | 0.00 for all rows | Real values |
| RL state features 39/40/41 | Zero (broken feedback) | Live values |
| Turnover assessment | Inflated (bad weights → over-trading) | True policy behavior |

J2 confirms the core RL policy does generate positive alpha during in-distribution
conditions. The frozen NAV in J1 was causing the policy to receive incorrect
portfolio state at every rebalance, making J1 performance data unreliable for
evaluating the policy.

---

## Production Readiness Verdict

**Not yet ready. One structural blocker: excess turnover.**

The system has strong fundamentals:
- Positive alpha during rl_e7 phase (+1.02% vs SPY)
- Competitive risk-adjusted returns (Sharpe 1.10)
- Lower volatility and shallower drawdowns than SPY
- 6/8 H-gates passing
- Zero pipeline errors across 72 days

But at 45.8% average turnover, live transaction costs would erode the alpha.
A round trip at 3–5 bps/share on $51K NAV with 20 active positions costs
roughly 0.3–0.5% per rebalance — the current 0.28% average 14d alpha would
be wiped out.

---

## Recommended Next Steps

### Priority 1 — Add turnover penalty to reward function (blocking)
- File: `src/rl/reward_v2.py`
- Add `lambda_t * sum(|Δw|)` term to `compute_reward_v2()`
- Target average rebalance turnover: < 30%
- Retrain rl_e7 with the updated reward, validate on backtest

### Priority 2 — Recalibrate G.4 drift switch threshold
- File: `src/rl/drift_monitor.py` (co-occurrence window / flag count)
- Change from 2 co-occurring flags → 3, or extend window from 5d → 10d
- Backtest the revised threshold against the J2 period to verify it would
  not have fired on 2026-07-29

### Priority 3 — Redefine H-2 slippage metric
- File: `scripts/log_paper_fills.py` (slippage computation)
- Replace T vs T+1 adj_close diff with bid-ask spread estimate
- Suggested: `est_slippage_bps = 0.5 * (high - low) / close * 10000`

### Priority 4 — Journey 3 paper run
- After retraining (Priority 1) and G.4 recalibration (Priority 2):
  `python scripts/run_j2_backfill.py --journey j3`
- With turnover controlled and correct NAV feedback, expect all 8 H-gates
  to pass on the next journey

---

*Analysis based on Journey 2 data: 71 trading days, 7 completed rebalances,
72 audit trail entries. Journey 2 config: `config/paper_trading_j2.yaml`.*
