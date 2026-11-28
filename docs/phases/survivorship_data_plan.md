# Plan: survivorship-free price data for removed S&P 500 members

Status: PLAN (2026-11-28), not executed. Owner: decide D-1 to D-3 before step 1.

## 1. Why

The picks test (tracker sections 31 and 32) draws from current listings only. About 390 of the 889 stocks that were in the S&P 500 at some point in 2008 to April 2026 have no usable price history in the repo cache. Dropping them makes the picks look better than an investor could have done. The current 27% CAGR (holdout) is an upper bound. The result cannot be reported as an estimate of the strategy's real return until the removed companies are included.

## 2. What is needed

For each removed member (about 390 names, plus the reused tickers that need a mapping):

- Daily prices (open, high, low, close, adjusted close, volume) from the first date in the membership window until the removal date.
- Corporate actions (splits and dividends) so adjusted prices are consistent with our current cache.
- The final price or delisting return for names removed by acquisition, bankruptcy or merger. Without these, the test would silently treat a bankrupt stock as exiting at its last traded price.
- A company identifier (CIK, permno or similar) so a reused ticker is never mistaken for the original company.

## 3. Candidate sources

Only sources that include delisted US equities qualify. None of the free options tested so far do (yfinance, Stooq, INDmoney).

| Source | Delisted US equities | Access | Cost | Notes |
|---|---|---|---|---|
| Norgate Data | Yes | Download or Python | Paid subscription | Standard in research; has index membership history for S&P 500 |
| CRSP via WRDS | Yes | SQL via WRDS | Institutional licence; often via a university | Gold standard for delisting returns |
| EODHD | Claimed (docs say delisted symbols are supported) | REST API, key required | Paid plan | Verify coverage with a trial before buying |
| Tiingo | Claimed (verify) | REST API, key required | Paid plan | Verify the delisted coverage and history depth |
| Polygon | Verify | REST API, key required | Paid plan | Verify delisted coverage |

Verification is part of step 2. A claim in the docs is not evidence until the test in section 5 passes.

## 4. Decisions

- **D-1 Provider.** Recommend a trial of EODHD (cheapest with a stated delisted feature) and Norgate (strongest data). Pick one for the first pass.
- **D-2 Budget.** The amount of spend. A single year-long subscription is probably enough for the 2008 to 2026 pull.
- **D-3 Delisting returns.** Use the provider's delisting return if available, or model it (for example, a 100% loss for bankruptcies, the offer price for acquisitions). Recommend the provider's return, with the modelled version as a sensitivity.

## 5. Acceptance checks (must pass before any result is reported)

1. **Spot check, 10 names.** LEH, BSC, WM, CFC, GENZ, WB, ENE, JAVA, CCE and BRCM, plus one acquired name and one merged name. For each: first and last date match the membership window and the known removal date; the last price matches the known final trade; a split-adjusted price series has no unexplained jumps.
2. **Series stop at removal.** Every removed name's series ends on or near its removal date. A series that runs to 2026 fails. This is the check that the 93 names in tracker section 32 failed.
3. **Company identity.** Each series is matched to a CIK or permno and a company name. A reused ticker must be a different identifier from the original company's.
4. **Coverage.** At least 95% of members in each year from 2008 to 2026 have a price series. Report the names that do not.
5. **Consistency.** The adjusted-price returns for current names are unchanged against the current cache (within 1e-6). Adding the removed names must not change the existing series.
6. **Delisting returns.** Each name removed by bankruptcy, acquisition or merger has its delisting return applied, or is flagged as unmodelled.

## 6. Steps

1. **Trial (about 1 day).** Get a trial key or sample export from the chosen provider. Run the 10 spot names through check 1 and check 2.
2. **Decide.** If the trial passes, buy the subscription (D-2). If not, try the next provider.
3. **Pull (about 0.5 day).** Download the removed names from the membership file, using identifiers from the provider's symbol list rather than the ticker alone.
4. **Load (about 1 day).** Write one parquet per security, keyed by a stable identifier, under `data/raw_delisted/` (gitignored). Same column schema as `data/raw/`. Keep a manifest with provider, pull date, identifier and checks passed.
5. **Validate (about 1 day).** Run checks 1 to 6. Write a validation report to `docs/phases/survivorship_data_validation.md`.
6. **Rerun the picks test (about 1 day).** Extend the universe for the removed members (membership mask, no ADV), apply delisting returns, and rerun the holdout (2019 to April 2026) and the full period, with and without costs. Compare against the current-universe result (upper bound) and against SPY.
7. **Report.** Add a tracker section. Replace the upper-bound label with the survivorship-free estimate if the checks pass.

Total effort: about 4 to 5 working days, plus the provider's time to deliver the export.

## 6a. Pipeline changes

- The universe config needs a point-in-time member list, not a fixed 503-name list. The picks code should read the membership mask.
- Feature generation must cover every security that is a member on a given date, including removed ones.
- The price cache needs the removed names, with the delisting return recorded alongside.

The code work is about 1 to 2 days and can run in parallel with the data pull.

## 7. What this plan does not do

- It does not fix the earlier 93-name result. Those files stay quarantined (`data/raw_delisted_QUARANTINED/`) and must not be loaded.
- It does not change the B.5 picks or the production book.
- It does not add data to git. Data stays in gitignored folders.

## 8. Risks

- **Coverage may still fall short.** Some removed names may be missing from the provider too. Report the shortfall rather than fill it.
- **Ticker mapping errors.** A wrong match would silently corrupt the test. Check 3 exists to catch this.
- **Licence limits.** Check whether the provider allows the derived dataset to be stored and shared inside the repo. If not, keep it local and store only the code and checksums.
- **Cost overrun.** A trial that passes checks 1 and 2 can still fail check 4. Set a budget cap before buying.

## 9. Owner decisions needed

1. D-1 provider (or agree to trial EODHD first).
2. D-2 budget.
3. D-3 delisting-return method.
4. Whether the test should use the full period, or only 2008 onward (the period with the largest coverage gap).
