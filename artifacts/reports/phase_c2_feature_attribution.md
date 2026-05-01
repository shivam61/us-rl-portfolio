# Phase C.2 — Feature Attribution and Anti-Predictive Feature Pruning

- Run date: 2026-05-01 11:41:45 UTC
- Phase B.5 baseline: CAGR `16.04%`, Sharpe `1.078`, MaxDD `-32.98%`
- Universe: sp500, holdout 2019-01-01 to 2026-04-24.
- IC metric: rank IC (Spearman) vs 21-day forward return.

## Verdict: POSITIVE IC FOUND — proceed to C.3

## Feature IC Summary (sorted by holdout IC Sharpe)

| Feature | holdout_mean_ic | holdout_ic_sharpe | holdout_sign_stability | train_mean_ic | train_ic_sharpe | anti_pred |
|---|---|---|---|---|---|---|
| beta_to_spy_63d | 0.0495 | 1.7883 | 0.553 | 0.0230 | 1.0850 |  |
| downside_vol_63d | 0.0435 | 1.7823 | 0.532 | 0.0253 | 1.3310 |  |
| volatility_21d | 0.0405 | 1.7621 | 0.553 | 0.0169 | 0.9183 |  |
| volatility_63d | 0.0448 | 1.7574 | 0.521 | 0.0249 | 1.2889 |  |
| vol_score_composite | 0.0458 | 1.6682 | 0.521 | 0.0232 | 1.1156 |  |
| liquidity_rank | 0.0109 | 1.0227 | 0.543 | -0.0062 | -0.8074 |  |
| avg_dollar_volume_63d | 0.0109 | 1.0227 | 0.543 | -0.0062 | -0.8074 |  |
| ret_12m_ex_1m | 0.0150 | 0.6317 | 0.574 | -0.0129 | -0.7226 |  |
| ret_12m | 0.0146 | 0.6130 | 0.585 | -0.0131 | -0.7067 |  |
| sector_rel_momentum_6m | 0.0072 | 0.3706 | 0.585 | -0.0016 | -0.1164 |  |
| trend_consistency | 0.0036 | 0.3452 | 0.489 | 0.0131 | 1.5693 |  |
| ma_50_200_ratio | 0.0076 | 0.3222 | 0.574 | -0.0124 | -0.7440 |  |
| above_200dma | 0.0040 | 0.2204 | 0.532 | -0.0077 | -0.5733 |  |
| ret_6m_adj | 0.0044 | 0.2014 | 0.574 | -0.0093 | -0.5926 |  |
| ret_6m | 0.0024 | 0.1078 | 0.574 | -0.0099 | -0.5985 |  |
| ret_6m_ex_1m | -0.0020 | -0.0914 | 0.521 | -0.0134 | -0.8773 | YES |
| ret_zscore_21d | -0.0018 | -0.1151 | 0.532 | -0.0117 | -0.8814 | YES |
| sector_rel_momentum_3m | -0.0020 | -0.1190 | 0.553 | 0.0001 | 0.0109 | YES |
| gap_overnight | -0.0038 | -0.1975 | 0.479 | -0.0074 | -0.6063 | YES |
| mom_stability_3m | -0.0048 | -0.2979 | 0.468 | -0.0038 | -0.3267 | YES |
| ret_3m_ex_1w | -0.0070 | -0.3427 | 0.532 | -0.0107 | -0.7359 | YES |
| ret_1m | -0.0061 | -0.3489 | 0.511 | -0.0105 | -0.7616 | YES |
| overextension_20dma | -0.0069 | -0.3639 | 0.489 | -0.0044 | -0.3383 | YES |
| ret_3m_adj | -0.0074 | -0.3787 | 0.553 | -0.0117 | -0.8381 | YES |
| ret_3m | -0.0086 | -0.4346 | 0.521 | -0.0074 | -0.5027 | YES |
| relative_strength_vs_spy_63d | -0.0086 | -0.4346 | 0.521 | -0.0074 | -0.5027 | YES |
| pct_pos_months_6m | -0.0073 | -0.4701 | 0.500 | -0.0147 | -1.1333 | YES |
| above_50dma | -0.0078 | -0.5703 | 0.543 | -0.0079 | -0.6733 | YES |
| rsi_proxy | -0.0112 | -0.6682 | 0.447 | -0.0093 | -0.6883 | YES |
| ret_1w | -0.0138 | -0.7586 | 0.457 | 0.0022 | 0.1871 | YES |
| price_to_52w_high | -0.0197 | -0.8022 | 0.511 | -0.0262 | -1.4450 | YES |
| ret_2w | -0.0209 | -1.1229 | 0.479 | 0.0031 | 0.2502 | YES |
| max_drawdown_63d | -0.0339 | -1.4049 | 0.468 | -0.0164 | -0.9134 | YES |

## Anti-Predictive Features

Criterion: holdout mean IC < 0 OR holdout sign stability < 0.45
Count: 18 / 32 features (excl. vol_score_composite)

- `ret_6m_ex_1m`
- `ret_zscore_21d`
- `sector_rel_momentum_3m`
- `gap_overnight`
- `mom_stability_3m`
- `ret_3m_ex_1w`
- `ret_1m`
- `overextension_20dma`
- `ret_3m_adj`
- `ret_3m`
- `relative_strength_vs_spy_63d`
- `pct_pos_months_6m`
- `above_50dma`
- `rsi_proxy`
- `ret_1w`
- `price_to_52w_high`
- `ret_2w`
- `max_drawdown_63d`

## Feature Subset IC Sharpe Comparison (holdout)

| subset               |   feature_count |   mean_ic |   ic_sharpe |   sign_stability |   n |
|:---------------------|----------------:|----------:|------------:|-----------------:|----:|
| vol_score_standalone |               4 |    0.0458 |      1.6682 |           0.5213 |  94 |
| momentum_core        |               6 |    0.0263 |      1.5926 |           0.5106 |  94 |
| vol_features_lgbm    |               4 |    0.0214 |      1.1960 |           0.5319 |  94 |
| all_features         |              32 |   -0.0021 |     -0.1389 |           0.5000 |  94 |
| vol_plus_momentum    |              10 |   -0.0024 |     -0.1673 |           0.4894 |  94 |
| no_anti_predictive   |              14 |   -0.0141 |     -1.0053 |           0.4787 |  94 |
| positive_ic_holdout  |              14 |   -0.0142 |     -1.0187 |           0.4681 |  94 |

**Best subset:** `vol_score_standalone` (4 features)

Features: `volatility_63d`, `downside_vol_63d`, `max_drawdown_63d`, `beta_to_spy_63d`

## Model Sanity Comparison (holdout, best feature subset)

| model            |   feature_count |   mean_ic |   ic_sharpe |   sign_stability |   n |
|:-----------------|----------------:|----------:|------------:|-----------------:|----:|
| simple_mean_rank |              14 |    0.0346 |      1.8559 |           0.5957 |  94 |
| vol_score_rank   |               4 |    0.0458 |      1.6682 |           0.5213 |  94 |
| lgbm_ranker      |               4 |    0.0258 |      1.6595 |           0.6064 |  94 |
| ridge_regressor  |               4 |    0.0339 |      1.5103 |           0.5745 |  94 |
| lgbm_regressor   |               4 |    0.0214 |      1.1960 |           0.5319 |  94 |

## Portfolio Validation

_Skipped — best subset is `vol_score_standalone` (no model), which is already the production signal validated in Phase B.5. Next: C.3 portfolio validation of `simple_mean_rank` (IC Sharpe=1.8559) vs B.5 baseline._

## Output Files

- `artifacts/reports/phase_c2_feature_attribution.md`
- `artifacts/reports/feature_ic_by_regime.csv`
- `artifacts/reports/feature_ic_by_period.csv`
- `artifacts/reports/anti_predictive_features.csv`
- `artifacts/reports/feature_subset_results.csv`
- `artifacts/reports/model_sanity_comparison.csv`

