# Survivorship data ingest (free sources)

## Purpose and the ticker-reuse trap

The PIT membership mask lists former S&P 500 members. About 484 of them have no price file in
`data/raw` (`artifacts/reports/members_missing_price_data_2006plus.csv`). This runbook re-pulls
free-source prices for them, tiers each name, writes the usable ones to a separate cache, and
checks feature and coverage effects.

Trap: a ticker can be reused. A current series under the same symbol may belong to a different
company than the one that was a member years ago. Earlier, 93 series were wrongly called delisted
because they were current tickers. A series is usable for a member window only if the SEC CIK
that holds the ticker today was alive at member start, the vendor name matches a name the CIK
held in the window, and the series is continuous and price-scaled correctly. Current-ticker
matches alone are never enough.

## Commands (run from the repo root, in order)

Paths: `V` = verify2 outputs (raw Yahoo pulls, SEC JSON, `verdicts.csv`), currently in
`.claude/worktrees/agent-accc39d7234f356e8/runs_verify2/` (method in its `method.md`).

```bash
PY=.venv/bin/python
MEM=artifacts/reports/members_missing_price_data_2006plus.csv
V=.claude/worktrees/agent-accc39d7234f356e8/runs_verify2

# 1. Tier candidates (network: vendor name via yfinance, SEC companyfacts; cached in runs_ingest/net_cache)
$PY -I scripts/tier_free_price_candidates.py --verdicts $V/verdicts.csv --membership $MEM \
    --yf-dir $V/raw/yf --sec-dir $V/raw/sec --out-dir runs_ingest

# 2. Tests
$PY -m pytest -q tests/test_ingest_free_price_data.py

# 3. Ingest. --dest is the cache ROOT (the folder holding raw/); never pass data/raw.
$PY -I scripts/ingest_free_price_data.py --verdicts runs_ingest/tiers.csv --dest data --tier A --skip-existing
$PY -I scripts/ingest_free_price_data.py --verdicts runs_ingest/tiers.csv --dest data/raw_tierB --tier B --dry-run
$PY -I scripts/ingest_free_price_data.py --verdicts runs_ingest/tiers.csv --dest data/raw_tierB --tier B

# 4. Features on the fly (extended universe copy + symlinked merged cache, nothing written to data/raw)
$PY -I scripts/build_features_check.py

# 5. Coverage before/after by year
$PY -I scripts/coverage_before_after.py
```

Scripts `-I` reads of downloaded files: `ingest_free_price_data.py` and the tiering script read
only files under `V` and `data/`. Run ingest with `--dry-run` first.

Worktrees: `data/` is gitignored and lives in the main checkout. In a worktree, link it once:
`ln -s <main>/data data` (keep it out of commits; stage files by name).

## Tiers and checks

Tier A: verify2 VERIFIED (BF.B, VEEV, FDXF, FLEX, HONA). Already in `data/raw`; skip on rerun.
No price-scale anchor, so confidence is medium.

Tier B (usable, medium-low confidence), all of:
- (a) series starts within 30 days of member start, or an IPO/spin date falls inside the window.
- (b) continuous: no gap over 10 trading days in the window, no non-positive price, zero-volume
  days at most 5%.
- (c) no unexplained |daily return| over 40%. Explained only by a recorded split with a matching
  ratio. Crisis-period moves count as unexplained.
- (d) identity: CIK first filing at or before member start + 30 days; series not older than the
  CIK's first filing by more than a year (EDGAR phase-in before 1998 is ignored); CIK still
  filing near member end; vendor name matches an SEC name valid in the window (current or
  former name).
- (e) scale anchor: SEC `dei:EntityPublicFloat` / shares outstanding inside the window, median
  close within 45 days of that date within 0.5x to 2.0x of the implied price.

Anything else is REJECT, with reasons in `runs_ingest/tiers.csv`. Evidence per name is in
`runs_ingest/evidence/<TICKER>.json`.

## Where files go

- `data/raw/<T>.parquet`: Tier A (cache schema: date index, open/high/low/close/volume int64/adj_close).
- `data/raw_tierB/raw/<T>.parquet` and `data/raw_tierB/_manifest.json`: Tier B. Read with
  `DataIngestion(cache_dir="data/raw_tierB")`.
- Manifest row per file: ticker, tier, source, pull date, sha256, first, last, rows,
  checks passed, evidence ref, CIK.
- `runs_ingest/` (gitignored): tiers.csv, evidence/, net_cache/, feature_check/, coverage CSV.

## Extending the universe or membership mask

- Mask: the mask comes from `scripts/build_sp500_pit_membership.py` (fja05680 components CSV,
  not in the repo). The mask already lists every member name, so no rebuild is needed to price
  new names. Coverage uses the same mask.
- Universe: `build_features_check.py` writes `runs_ingest/feature_check/universe_extended.yaml`
  (Tier B names, sector `Unknown`). To use it in a pipeline, point `--universe` at that file
  and set `cache_dir` to a merged cache (symlinks to `data/raw` plus `data/raw_tierB/raw`).
- After a rerun, delete `runs_ingest/feature_check/cache_*` and rebuild it, since it holds symlinks.

## Validation checklist

- [ ] `pytest -q tests/test_ingest_free_price_data.py` passes.
- [ ] Dry run reports no FAILED; the real run exits 0.
- [ ] Each Tier B manifest row has sha256 matching the file, and first/last match the parquet.
- [ ] No file in `data/raw` was created or changed (`ls data/raw | wc -l` stays at the same count).
- [ ] `feature_check.json`: feature columns equal; only `liquidity_rank` changes for baseline
      names (a cross-sectional percentile); every Tier B name has features after warm-up.
- [ ] `coverage_before_after.csv` covers 2008-2026; no backtest run.

## Known dead ends

- yfinance returns no rows for most delisted names (281 of 484 in verify2).
- Stooq is blocked by a bot check.
- INDmoney, EODHD (demo key only), Quandl WIKI mirrors need keys; not used.
- Successor-ticker fetching was not run; no rename evidence exists in free sources.
- SEC submissions carry only current tickers, so ticker history is not available. Identity
  rests on CIK plus name.
- The price-scale anchor needs XBRL facts, which start around 2009. Members who left before
  2009 cannot pass (e).

## Still missing

About 360 names remain REJECT, most of them truly delisted (no free series). Closing the gap
needs a paid survivorship-free source such as Norgate or Sharadar. Tier B itself is capped at
medium-low confidence: a restated series such as ITT (spin adjustment) can pass the band, and
renamed-after-window names are conservatively rejected.
