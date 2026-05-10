# US RL Portfolio System

A complete end-to-end US equity portfolio system with walk-forward backtesting, RL regime
control, risk overlays, and a live paper trading loop.

**Disclaimer:** Research infrastructure only. Not investment advice. Do not deploy real capital
without completing all Phase H exit gates.

---

## Current Status — Phase H: Paper Trading (ACTIVE)

| Field | Value |
|-------|-------|
| Portfolio NAV | $50,000 (paper) |
| Mode | `rl_e7` — dual-mode RL regime controller |
| T=0 date | 2026-05-09 |
| Allocation | Equity 25% / Trend 62.14% / Cash 12.86% |
| Next rebalance | ~2026-05-23 (every 14 days) |
| Production model | `rl_e7_clean_promoted` — Sharpe 1.296, MaxDD −24.5%, CAGR 17.8% (2019–2026) |

---

## Phase H — Daily Operations Runbook

### Every trading day (~5 min, after 16:05 ET)

```bash
.venv/bin/python scripts/run_daily_paper_ops.py --date YYYY-MM-DD
```

This runs 8 steps automatically:

| Step | Script | Output |
|------|--------|--------|
| 0 | `refresh_market_data.py` | Incremental price + feature update (`data/raw/`, `data/features/`) |
| 1 | `run_prod_signal.py` | `data/allocations/{date}.json` |
| 2 | `run_drift_monitor_g3.py` | `data/drift/flags.parquet` |
| 3 | `compute_paper_orders.py` | `data/paper_trading/orders_{date}.csv` |
| 4 | `log_paper_fills.py` | `fills_{date}.csv` + `positions_latest.parquet` |
| 5 | `run_benchmark_dashboard_g5.py` | `artifacts/reports/benchmark_dashboard.html` |
| 6 | `generate_paper_journal.py` | `docs/paper_trading/YYYY-MM-DD.md` + rolling journal |
| 7 | `append_experience_log.py` | `experience_log.parquet` (rebalance days only) |

After it runs, open `docs/paper_trading/YYYY-MM-DD.md` for the day's summary.

### Rebalance days (~15 min, every 14 days)

Rebalances trigger automatically inside the daily command when 14 calendar days have elapsed
since the last rebalance. **No separate command needed** — just run the same daily command.

**Rebalance schedule:**

| Rebalance | Target date |
|-----------|-------------|
| T=0 bootstrap | 2026-05-09 ✅ |
| R1 | ~2026-05-23 |
| R2 | ~2026-06-06 |
| R3 | ~2026-06-20 |
| R4 | ~2026-07-04 |
| Mid-point review | ~2026-06-14 (after R3) |
| Exit gate | Week 11+ (~2026-07-18) |

**After the daily command completes on a rebalance day, review:**

1. `docs/paper_trading/YYYY-MM-DD.md` — orders table, slippage table, H-gate status
2. Turnover — must be < 35% (H-3 gate)
3. Max weight drift — must be < 5pp (H-4 gate)
4. RL mode — should show `rl_e7`; if `b5_only` for 2+ rebalances in a row, investigate switching rule
5. Drift flags — if ≥ 2 active, check `data/drift/flags.parquet`

### Mid-point review (week 5, ~2026-06-14)

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

Pass criteria: avg slippage < 20 bps, pipeline errors < 2, RL mode seen at least once.

---

## Phase H Exit Gates

All 8 must pass before deploying real capital:

| # | Gate | Threshold |
|---|------|-----------|
| H-1 | Pipeline reliability | Zero unrecovered signal failures (last 4 weeks) |
| H-2 | Avg fill slippage | < 20 bps cumulative avg |
| H-3 | Rebalance turnover | < 35% avg |
| H-4 | Weight drift | Max < 5pp on any position for > 2 days |
| H-5 | RL mode operational | At least one rebalance in `rl_e7` mode |
| H-6 | Paper Sharpe (8w) | ≥ B.5 paper Sharpe − 0.20 |
| H-7 | Data parity | G.0 feature parity check still passing |
| H-8 | Audit trail | 100% of rebalance decisions queryable |

Full spec: [`docs/phases/phase_h.md`](docs/phases/phase_h.md)

---

## Architecture

```
Market data (yfinance)
    └─> data/raw/{ticker}.parquet          per-ticker OHLCV + adj_close
    └─> data/features/{ticker}.parquet     32 engineered features (point-in-time safe)

Signal pipeline
    └─> B.5 vol_score weights              locked alpha signal
    └─> RL regime controller (rl_e7)       sets equity / trend / cash sleeve fractions
    └─> data/allocations/{date}.json       target weights + RL state + audit fields

Paper trading loop
    └─> data/paper_trading/orders_{date}.csv
    └─> data/paper_trading/fills_{date}.csv
    └─> data/paper_trading/positions_latest.parquet
    └─> docs/paper_trading/YYYY-MM-DD.md   per-day journal entry
    └─> docs/paper_trading_journal.md      rolling journal (newest first)
```

Full architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Historical Pipeline Commands (Phases A–G, already complete)

```bash
# One-time data download and feature build
.venv/bin/python scripts/download_data.py --config config/base.yaml
.venv/bin/python scripts/build_features.py --config config/base.yaml --universe config/universes/sp500.yaml

# Walk-forward backtest
.venv/bin/python scripts/run_backtest.py --config config/base.yaml

# Signal only (no paper trading loop)
.venv/bin/python scripts/run_prod_signal.py --as-of YYYY-MM-DD
```

---

## Key Artifacts

| Path | Description |
|------|-------------|
| `artifacts/production/rl_e7_clean_promoted.zip` | Production RL model (E.7, ep=51) |
| `artifacts/production/rl_e7_manifest.json` | Model provenance, holdout metrics, promotion gates |
| `config/paper_trading.yaml` | Paper trading config (frozen at v H.0.0) |
| `data/allocations/latest.json` | Most recent signal allocation |
| `data/paper_trading/positions_latest.parquet` | Current portfolio snapshot |
| `docs/paper_trading/` | Per-date journal files (`YYYY-MM-DD.md`) |
| `docs/paper_trading_journal.md` | Rolling daily journal (newest first) |
| `docs/ROADMAP.md` | Phase overview and current state |
| `docs/phases/phase_h.md` | Full Phase H spec, ops runbook, exit gates |

---

## Testing

```bash
pytest -q tests/
```

---

## Roadmap

| Phase | Status |
|-------|--------|
| A — Alpha discovery | ✅ Complete |
| B — Portfolio stabilization (B.5) | ✅ Complete |
| C — Model refinement | ✅ Complete — vol_score unchanged |
| D — RL sector tilts | ✅ Complete — REJECT |
| E — RL regime controller | ✅ Complete — PROMOTE (Sharpe 1.296) |
| F — Policy hardening | ✅ Complete |
| G — Production infrastructure | ✅ Complete |
| **H — Paper trading** | 🔄 **ACTIVE** — T=0 live 2026-05-09 |
| PROD — Live deployment | ⏳ Pending Phase H exit gates |

Full roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md)
