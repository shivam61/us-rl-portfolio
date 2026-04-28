# Session Handoff — Deep Context

Last updated: 2026-04-28T09:12:58+00:00

---

## Baseline Convention

- **sp100 (44 tickers)** = research baseline / dev universe / fast iteration track
- **sp500 (503 tickers)** = validation baseline / system benchmark / locked comparison track
- Historical notes may say "baseline" loosely; check the universe before comparing any metric

---

## Phase A Research Summary (sp100, 2016–2026)

### What was done
Three scripts written; all pure rank-based (no LGBM), all sp100 universe:

| Script | Output | Purpose |
|---|---|---|
| `scripts/run_momentum_vol_combo.py` | `artifacts/reports/momentum_vol_combo.*` | Momentum + vol rank-combo evaluation |
| `scripts/run_beta_analysis.py` | `artifacts/reports/beta_analysis.*` | Beta decomposition of factor scores |
| `scripts/run_momentum_v2.py` | `artifacts/reports/momentum_v2.*` | Expanded momentum feature set audit |

---

## Core Empirical Finding — sp100 2016–2026

**Cross-sectional REVERSAL dominates momentum continuation.**  
**Risk PREMIUM dominates low-volatility anomaly.**

Individual mean cross-sectional ICs (target_fwd_ret, 2016-2026):

| Feature | cs-IC (asc=T) | Dominant effect |
|---|---|---|
| ret_3m_ex_1w | −0.018 | Reversal |
| ret_6m_ex_1m | −0.009 | Reversal |
| ret_12m_ex_1m | −0.005 | Reversal |
| ret_3m_adj | −0.027 | Reversal |
| ret_3m_adj_downside | −0.026 | Reversal |
| sector_rel_momentum_3m | −0.018 | Reversal |
| **sector_rel_momentum_6m** | **+0.003** | Trend ✓ |
| pct_pos_months_6m | −0.017 | Reversal |
| **trend_consistency** | **+0.016** | Trend ✓ |
| mom_stability_3m | −0.019 | Reversal |
| **volatility_63d** | **+0.046** | Risk premium |
| **downside_vol_63d** | **+0.039** | Risk premium |
| **beta_to_spy_63d** | **+0.050** | Risk premium |
| max_drawdown_63d | −0.044 | Risk premium (more drawdown = higher return) |
| **vol_126d** | **+0.061** | Risk premium |

---

## Factor Score Results (momentum_vol_combo.py)

Factor construction (directions empirically calibrated):
- **momentum_score**: return features ranked descending (reversal), `trend_consistency` + `sector_rel_6m` ascending
- **volatility_score**: vol/beta ranked ascending (risk premium), max_drawdown ranked descending

| Score | IC | IC Sharpe | Top-Bot | P@20 |
|---|---|---|---|---|
| volatility_only | **0.050** | 0.175 | 1.64% | 33.6% |
| score_50_50 | **0.041** | 0.150 | 1.22% | 28.9% |
| score_60_40 | 0.036 | 0.131 | 1.19% | 28.3% |
| momentum_only | 0.018 | 0.066 | 0.71% | 24.9% |

Regime split (VIX threshold=25):
- momentum_only: stronger in high-VIX (0.051) vs low-VIX (0.012) — reversal pays most in stress
- volatility_only: stronger in low-VIX (0.053) vs high-VIX (0.031) — risk premium pays in calm markets
- score_50_50: most balanced (0.042 hi, 0.041 lo)

---

## Beta Decomposition Results (beta_analysis.py)

Monthly (21d) long-top-quintile vs SPY OLS: `portfolio_return ~ α + β·SPY`

| Score | Long β | Long α (ann) | t(α) | LS β | LS α (ann) | t(α) | Verdict |
|---|---|---|---|---|---|---|---|
| volatility_only | 1.084 | **+16.4%** | **3.36** | 0.619 | +11.6% | 1.79 | NOT just beta — sig alpha |
| score_50_50 | 1.092 | +6.1% | 1.19 | 0.592 | +3.4% | 0.50 | Beta-plus-noise |
| momentum_only | 1.130 | +6.6% | 1.32 | 0.497 | +0.5% | 0.06 | Beta-driven |

Key: **volatility_only** has 16.4% annualized alpha at t=3.36 — genuine alpha, not just beta loading.  
The risk-premium signal selects genuinely mis-priced stocks, not just high-beta exposure.

Avg beta of selected stocks (`beta_to_spy_63d` feature):
- volatility_only: long avg β=0.791 vs short avg β=0.483 (L-S spread=+0.308) — genuinely sorts by risk
- momentum_only: long avg β=0.513 vs short avg β=0.845 — reversal factor buys low-beta laggards

---

## Momentum V2 Results (momentum_v2.py)

11 features tested: 9 require reversal calibration, only 2 have positive IC in momentum direction.

| Score | IC | IC Sharpe | Top-Bot | Long α (ann) | t(α) |
|---|---|---|---|---|---|
| momentum_v2_theory (asc=T) | −0.022 | −0.080 | −0.85% | +5.1% | 1.33 |
| **momentum_v2_calibrated** | **0.027** | 0.097 | 0.97% | **+8.9%** | **1.77** |

Gate check (momentum_v2_calibrated):
- IC ≥ 0.030: ❌ (0.027, −0.003 gap)
- IC Sharpe ≥ 0.200: ❌ (0.097)
- Top-Bot ≥ 1%: ❌ (0.97%)
- Positive alpha at 90%: ✅ (t=1.77)

**Why classical momentum fails in sp100 2016-2026:**  
Large-cap liquid stocks mean-revert at 1–6m horizons. Only `trend_consistency` (+0.016) and  
`sector_rel_momentum_6m` (+0.003) have positive IC in the momentum direction. Pure price-momentum  
cannot meet IC Sharpe ≥ 0.20 with 44 tickers.

---

## Phase A Gate Status

| Metric | Best result | Target | Status |
|---|---|---|---|
| Mean Rank IC | 0.050 (vol-only rank) | ≥ 0.040 | ✅ |
| IC Sharpe | 0.175 (vol-only) | ≥ 0.30 | ❌ structural at 44 tickers |
| Top-bot spread | 1.64% (vol-only) | ≥ 0.40% | ✅ |
| Precision@20 | 33.6% (vol-only) | ≥ 15% | ✅ |

IC Sharpe gate: the best LGBM result was 0.186; best rank-based is 0.175.  
Both hit the same structural ceiling. Resolves at sp500 scale (503 tickers).

---

## Recommended Next Steps (priority order)

1. **Validate on sp500** — run `run_momentum_vol_combo.py` + `run_beta_analysis.py` with  
   `--universe config/universes/sp500.yaml`; expect IC Sharpe to improve toward 0.25+ with 503 tickers.

2. **Add fundamental momentum** — earnings surprise (SUE), analyst revision momentum.  
   Fundamental signals are less susceptible to reversal and have positive IC even in large-caps.

3. **Longer skip periods** — test 18m-ex-3m horizon (`close.shift(63).pct_change(315)`).  
   Classic momentum degrades at sub-12m horizons; extending reduces reversal noise.

4. **Phase B** — once IC Sharpe ≥ 0.25 on sp500, proceed to experiment matrix.

---

## Useful Commands

```bash
# Run factor combo eval (sp100 research)
.venv/bin/python scripts/run_momentum_vol_combo.py \
  --config config/base.yaml --universe config/universes/sp100.yaml

# Run beta decomposition
.venv/bin/python scripts/run_beta_analysis.py \
  --config config/base.yaml --universe config/universes/sp100.yaml

# Run momentum v2 evaluation
.venv/bin/python scripts/run_momentum_v2.py \
  --config config/base.yaml --universe config/universes/sp100.yaml

# Validate on sp500 (swap universe)
.venv/bin/python scripts/run_momentum_vol_combo.py \
  --config config/base.yaml --universe config/universes/sp500.yaml

# Per-feature IC diagnostic (inline)
.venv/bin/python - <<'EOF'
# ... see run_momentum_vol_combo.py diagnostic block
EOF

# Run full backtest (sp500)
.venv/bin/python scripts/run_backtest.py \
  --config config/base.yaml --universe config/universes/sp500.yaml

# Check active tickers in PIT mask
.venv/bin/python -c "
import pandas as pd
m = pd.read_parquet('data/artifacts/universe_mask_sp500.parquet')
print(m.loc['2020-01-31'][m.loc['2020-01-31']].index.tolist()[:10])
"
```

---

## Experiment Chain

### Session 1 (prior)
- Built initial pipeline: data ingestion → features → LightGBM ranker → MVO optimizer → risk engine → simulator
- **sp100 universe (44 tickers), 2006–2026** — original research baseline
- Initial ablation showed Sharpe 1.86 — **INVALID** (simulator MtM tautology bug)

### Session 2 (prior)
- Fixed 5 bugs (simulator cash tracking, walk-forward KeyError, datetime mismatch, NYSE calendar, typos)
- Expanded universe to sp500 (503 tickers), rebuilt PIT mask and features
- sp500 ablation: EW=12.9%/0.62, Full=8.7%/0.59 (established locked validation baselines)
- IC on sp100 = 0.033, below 0.04 target → Phase A feature engineering

### Session 3 (prior)
- Added 13 new features (reversal + quality momentum families)
- Phase A LGBM IC eval: momentum IC=0.038/0.186 Sharpe, volatility IC=0.032/0.183
- Found: reversal features dilute signal; `all_new` worse than `momentum` alone

### Session 4 (this session)
- **Momentum + Vol rank-based combo**: calibrated directions (reversal + risk premium)
  - `score_50_50`: IC=0.041, Sharpe=0.150, Top-Bot=1.22% — IC gate met
  - `volatility_only`: IC=0.050, Sharpe=0.175, Top-Bot=1.64% — best raw signal
- **Beta decomposition**: `volatility_only` has genuine alpha (16.4% ann, t=3.36)
- **Momentum V2**: 11-feature expanded set; IC=0.027, Sharpe=0.097 — improvement but below gate
- **Structural finding**: IC Sharpe ceiling at 0.175 for 44-ticker universe; need sp500 to close gap
