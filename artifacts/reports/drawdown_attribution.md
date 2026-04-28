# Drawdown Attribution

- Config: `config/baseline_v1_volatility_score_sp100.yaml`
- Universe: `config/universes/sp100.yaml`
- Strategy unchanged: `volatility_score + optimizer + risk`, RL disabled

## Top 5 Drawdown Periods

|   period_id | start_date   | trough_date   | recovery_date   |   duration_days |   recovery_days |   depth |   avg_gross_exposure |   avg_net_exposure |   avg_sector_concentration |   max_sector_concentration |   avg_turnover |   avg_vix |   max_vix |   avg_spy_drawdown |   min_spy_drawdown |   avg_beta |   top10_loser_contribution |   mean_rebalance_ic |
|------------:|:-------------|:--------------|:----------------|----------------:|----------------:|--------:|---------------------:|-------------------:|---------------------------:|---------------------------:|---------------:|----------:|----------:|-------------------:|-------------------:|-----------:|---------------------------:|--------------------:|
|           1 | 2020-02-19   | 2020-03-23    | 2021-01-06      |              33 |             322 | -0.3706 |               0.8732 |             0.8732 |                     0.1641 |                     0.1998 |         0.0156 |   44.4750 |   82.6900 |            -0.1421 |            -0.3198 |     0.9943 |                    -0.2541 |             -0.1759 |
|           2 | 2022-01-04   | 2022-09-30    | 2024-02-08      |             269 |             765 | -0.3365 |               0.8348 |             0.8348 |                     0.1674 |                     0.2151 |         0.0129 |   25.7766 |   36.4500 |            -0.1227 |            -0.2318 |     0.9799 |                    -0.2152 |             -0.1056 |
|           3 | 2008-06-05   | 2008-11-20    | 2009-10-14      |             168 |             496 | -0.2983 |               0.5330 |             0.5330 |                     0.1277 |                     0.2242 |         0.0048 |   35.6037 |   80.0600 |            -0.2345 |            -0.4527 |     0.7156 |                    -0.3164 |             -0.2298 |
|           4 | 2011-02-18   | 2011-11-25    | 2012-03-13      |             280 |             389 | -0.2194 |               0.8376 |             0.8376 |                     0.1697 |                     0.2059 |         0.0060 |   25.1557 |   48.0000 |            -0.0624 |            -0.1861 |     0.9366 |                    -0.1861 |             -0.1337 |
|           5 | 2018-10-03   | 2018-12-24    | 2019-11-21      |              82 |             414 | -0.1963 |               0.8248 |             0.8248 |                     0.1444 |                     0.2087 |         0.0155 |   20.4242 |   30.1100 |            -0.0713 |            -0.1716 |     1.0081 |                    -0.1612 |              0.0427 |

## Aggregate Comparison

- Average gross exposure during drawdowns: `77.46%`
- Average gross exposure during normal periods: `91.02%`
- Average beta during drawdowns: `0.915`
- Average turnover during drawdowns: `0.0093`
- Average turnover during normal periods: `0.0070`
- Average top-10 loser contribution across top drawdowns: `-22.66%`

## Top Losing Positions

### Period 1
| ticker   |   start_weight |   return |   contribution |
|:---------|---------------:|---------:|---------------:|
| BA       |         0.0493 |  -0.6878 |        -0.0339 |
| SLB      |         0.0500 |  -0.6258 |        -0.0313 |
| COP      |         0.0501 |  -0.5857 |        -0.0293 |
| TSLA     |         0.0538 |  -0.5266 |        -0.0284 |
| CVX      |         0.0502 |  -0.5104 |        -0.0256 |
| XOM      |         0.0495 |  -0.4788 |        -0.0237 |
| WFC      |         0.0485 |  -0.4638 |        -0.0225 |
| GS       |         0.0495 |  -0.4278 |        -0.0212 |
| DIS      |         0.0502 |  -0.3931 |        -0.0197 |
| UNP      |         0.0494 |  -0.3749 |        -0.0185 |

### Period 2
| ticker   |   start_weight |   return |   contribution |
|:---------|---------------:|---------:|---------------:|
| NVDA     |         0.0501 |  -0.5853 |        -0.0293 |
| META     |         0.0476 |  -0.5968 |        -0.0284 |
| NFLX     |         0.0471 |  -0.6017 |        -0.0283 |
| BA       |         0.0530 |  -0.4332 |        -0.0230 |
| DIS      |         0.0495 |  -0.3943 |        -0.0195 |
| BAC      |         0.0518 |  -0.3598 |        -0.0186 |
| ECL      |         0.0489 |  -0.3753 |        -0.0183 |
| TSLA     |         0.0589 |  -0.3078 |        -0.0181 |
| GOOGL    |         0.0482 |  -0.3376 |        -0.0163 |
| AMZN     |         0.0469 |  -0.3255 |        -0.0153 |

### Period 3
| ticker   |   start_weight |   return |   contribution |
|:---------|---------------:|---------:|---------------:|
| NVDA     |         0.0516 |  -0.7626 |        -0.0394 |
| EQIX     |         0.0555 |  -0.6306 |        -0.0350 |
| GS       |         0.0495 |  -0.7041 |        -0.0348 |
| SLB      |         0.0509 |  -0.6220 |        -0.0316 |
| APD      |         0.0518 |  -0.6030 |        -0.0312 |
| AMZN     |         0.0519 |  -0.5855 |        -0.0304 |
| BAC      |         0.0461 |  -0.6413 |        -0.0296 |
| GOOGL    |         0.0518 |  -0.5573 |        -0.0288 |
| AAPL     |         0.0499 |  -0.5751 |        -0.0287 |
| LIN      |         0.0521 |  -0.5161 |        -0.0269 |

### Period 4
| ticker   |   start_weight |   return |   contribution |
|:---------|---------------:|---------:|---------------:|
| NFLX     |         0.0531 |  -0.7288 |        -0.0387 |
| BAC      |         0.0517 |  -0.6485 |        -0.0335 |
| GS       |         0.0501 |  -0.4678 |        -0.0234 |
| NVDA     |         0.0518 |  -0.4522 |        -0.0234 |
| JPM      |         0.0520 |  -0.3945 |        -0.0205 |
| SLB      |         0.0530 |  -0.2973 |        -0.0158 |
| WFC      |         0.0491 |  -0.2684 |        -0.0132 |
| BA       |         0.0510 |  -0.1245 |        -0.0063 |
| COP      |         0.0521 |  -0.1125 |        -0.0059 |
| GOOGL    |         0.0502 |  -0.1065 |        -0.0053 |

### Period 5
| ticker   |   start_weight |   return |   contribution |
|:---------|---------------:|---------:|---------------:|
| NVDA     |         0.0503 |  -0.5564 |        -0.0280 |
| SLB      |         0.0510 |  -0.4319 |        -0.0220 |
| NFLX     |         0.0500 |  -0.3797 |        -0.0190 |
| GS       |         0.0502 |  -0.3108 |        -0.0156 |
| AMZN     |         0.0481 |  -0.3118 |        -0.0150 |
| COP      |         0.0503 |  -0.2714 |        -0.0137 |
| BA       |         0.0521 |  -0.2467 |        -0.0129 |
| BAC      |         0.0504 |  -0.2381 |        -0.0120 |
| META     |         0.0497 |  -0.2362 |        -0.0117 |
| UPS      |         0.0495 |  -0.2305 |        -0.0114 |

## Cause Assessment

- A. Market crashes: YES
- B. Concentration: NO
- C. Factor failure: YES
- D. Turnover/whipsaw: NO

## Interpretation

- Drawdowns overlap with broad market stress: VIX spikes and SPY drawdowns are material in the worst periods.
- Sector concentration is not the primary explanation under the 30% diagnostic threshold.
- Factor quality deteriorates during the top drawdowns based on negative mean rebalance IC.
- Turnover does not appear to be the dominant drawdown source.
