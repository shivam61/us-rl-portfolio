# Volatility Alpha Production

- Run date: 2026-04-28 12:25:04 UTC
- Universe: `sp100_sample`
- Default alpha score: `volatility_score`
- RL enabled: `False`
- Wall time: 165.8s

## Production Decision

- `volatility_score` is the default production alpha sleeve.
- `trend_score` and `mean_reversion_score` remain research-only in `scripts/run_regime_switch_strategy.py`.
- Top-N sensitivity below uses equal-weight construction only.
- Sector-cap sensitivity below uses `volatility_score + optimizer + risk engine`.

## Core Backtests

| variant                   |    top_n |   sector_cap | use_optimizer   | use_risk_engine   |   cagr |   sharpe |   max_dd |   volatility |   mean_ic |   ic_sharpe |   mean_spread |   n_rebalances |
|:--------------------------|---------:|-------------:|:----------------|:------------------|-------:|---------:|---------:|-------------:|----------:|------------:|--------------:|---------------:|
| volatility_topn_ew        |  50.0000 |       0.2500 | False           | False             | 0.1616 |   0.8523 |  -0.4306 |       0.1896 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_optimizer      | nan      |       0.2500 | True            | False             | 0.2086 |   0.8591 |  -0.5159 |       0.2428 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_optimizer_risk | nan      |       0.2500 | True            | True              | 0.1797 |   0.9320 |  -0.3651 |       0.1928 |    0.0408 |      0.1259 |        0.0168 |            238 |

## Top-N Sensitivity

| variant            |   top_n |   sector_cap | use_optimizer   | use_risk_engine   |   cagr |   sharpe |   max_dd |   volatility |   mean_ic |   ic_sharpe |   mean_spread |   n_rebalances |
|:-------------------|--------:|-------------:|:----------------|:------------------|-------:|---------:|---------:|-------------:|----------:|------------:|--------------:|---------------:|
| volatility_topn_20 |      20 |       0.2500 | False           | False             | 0.1976 |   0.8143 |  -0.5014 |       0.2426 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_topn_30 |      30 |       0.2500 | False           | False             | 0.1756 |   0.8239 |  -0.4570 |       0.2131 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_topn_40 |      40 |       0.2500 | False           | False             | 0.1617 |   0.8434 |  -0.4306 |       0.1917 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_topn_50 |      50 |       0.2500 | False           | False             | 0.1616 |   0.8523 |  -0.4306 |       0.1896 |    0.0408 |      0.1259 |        0.0168 |            238 |

## Sector Cap Sensitivity

| variant                  | top_n   |   sector_cap | use_optimizer   | use_risk_engine   |   cagr |   sharpe |   max_dd |   volatility |   mean_ic |   ic_sharpe |   mean_spread |   n_rebalances |
|:-------------------------|:--------|-------------:|:----------------|:------------------|-------:|---------:|---------:|-------------:|----------:|------------:|--------------:|---------------:|
| volatility_sector_cap_20 |         |       0.2000 | True            | True              | 0.1813 |   0.9409 |  -0.3650 |       0.1927 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_sector_cap_25 |         |       0.2500 | True            | True              | 0.1797 |   0.9320 |  -0.3651 |       0.1928 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_sector_cap_30 |         |       0.3000 | True            | True              | 0.1807 |   0.9372 |  -0.3651 |       0.1928 |    0.0408 |      0.1259 |        0.0168 |            238 |
| volatility_sector_cap_35 |         |       0.3500 | True            | True              | 0.1810 |   0.9390 |  -0.3651 |       0.1928 |    0.0408 |      0.1259 |        0.0168 |            238 |

## Success Criteria

- CAGR > 13.5%: PASS (17.97%)
- Sharpe > 0.9: PASS (0.932)
- MaxDD < 32%: FAIL (-36.51%)
- Portfolio uses `volatility_score` by default: PASS
- Momentum/regime features remain research-only: PASS
