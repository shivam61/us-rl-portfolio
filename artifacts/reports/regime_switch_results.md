# Regime Switch Results

- Run date: 2026-04-28
- Universe: `config/universes/sp100.yaml`
- Eval window: `2016-01-01` to `2026-01-01`
- Regime rules: `high_vol` if VIX pct >= 0.80 or SPY drawdown <= -10% or realized vol pct >= 0.80; `low_vol` if VIX pct <= 0.20 and SPY drawdown >= -5% and realized vol pct <= 0.20; else `neutral`
- Selection map: `high_vol -> mean_reversion`, `low_vol -> volatility`, `neutral -> trend`
- Wall time: 91.2s

## IC Summary

| score                |   mean_ic |   ic_sharpe |   top_bot_spread |
|:---------------------|----------:|------------:|-----------------:|
| volatility_score     |    0.0547 |      0.2085 |           1.7948 |
| regime_switch_score  |    0.0427 |      0.1834 |           1.2727 |
| mean_reversion_score |    0.0154 |      0.0554 |           0.6418 |
| trend_score          |    0.0078 |      0.0407 |           0.0778 |

## Regime-Wise IC

| score                | regime   |   mean_ic |   ic_sharpe |   top_bot_spread |   n_dates |
|:---------------------|:---------|----------:|------------:|-----------------:|----------:|
| mean_reversion_score | high_vol |    0.0386 |      0.1373 |           1.0676 |       801 |
| mean_reversion_score | low_vol  |   -0.0036 |     -0.0141 |           0.5720 |       437 |
| mean_reversion_score | neutral  |    0.0112 |      0.0430 |           0.2857 |      1276 |
| regime_switch_score  | high_vol |    0.0386 |      0.1373 |           1.0676 |       801 |
| regime_switch_score  | low_vol  |    0.0733 |      0.3218 |           2.5768 |       437 |
| regime_switch_score  | neutral  |    0.0161 |      0.0912 |           0.1736 |      1276 |
| trend_score          | high_vol |   -0.0067 |     -0.0457 |           0.0018 |       801 |
| trend_score          | low_vol  |    0.0139 |      0.0766 |           0.0580 |       437 |
| trend_score          | neutral  |    0.0161 |      0.0912 |           0.1736 |      1276 |
| volatility_score     | high_vol |    0.0464 |      0.1403 |           1.2363 |       801 |
| volatility_score     | low_vol  |    0.0733 |      0.3218 |           2.5768 |       437 |
| volatility_score     | neutral  |    0.0443 |      0.1633 |           1.5714 |      1276 |

## Backtest

|   Total Return |   CAGR |   Volatility |   Sharpe |   Sortino |   Max Drawdown |   Calmar | score                |   mean_ic |   alpha_obs |
|---------------:|-------:|-------------:|---------:|----------:|---------------:|---------:|:---------------------|----------:|------------:|
|         9.2869 | 0.1361 |       0.1504 |   0.9048 |    1.0907 |        -0.3186 |   0.4272 | volatility_score     |    0.0408 |         238 |
|         9.1067 | 0.1350 |       0.1504 |   0.8977 |    1.0819 |        -0.3186 |   0.4238 | mean_reversion_score |    0.0098 |         238 |
|         9.1067 | 0.1350 |       0.1504 |   0.8977 |    1.0819 |        -0.3186 |   0.4238 | trend_score          |    0.0027 |         238 |
|         9.0840 | 0.1349 |       0.1504 |   0.8968 |    1.0808 |        -0.3186 |   0.4233 | regime_switch_score  |    0.0171 |         238 |

## Success Criteria

| Criterion | Regime Switch | Baseline | Pass? |
|---|---:|---:|---|
| IC Sharpe > 0.2 | 0.1834 | 0.2000 | ❌ |
| CAGR improves vs best single-factor | 0.1349 | 0.1361 (volatility_score) | ❌ |
| Max drawdown improves vs best single-factor | -0.3186 | -0.3186 (volatility_score) | ❌ |

## Notes

- Best single-factor IC Sharpe: `volatility_score` at `0.2085`.
- Best single-factor CAGR: `volatility_score` at `0.1361`.
- Lowest single-factor drawdown: `volatility_score` at `-0.3186`.