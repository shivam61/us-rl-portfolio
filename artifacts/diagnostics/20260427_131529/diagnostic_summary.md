# Diagnostic Summary
Generated: 2026-04-27 13:31:35.505450
Universe:  sp500_dynamic  (503 tickers)
Top-N:     50 stocks

## Ablation
| Experiment | CAGR | Sharpe | MaxDD | Vol |
|---|---|---|---|---|
| Alpha_Top50_EW | 15.31% | 0.62 | -62.04% | 24.77% |

## Alpha Quality
- Mean Rank IC:    0.0056
- Median Rank IC:  -0.0013
- % Positive IC:   49.6%
- Mean Spread:     0.0009
- Mean Top Decile: 0.0175
- Mean Bot Decile: 0.0166
- Precision@20:    0.1591
- Precision@50:    0.2517
- Sector IC (mean across rebalances):
  - XLI: 0.0311
  - XLK: 0.0269
  - XLP: 0.0232
  - XLY: 0.0141
  - XLF: 0.0086
  - XLC: 0.0055
  - XLU: -0.0125
  - XLV: -0.0182
  - XLB: -0.0216
  - XLRE: -0.0450
  - XLE: -0.0462

## Training Benchmark
- Retrain every N rebalances: 3
- Train calls:         77
- Avg train time:      11.95s
- Total train time:    920s (15.3 min)
- IC mean:             0.0056
- IC std:              0.1302
- CAGR:                15.31%
- Sharpe:              0.62
- Max Drawdown:        -62.04%
- Avg Turnover:        51.45%

## Exposure & Holdings
- Avg Gross Exposure:  96.23%
- Avg Cash:            3.77%
- Avg Holdings:        48.1
- Avg HHI:             0.0569
- Avg Effective N:     48.2
- % Rebalances w/ Risk Trigger: 0.00%

## Key Findings
- **Alpha Top-50 EW**: CAGR=15.31%  Sharpe=0.62
- **IC BELOW TARGET**: 0.0056 (target >0.04)