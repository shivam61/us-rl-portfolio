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

> **Status: COMPLETE** — Config frozen at `config/paper_trading.yaml` v H.0.0 (2026-05-12).
> T=0 bootstrap executed 2026-05-12 with RL model `rl_e7_clean_promoted` firing its action.
> Initial NAV: **$50,000** | Broker: Alpaca paper | Fractional shares: enabled.
> Allocation: Equity 25.00% / Trend 67.91% (UUP 58.05% + GLD 9.86%) / Cash 7.09%.

### Broker Choice

| Option | Best for | Notes |
|--------|----------|-------|
| **Alpaca** | $0–$100K, paper trading native support | Free paper trading API; Python-native; good for Phase H simulation |
| **Interactive Brokers (IBKR)** | $50K+ | Industry standard; better fill quality; use for Phase PROD |
| **TD Ameritrade / Schwab thinkorswim** | Any size | PaperMoney platform; no clean programmatic API |

**Phase H uses Alpaca paper (simulation only). Phase PROD will migrate to the real broker.**

### T=0 Bootstrap (one-time, already done)

```bash
# Already executed. Do not re-run unless resetting the paper portfolio from scratch.
.venv/bin/python scripts/run_daily_paper_ops.py --date 2026-05-09 --initial
```

The `--initial` flag does two things:
1. Passes `--force-rebalance` to `run_prod_signal.py` so the RL model fires its action
   (without this, the signal falls back to B.5 defaults and cash is wrong)
2. Treats all current positions as zero (starting from empty)

---

## H.1–H.4 — Live Paper Trading Loop

> **Rebalance cadence: every 14 calendar days.**
> The pipeline runs every trading day. On most days it is read-only (data refresh + signal + drift check).
> Orders and fills only execute on rebalance days (~every 14 days).

---

### Every trading day — required (~5 min, after 16:05 ET)

```bash
.venv/bin/python scripts/run_daily_paper_ops.py --date YYYY-MM-DD
```

8 steps run automatically:

| Step | Script | Action | Output |
|------|--------|--------|--------|
| 0 | `refresh_market_data.py` | Incremental price append for all tickers; rebuilds features only if stale | `data/raw/*.parquet` + `data/features/*.parquet` |
| 1 | `run_prod_signal.py` | RL signal on fresh features → target allocation | `data/allocations/{date}.json` |
| 2 | `run_drift_monitor_g3.py` | Feature drift + model health check | `data/drift/flags.parquet` |
| 3 | `compute_paper_orders.py` | Fractional share orders (buys/sells on rebalance days; hold-only otherwise) | `data/paper_trading/orders_{date}.csv` |
| 4 | `log_paper_fills.py` | T+1 fill simulation at adj_close; updates portfolio snapshot | `fills_{date}.csv` + `positions_latest.parquet` |
| 5 | `run_benchmark_dashboard_g5.py` | Refreshes performance vs B.5 / SPY | `artifacts/reports/benchmark_dashboard.html` |
| 6 | `generate_paper_journal.py` | Writes day entry to dated file + rolling journal | `docs/paper_trading/YYYY-MM-DD.md` + `docs/paper_trading_journal.md` |
| 7 | `append_experience_log.py` | Logs full transition tuple for offline RL (rebalance days only) | `data/paper_trading/experience_log.parquet` |

**On non-rebalance days:** Steps 3, 4, 7 still run but produce hold-only orders and no fills.
This catches data freshness failures early rather than discovering them on rebalance day.

**What populates the data:** Step 0 is the data population step. It appends only the missing
trading days to each `data/raw/{ticker}.parquet` file (incremental, not a full re-download),
then rebuilds `data/features/` if any ticker was updated. Features lag price by 1 business day
(point-in-time safe). Running the daily command every trading day keeps features always current.

---

### Rebalance days — additional review (~15 min, every 14 days)

**The daily command handles rebalance automatically** — no separate command needed.
The signal pipeline detects that 14+ days have elapsed since the last rebalance and fires
the RL model action, sizing new orders rather than producing hold-only output.

**Rebalance schedule:**

| # | Target date | Notes |
|---|-------------|-------|
| T=0 | 2026-05-12 | ✅ Bootstrap complete. RL action: equity 25% / trend 67.91% / cash 7.09% |
| R1 | ~2026-05-26 | First live rebalance |
| R2 | ~2026-06-09 | |
| R3 | ~2026-06-23 | |
| R4 | ~2026-07-07 | |
| Mid-point review | ~2026-06-17 | After R3 — run cumulative stats (see below) |
| Exit gate | Week 11+ (~2026-07-21) | All 8 H-gates must pass |

**After the daily command completes on a rebalance day, review:**

1. **Read the journal** — `docs/paper_trading/YYYY-MM-DD.md`
   - Allocation section: are equity/trend/cash sleeve fractions reasonable?
   - Orders table: confirm tickers and notional look right
   - Slippage table: any trades flagged > 30 bps?
   - H-gate status block: all green?

2. **Check turnover** — journal shows estimated turnover %. Must be < 35% (H-3 gate).

3. **Check weight drift** — max drift < 5pp across all positions (H-4 gate).

4. **Check RL mode** — should show `rl_e7`. If stuck in `b5_only` for 2+ consecutive
   rebalances, investigate G.4 switching rule thresholds in `src/rl/switching_rule.py`.

5. **Check drift flags** — if ≥ 2 flags active, read `data/drift/flags.parquet` and
   check `artifacts/reports/phase_g3_drift_report.md`.

---

### Week 5 — Mid-point review (~30 min, ~2026-06-14)

Run after the R3 rebalance (week 5). Check cumulative stats across all rebalances so far:

```bash
.venv/bin/python -c "
import pandas as pd, json
fills = pd.read_csv('data/paper_trading/slippage_summary.csv')
print('Avg slippage:', fills['actual_slippage_bps'].abs().mean().round(1), 'bps')
print('Flagged trades:', fills['slippage_flagged'].sum(), '/', len(fills))
ops = [json.loads(l) for l in open('data/paper_trading/daily_ops_log.jsonl')]
errors = sum(len(e['pipeline_errors']) for e in ops)
print('Total pipeline errors:', errors)
print('RL mode days:', sum(1 for e in ops if e['mode'] == 'rl_e7'))
"
```

Decision tree:
```
avg slippage < 20 bps?      YES → continue   NO → diagnose order timing / data source
pipeline errors < 2?        YES → continue   NO → fix G.1 reliability before proceeding
RL mode seen at least once? YES → continue   NO → diagnose G.4 switching thresholds
```

If any critical issue: pause paper trading, fix, restart the 8-week clock.

---

### What to track (journal does this automatically)

| Metric | Flag threshold | Gate |
|--------|---------------|------|
| Avg fill slippage | > 20 bps cumulative avg | H-2 |
| Rebalance turnover | > 35% on any rebalance | H-3 |
| Max weight drift | > 5pp on any position for > 2 days | H-4 |
| RL mode | stuck in `b5_only` for 2+ rebalances | H-5 |
| Pipeline errors | any unrecovered failure | H-1 |
| Drift flags active | ≥ 2 simultaneously | H-7 |

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

## H.6 — Paper Trading Experience Log

**Purpose:** Passive data collection for future offline RL training/evaluation. No automatic
retraining is triggered. The log is inert until explicitly used by a researcher.

**Artifact:** `data/paper_trading/experience_log.parquet` — one row per rebalance.

**Script:** `scripts/append_experience_log.py --date YYYY-MM-DD`
Called automatically from `run_daily_paper_ops.py` Step 6 on rebalance days only.

### Schema

| Field | When available | Source |
|-------|---------------|--------|
| `date_t` | T (rebalance) | allocation JSON |
| `state_vector_t` | T | allocation JSON `rl_state_vector` (42-element, JSON string) |
| `mode_t` | T | `"rl_e7"` or `"b5_only"` |
| `rl_action_t` | T | allocation JSON `rl_raw_action` ([3 floats] or null) |
| `target_weights_t` | T | allocation JSON `stock_weights` (JSON blob) |
| `nav_t` | T | allocation JSON |
| `equity_frac_t` | T | allocation JSON |
| `cash_frac_t` | T | allocation JSON |
| `stress_score_t` | T | allocation JSON |
| `spy_trend_positive_t` | T | allocation JSON |
| `model_id_t` | T | allocation JSON |
| `switch_reason_t` | T | allocation JSON |
| `drift_flags_t` | T | `data/drift/flags.parquet` latest row (JSON blob) |
| `actual_weights_t` | T+1 fills | `positions_latest.parquet` |
| `orders_t` | T+1 fills | `orders_{date}.csv` (ticker → delta_shares JSON) |
| `fills_t` | T+1 fills | `fills_{date}.csv` (ticker → fill_price JSON) |
| `slippage_bps_t` | T+1 fills | Notional-weighted avg `actual_slippage_bps` |
| `rebalance_turnover_t` | T+1 fills | Sum(\|notional\|) / NAV |
| `tracking_error_vs_target` | T+1 fills | Sqrt(sum((w_actual − w_target)²)) |
| `nav_t_plus_1` | T+1 fills | Sum of market values after fills |
| `nav_t_plus_14` | T+14 (backfilled) | Daily positions archive |
| `realized_return_14d` | T+14 (backfilled) | `nav_t_plus_14 / nav_t − 1` |
| `realized_vol_14d` | T+14 (backfilled) | Annualised std of daily returns [T, T+14] |
| `drawdown_14d` | T+14 (backfilled) | `min(nav) / max(nav) − 1` over [T, T+14] |
| `tracking_error_vs_b5` | T+14 (backfilled) | Annualised TE vs `nav_b5_backtest.parquet` |
| `tracking_error_vs_spy` | T+14 (backfilled) | Annualised TE vs `data/raw/SPY.parquet` |
| `reward_offline_t` | T+14 (backfilled) | `compute_reward_v2` with realized nav window |

### Two-pass design

- **Pass 1 (rebalance day):** T-fields + T+1 fill fields written; T+14 columns are null.
- **Pass 2 (14 days later, on next rebalance):** T+14 outcome columns backfilled from
  accumulated daily `positions_{date}.parquet` snapshots. Pass 2 is idempotent.

---

## Artifacts

- `data/paper_trading/daily_positions_{date}.parquet` — daily position snapshots
- `data/paper_trading/fills_{date}.csv` — simulated fill records with slippage
- `data/paper_trading/slippage_summary.csv` — aggregated slippage by ticker and date
- `data/paper_trading/experience_log.parquet` — H.6 offline RL training dataset
- `artifacts/reports/phase_h_exit_gate.md` — written gate evaluation at Week 11+
