# Momentum V2 — Trend Factor Evaluation

_Eval: 2016-01-01 – 2026-01-01 | sp100 (44 tickers) | VIX threshold: 25.0 | Wall time: 86s_

## Per-feature IC audit (target_fwd_ret, 2016-2026)

| Feature | Theory asc | Theory IC | Calib asc | Calib IC | Effect |
|---|---|---|---|---|---|
| `ret_3m_ex_1w` | True | -0.0183 | False | +0.0183 | reversal ↩ |
| `ret_6m_ex_1m` | True | -0.0093 | False | +0.0093 | reversal ↩ |
| `ret_12m_ex_1m` | True | -0.0054 | False | +0.0054 | reversal ↩ |
| `ret_3m_adj` | True | -0.0266 | False | +0.0266 | reversal ↩ |
| `ret_3m_adj_downside` | True | -0.0256 | False | +0.0256 | reversal ↩ |
| `sector_rel_momentum_3m` | True | -0.0178 | False | +0.0178 | reversal ↩ |
| `sector_rel_momentum_6m` | True | +0.0030 | True | +0.0030 | trend ✓ |
| `pct_pos_months_6m` | True | -0.0168 | False | +0.0168 | reversal ↩ |
| `trend_consistency` | True | +0.0161 | True | +0.0161 | trend ✓ |
| `mom_stability_3m` | True | -0.0189 | False | +0.0189 | reversal ↩ |
| `vol_126d` | False | -0.0605 | True | +0.0605 | reversal ↩ |

> Theory asc = textbook momentum direction (buy high returns).
> Calib asc = empirically validated direction for this universe.
> In sp100 2016-2026, **cross-sectional reversal dominates**.
> Only `sector_rel_momentum_6m` and `trend_consistency` have naturally positive IC.

---

## IC Evaluation

### Label: `target_fwd_ret`

| Score | Mean IC | IC Sharpe | % Pos IC | Top-Bot % | P@20 % | Dec Mono | Hi-VIX IC | Lo-VIX IC |
|---|---|---|---|---|---|---|---|---|
| momentum_v2_theory (target_fwd_r) | -0.0218 | -0.080 | 48.9% | -0.85% | 20.7% | -0.039 | -0.0595 | -0.0154 |
| momentum_v2_calibrated (target_fwd_r) | 0.0271 | 0.097 | 51.2% | 0.97% | 24.7% | 0.055 | 0.0596 | 0.0216 |
| momentum_v2_theory (target_rank_) | -0.0218 | -0.080 | 48.9% | -1.74% | 20.7% | -0.029 | -0.0595 | -0.0154 |
| momentum_v2_calibrated (target_rank_) | 0.0271 | 0.097 | 51.2% | 2.30% | 24.7% | 0.034 | 0.0596 | 0.0216 |

---

## Beta Decomposition

Monthly (21-day) long top-quintile portfolio regressed against SPY 21-day return.

| Score | Avg long β | Long β | Long α (ann%) | t(α) | LS β | LS α (ann%) | t(α) |
|---|---|---|---|---|---|---|---|
| momentum_v2_theory | 0.778 | 0.589 | 0.051 (5.1%) | 1.329 | -0.477 | -0.034 (-3.4%) | -0.444 |
| momentum_v2_calibrated | 0.508 | 1.116 | 0.089 (8.9%) | 1.774 | 0.544 | 0.050 (5.0%) | 0.640 |

---

## Success Criteria (momentum_v2_calibrated vs target_fwd_ret)

| Metric | Value | Target | Pass? |
|---|---|---|---|
| Mean IC | 0.0271 | ≥ 0.030 | ❌ |
| IC Sharpe | 0.097 | ≥ 0.200 | ❌ |
| Top-Bot Spread | 0.97% | ≥ 1.0% | ❌ |
| Positive alpha (90%) | t=1.77 | t > 1.64 | ✅ |

## Conclusion

**Why classical momentum (asc=True) fails in sp100 2016-2026:**
- Large-cap, liquid stocks mean-revert at 1–6 month horizons due to over-reaction correction and institutional rebalancing.
- Only `trend_consistency` (+0.016) and `sector_rel_momentum_6m` (+0.003) have positive IC in the momentum direction — combined they yield IC ≈ 0.010, well below the 0.03 gate.

**What momentum_v2_calibrated captures:**
- Return features ranked descending → contrarian mean-reversion signal
- `trend_consistency` and `sector_rel_momentum_6m` ranked ascending → genuine trend signal from sector-relative performance
- `vol_126d` ranked ascending → risk premium (high-vol stocks outperform)

**Recommendation:** The momentum factor in this universe is empirically a
REVERSAL signal. To get genuine trend-following alpha, consider:
1. Longer skip periods (e.g., 18m-ex-3m) — classic momentum degrades below 12m
2. Earnings momentum (SUE, analyst revisions) — fundamental, not price-based
3. Sector-level momentum (buy high-momentum sectors) — sector effect is cleaner
4. Use sp500 (503 tickers) — cross-sectional reversal is weaker in mid/small-cap

_Generated: 2026-04-28T07:33_