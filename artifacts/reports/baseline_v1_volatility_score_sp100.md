# Baseline Freeze — `baseline_v1_volatility_score_sp100`

- Baseline name: `baseline_v1_volatility_score_sp100`
- Exact run ID: `baseline_v1_volatility_score_sp100_2026-04-28T12:25:04Z`
- Frozen on: `2026-04-28`
- Universe: `config/universes/sp100.yaml`
- Config path: `config/baseline_v1_volatility_score_sp100.yaml`
- Default config path: `config/base.yaml`

## Strategy Definition

- Alpha: `volatility_score`
- Optimizer: enabled
- Risk engine: enabled
- Sector cap: `20%`
- RL: disabled

## Frozen Metrics

- CAGR: `18.13%`
- Sharpe: `0.941`
- MaxDD: `-36.50%`
- Reference sleeve: `volatility_sector_cap_20`

## Artifact Paths

- Production report: `artifacts/reports/volatility_alpha_production.md`
- Top-N sweep: `artifacts/reports/volatility_topn_sensitivity.csv`
- Sector-cap sweep: `artifacts/reports/volatility_sector_cap_sensitivity.csv`

## Next Work

- Optimizer stability hardening
- Drawdown analysis
