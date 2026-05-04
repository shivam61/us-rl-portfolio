# Phase PROD — Live Capital Deployment

> **Navigation:** [← Phase H](phase_h.md) | [← ROADMAP](../ROADMAP.md)

**Prerequisite:** All 8 Phase H exit gates pass.

**Objective:** Deploy the E.7 RL system with real capital. Ramp gradually, enforce hard circuit
breakers, and establish steady-state operations with a clear quarterly review cadence.

---

## Budget & Position Sizing

| Parameter | Value | Notes |
|-----------|-------|-------|
| Initial capital | `$[BUDGET]` | Fill in before PROD.0 |
| Minimum sensible budget | ~$25K | Below this, integer-lot rounding on Top-20 creates > 2pp tracking error |
| Target portfolio AUM ceiling | ~$50M | Above this, sp500 Top-20 liquidity assumption needs re-validation |
| Leverage | **None (1×)** | No margin in V1; revisit at Phase PROD.2+ |
| Max single position | 15% of NAV | Hard limit regardless of vol_score signal |
| Min position size | 0.5% of NAV | Positions below this threshold are treated as zero (avoid rounding noise) |
| Cash instrument | T-bill ETF (e.g., BIL) or money market | RL cash fraction → this instrument; accrues yield |

### Position Sizing Formula

```python
# On each rebalance:
target_shares[ticker] = floor((target_weight[ticker] * portfolio_nav) / price[ticker])
cash_residual = portfolio_nav - sum(target_shares[ticker] * price[ticker])
# Cash residual → BIL or hold as sweep
```

---

## PROD.0 — Pre-Launch Checklist

Before first real-money order:

- [ ] Phase H exit gate signed off (all 8 criteria)
- [ ] Live broker account funded with `$[BUDGET]`
- [ ] API keys in secure store (not in code, not in git)
- [ ] Order submission tested with 1-share test orders on each ticker
- [ ] G.2 audit trail pointing to live (not paper) store
- [ ] G.3 monitoring dashboard connected to live portfolio NAV
- [ ] Emergency halt procedure documented and tested (see PROD.4)
- [ ] Halting thresholds agreed and configured (see PROD.3)
- [ ] Tax lot accounting method selected (FIFO default)

---

## PROD.1 — Capital Ramp

Do not deploy full capital on day one. Ramp gradually to catch any live-specific issues with
limited exposure.

| Week | Capital deployed | Mode | Trigger to advance |
|------|-----------------|------|--------------------|
| 1–2 | 25% of `$[BUDGET]` | b5_only | No pipeline failures; fills within 20 bps |
| 3–4 | 50% of `$[BUDGET]` | b5_only → RL if G.3 clean | Live Sharpe ≥ paper Sharpe − 0.10 |
| 5–6 | 75% of `$[BUDGET]` | RL (if switched) | No circuit breaker triggers |
| 7+ | 100% of `$[BUDGET]` | RL | 6-week performance review passes |

**Ramp abort rule:** If a circuit breaker triggers during the ramp (see PROD.3), freeze at
current deployment level, investigate, resolve before advancing.

---

## PROD.2 — Execution

### Order Type & Timing

| Step | Time (ET) | Action |
|------|-----------|--------|
| Signal generation | 16:05 | G.1 pipeline runs on EOD prices |
| Order calculation | 16:10 | Target shares computed |
| Order submission | **Next trading day, 09:35** | Limit orders at previous close ± 5 bps; cancel/replace at 15:55 with market |
| Fill confirmation | 16:00 | Log fills; compute slippage |
| Audit record | 16:30 | G.2 entry with full state snapshot |

**Why T+1 execution:** EOD prices arrive after 16:00; same-day MOC submission is operationally
risky. T+1 open/mid-session limit orders are cleaner and allow price-checking. The backtest's
10 bps cost assumption is conservative enough to absorb overnight drift on large-cap names.

**Alternative (simpler V1):** Market-on-open the next morning. Slippage is higher on average
but more predictable and requires no order management system.

### Rebalance Cadence

- Every 2 rebalance dates (matches backtest cadence, ~2 weeks in practice)
- Non-rebalance days: G.1 pipeline runs for monitoring only; no orders placed
- Emergency rebalance: only if a circuit breaker triggers a mode switch

---

## PROD.3 — Circuit Breakers & Risk Controls

### Hard Stops (automatic, immediate)

| Trigger | Action | Resume condition |
|---------|--------|-----------------|
| Portfolio NAV drops > 15% from high-water mark | Liquidate to 100% BIL + halt | Manual review + reset approval |
| Any single position > 20% NAV | Reduce to 15% target at next open | Auto-resume after trim |
| Signal pipeline fails 2 consecutive days | Hold current positions; no new trades | Pipeline restored + test pass |
| Beta violation flagged (rolling beta > cap) | Reduce offending position by 50% | Auto-resume when beta within band |

### Soft Stops (alert, manual review)

| Trigger | Action |
|---------|--------|
| Rolling 63d live Sharpe < B.5 paper Sharpe − 0.10 for 21 days | Review; consider switching to b5_only |
| G.3 two drift flags co-occurring | Review; consider switching to b5_only |
| RL avg equity < 0.25 for 10 rebalances | Review RL regime posture; consider disabling RL |
| Monthly drawdown > 10% | Alert; no automatic action |

### Mode Switch Protocol

- **RL → b5_only:** Executes at next scheduled rebalance (no forced immediate trades)
- **b5_only → RL:** Requires G.3 clean for 10 days + manual approval
- All mode switches logged to G.2 audit trail with reason code

---

## PROD.4 — Emergency Halt Procedure

If something goes wrong that isn't covered by circuit breakers:

1. Manually trigger halt flag in G.1 pipeline (sets `HALT=true` in config; pipeline exits without trading)
2. Current positions held as-is (no forced liquidation unless hard stop triggered)
3. Open G.3 dashboard — assess what triggered the concern
4. If positions need to exit: manually submit limit orders to reduce; do not use market orders in bulk
5. Write incident note to `data/audit/incidents/YYYY-MM-DD.md`
6. Root-cause investigation before resuming

---

## PROD.5 — Steady-State Operations

### Daily (automated, ~15 min review)

- G.1 pipeline log: did it run? any errors?
- G.3 dashboard: any flags?
- Fill log: any outlier slippage (> 30 bps)?
- Portfolio NAV vs previous day

### Weekly (manual, ~30 min)

- Actual vs target weights (drift check)
- Rolling 4-week Sharpe vs B.5 paper portfolio vs SPY
- RL equity fraction trend (is the RL de-risking or re-risking appropriately?)
- Any new G.3 drift flags this week?

### Monthly (~2 hours)

- Full performance attribution: alpha (vol_score), risk (beta cap, stress), RL regime decisions
- Slippage report: actual vs 10 bps assumption
- Compare to holdout backtest forward-looking projection
- Update `artifacts/reports/prod_monthly_{YYYY_MM}.md`

### Quarterly (~half day)

- Is the RL policy still in-distribution? (G.3 PSI check on full feature set)
- Retrain evaluation gate: has market regime shifted enough to warrant a retrain?
  - Trigger: rolling 252d live Sharpe < backtest val Sharpe − 0.10
  - If triggered: start Phase F.3 (retrain evaluation) without halting production
- Review position sizing: has AUM grown to where liquidity assumptions need revisiting?
- Review cash instrument yield vs portfolio cash drag assumption

---

## Performance Reporting

### Benchmarks to Track

| Benchmark | Ticker | Rationale |
|-----------|--------|-----------|
| SPY | SPY | Market reference; floor for any active strategy |
| 60/40 | SPY 60% + AGG 40% | Traditional balanced portfolio |
| B.5 paper portfolio | internal | Own no-RL baseline; RL must justify its complexity |
| E.7 RL backtest projection | internal | Forward-looking expected return from holdout metrics |

### Target Live Metrics (from Phase E holdout, 2019–2026)

| Metric | Target | Notes |
|--------|--------|-------|
| Annual Sharpe | ≥ 1.270 | Phase E holdout bar |
| Annual CAGR | ≥ 17.79% | E.7 holdout; note 2019–2026 was a strong bull period |
| MaxDD | ≥ −24.48% | E.7 holdout; harder to achieve live due to real slippage |
| vs SPY Sharpe | > 0.70 (SPY ~0.85 in same period) | Should clearly beat passive |

**Caveat on live vs backtest:** 2019–2026 includes COVID recovery and a historic bull run.
Live forward performance starting 2026+ will likely have lower CAGR. Judge on Sharpe and
drawdown control, not absolute CAGR.

---

## Scaling Path (Post-PROD V1)

| Milestone | Condition | Next action |
|-----------|-----------|-------------|
| PROD V1 stable (6 months) | All hard stops untriggered; live Sharpe ≥ 1.0 | Consider increasing capital allocation |
| AUM > $1M | Need to revisit Top-20 concentration and liquidity | Expand to Top-30? Re-run F.1 sensitivity |
| AUM > $10M | Market impact starts to matter for small-cap overflow | Consider impact model |
| Retrain triggered | Live Sharpe < val Sharpe − 0.10 for 252d | F.3 retrain without halting prod |

---

## Key Files

| File | Purpose |
|------|---------|
| `config/prod.yaml` | Production config (budget, broker, thresholds) — **not committed to git** |
| `scripts/run_prod_signal.py` | Daily signal generation + order calculation (to be built in G.1) |
| `data/audit/` | G.2 immutable audit trail |
| `data/paper_trading/` | Phase H paper trade records |
| `artifacts/reports/prod_monthly_*.md` | Monthly performance reports |
| `data/audit/incidents/` | Emergency halt records |
