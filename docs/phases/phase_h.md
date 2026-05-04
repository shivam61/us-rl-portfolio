# Phase H — Paper Trading

> **Navigation:** [← Phase G](phase_g.md) | [← ROADMAP](../ROADMAP.md) | [→ Phase PROD](phase_prod.md)

**Prerequisite:** Phase G complete — signal pipeline runs unattended, audit trail live, drift
monitoring dashboard active, dual-mode switching rule validated on 3 historical dates.

**Objective:** Run the production signal pipeline against live market data for 8–12 weeks with
simulated (paper) fills. Validate that backtest assumptions hold forward in time before committing
real capital. This phase has a hard pass/fail gate at the end — no capital is deployed until
Phase H exit criteria are met.

---

## Why Paper Trade Before Going Live

Backtests assume:
- 10 bps fill cost (round-trip) on all trades
- No market impact
- Data is always available end-of-day
- Signal gen is instantaneous

Live trading breaks all four. Phase H is where those assumptions are stress-tested with zero
downside risk.

---

## Phase H Timeline

| Week | Milestone |
|------|-----------|
| H.0 (pre-start) | Broker paper account set up, signal pipeline connected, initial allocation loaded |
| H.1–H.4 (weeks 1–4) | Live paper trading; daily signal gen; track slippage, data failures, fill latency |
| H.5 (week 5) | Mid-point review: slippage vs assumption, pipeline reliability, any signal anomalies |
| H.6–H.10 (weeks 6–10) | Continue paper trading; at least 2 full rebalance cycles must complete |
| H.11 (week 11) | Final Phase H gate evaluation — go/no-go for Phase PROD |

Minimum duration: **8 weeks** (covers ~4 rebalances at every-2-rebalance cadence, ~2 weeks apart).
Extend to 12 weeks if mid-point review flags concerns.

---

## H.0 — Setup

### Broker Choice

| Option | Best for | Notes |
|--------|----------|-------|
| **Alpaca** | $0–$100K, paper trading native support | Free paper trading API; easy Python SDK; no PDT rule for $0 account; good for development |
| **Interactive Brokers (IBKR)** | $50K+ | Industry standard; better fill quality; TWS API more complex; real paper account mirrors live |
| **TD Ameritrade / Schwab thinkorswim** | Any size | PaperMoney platform; good simulation; no programmatic API as clean as Alpaca/IBKR |

**Recommendation for Phase H:** Start with Alpaca paper trading (zero friction, Python-native).
Before Phase PROD, migrate to the actual broker you'll use with real capital.

### Initial Paper Allocation

1. Run full G.1 signal pipeline to get current target allocation
2. Load paper account with simulated NAV = planned Phase PROD capital (e.g., $[BUDGET])
3. Submit paper orders at today's close prices using target weights
4. This becomes the paper portfolio baseline (T=0 NAV)

---

## H.1–H.4 — Live Paper Trading Loop

### Daily Operations

```
16:00 ET  Market close
16:05 ET  G.1 pipeline runs (fetches EOD prices, computes features, runs RL)
16:10 ET  Allocation JSON exported (stock weights, fracs, state vector)
16:15 ET  Order calculation: (target_weight × NAV / price → shares to buy/sell)
16:20 ET  Paper orders submitted to broker (limit or market-on-close)
16:30 ET  Fill confirmation + slippage log entry
16:45 ET  G.2 audit trail entry written
17:00 ET  G.3 drift monitoring checks run
```

**On non-rebalance days:** Signal pipeline still runs (feature computation, state vector, drift
checks) but no orders are placed. This catches data failures early without unnecessary turnover.

### What to Track Daily

| Metric | How to compute | Flag threshold |
|--------|---------------|----------------|
| Signal latency | Time from 16:00 to allocation JSON ready | > 20 min |
| Data feed failure | Any missing tickers in EOD prices | Any missing large-cap |
| Target weight drift | Actual portfolio weights vs target | Any position > target + 3pp |
| Paper slippage | Simulated fill price vs 16:00 close | > 30 bps per trade |
| Rebalance turnover | Actual vs backtest estimated (25%) | > 40% on any rebalance |

---

## H.5 — Mid-Point Review (Week 5)

Decision tree:

```
avg slippage < 20 bps? ──YES──> continue
                        ──NO──> diagnose (large-cap liquidity fine; suspect data timing or order type)

pipeline failures < 2? ──YES──> continue  
                        ──NO──> fix G.1 reliability before proceeding

RL mode active? ─────── NO (stuck in b5_only)? diagnose G.4 switching rule thresholds
```

If any critical issue: pause paper trading, fix, restart clock.

---

## H.6–H.10 — Extended Paper Trading

At least **2 full rebalance cycles** must complete post-mid-point-review before the exit gate.
Use this period to:
- Validate sector concentration matches backtest (XLK ~26%, XLY ~14%, XLF ~9%)
- Confirm avg equity fraction ≥ 0.35 (RL not stuck in cash)
- Track rolling paper NAV vs B.5 paper NAV vs SPY

---

## Phase H Exit Gate (Week 11+)

All of the following must pass to proceed to Phase PROD:

| # | Gate | Threshold |
|---|------|-----------|
| H-1 | Pipeline reliability | Zero unrecovered signal failures over last 4 weeks |
| H-2 | Average fill slippage | < 20 bps (vs 10 bps backtest assumption) |
| H-3 | Rebalance turnover | < 35% avg (vs 25% backtest; tolerance for live timing) |
| H-4 | Target weight tracking | Max drift from target < 5pp on any position for > 2 days |
| H-5 | RL mode operational | At least one rebalance in RL mode (not permanently in b5_only) |
| H-6 | Paper Sharpe (8w) | ≥ B.5 paper Sharpe − 0.20 (wide tolerance; 8 weeks is too short to judge alpha) |
| H-7 | No data parity gap | G.0 feature parity check still passing |
| H-8 | Audit trail complete | 100% of rebalance decisions have a queryable audit record |

**Outcome:**
- All 8 pass → Proceed to Phase PROD
- Any fail → Extend paper trading until resolved; re-run gate

---

## Artifacts

- `data/paper_trading/daily_positions_{date}.parquet` — daily position snapshots
- `data/paper_trading/fills_{date}.csv` — simulated fill records with slippage
- `data/paper_trading/slippage_summary.csv` — aggregated slippage by ticker and date
- `artifacts/reports/phase_h_exit_gate.md` — written gate evaluation at Week 11+
