# Feature Family IC Report

## Label: `target_fwd_ret`

| Family     |   Mean IC |   IC Sharpe |   Precision@20 |   Top-Bot Spread |
|:-----------|----------:|------------:|---------------:|-----------------:|
| momentum   |    0.0379 |      0.1860 |         0.2794 |           0.0123 |
| volatility |    0.0321 |      0.1833 |         0.2840 |           0.0094 |
| all_new    |    0.0310 |      0.1457 |         0.2745 |           0.0110 |
| baseline   |    0.0206 |      0.1022 |         0.2771 |           0.0060 |
| reversal   |    0.0149 |      0.0685 |         0.2644 |           0.0065 |

## Label: `target_rank_cs`

| Family     |   Mean IC |   IC Sharpe |   Precision@20 |   Top-Bot Spread |
|:-----------|----------:|------------:|---------------:|-----------------:|
| volatility |    0.0311 |      0.1772 |         0.2548 |           0.0230 |
| momentum   |    0.0270 |      0.1551 |         0.2595 |           0.0212 |
| baseline   |    0.0263 |      0.1370 |         0.2595 |           0.0236 |
| all_new    |    0.0205 |      0.1100 |         0.2529 |           0.0167 |
| reversal   |   -0.0003 |     -0.0015 |         0.2330 |          -0.0019 |

## Label: `target_fwd_ret_sector_rel`

| Family     |   Mean IC |   IC Sharpe |   Precision@20 |   Top-Bot Spread |
|:-----------|----------:|------------:|---------------:|-----------------:|
| baseline   |    0.0291 |      0.1763 |         0.2600 |           0.0050 |
| volatility |    0.0190 |      0.1136 |         0.2520 |           0.0044 |
| all_new    |    0.0177 |      0.1109 |         0.2565 |           0.0030 |
| momentum   |    0.0137 |      0.0881 |         0.2532 |           0.0019 |
| reversal   |    0.0060 |      0.0391 |         0.2265 |           0.0007 |


## Success Criteria

| Metric | Current | Phase A target |
|---|---|---|
| Mean Rank IC | 0.033 | ≥ 0.040 |
| IC Sharpe | 0.086 | ≥ 0.30 |
| Top-bot spread | 0.19% | ≥ 0.40% |
| Precision@20 | ~10% | ≥ 15% |

_Run: 15 jobs, 15×2 thread budget, 22s wall time_