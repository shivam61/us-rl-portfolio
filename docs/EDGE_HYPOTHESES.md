# Edge Hypothesis Register (DRAFT, 2026-10-23)

Owner profile: software / adtech (DSP lead, now platform). Constraints: liquid securities only;
3-6 hrs/week, scaled up only if results justify. Companion to `LONG_TERM_PLAN.md`.
Not investment or legal advice.

## 0. Ground rules (apply to every hypothesis)

1. **Compliance first.** Use only public information and general industry judgment. Never use employer-internal data
   (spend, bid landscape, customer/partner confidential info) or anything learned under NDA. Check the employer's
   securities-trading policy, restricted list and pre-clearance rules before trading any ad-tech or partner/customer
   name. Keep a dated source list for every thesis. (Ask HR/legal; this is not legal advice.)
2. **Concentration.** Salary, bonus and equity already depend on ad-tech. Domain sleeve is capped (<= 5-10% of
   portfolio at first); index core already holds large ad-driven weights, so count that too.
3. **Pre-register.** Hypothesis, test, kill rule and sample size are written *before* looking at results.
4. **Multiple testing.** Count every hypothesis tested; expect most to fail.
5. **No LLM historical backtests of picks** (model knows outcomes). Allowed: deterministic rules on structured data;
   forward shadow; post-cutoff replays with date-bounded retrieval for debugging only.
6. **Baseline for everything:** broad index, and the same sleeve without the hypothesis.

## 1. Hypotheses

Plausibility is my prior, not a result. Liquid-only removes the neglected-small-cap edges, and large caps are the
most heavily analysed, so domain edge must show up as better *forecasts of mechanisms*, not as access to facts.

| ID | Claim | Who is on the other side | Plausibility | Time |
|---|---|---|---|---|
| H1 | Domain-informed forecasts of company metrics beat analyst consensus | Generalist sell-side analysts | Medium-low | ~2-3 h/wk |
| H2 | Read-through from advertisers/platforms predicts ad-platform surprises | Analysts covering each name in isolation | Medium-low | ~1 h/wk |
| H3 | Large-cap spin-offs / index deletions drift in a predictable way | Mandate-constrained forced sellers | Medium | ~0.5 h/wk |
| H4 | Policy/platform shifts (privacy, antitrust remedies, auction/format changes) are mispriced in 2nd-order names | Narrative-driven flows | Low-medium, tiny N | event-driven |
| H5 | Rules-based tax/cost/rebalancing beats naive handling of the same holdings | Typical investor behaviour | **High** | ~0.5 h/wk |
| H6 | Low-turnover quality+value+momentum blend on PIT large-cap universe beats index net of costs | Factor-ETF design and investor impatience | Medium | ~0.5 h/qtr |
| H7 | Agent-picked macro themes add value over core | Late-recognition flows | Low (shadow only) | ~1 h/qtr |

## 2. Pre-registered tests and kill rules

**H1 — Forecast vs consensus (lead hypothesis).**
- Universe: ~8-12 liquid names with ad-revenue exposure across layers (e.g. independent DSP/SSP, mobile app-performance
  platforms, large platforms' ad segments, measurement/verification, CTV). Final list fixed before first forecast.
- Method: each quarter, before earnings, the owner (assisted by agents for filings/transcripts) writes dated
  forecasts of resolvable metrics (revenue growth, gross margin, guidance direction, key KPI) with probabilities and a
  one-line mechanism. Agents draft counter-arguments; owner signs.
- Scoring: owner's error vs consensus error on the same metric (paired comparison); Brier score for directional calls.
- Sample: ~10 names x 4 quarters x 3 metrics ~ 120 forecasts/yr.
- **Kill:** after 8 quarters / >= 200 resolved forecasts, if owner is not better than consensus (paired test, 80% CI
  excludes zero on the favourable side) -> no capital allocated on H1 thesis; keep as learning only.
- **Scale:** capital rises stepwise (2% -> 5% -> 10%) only after 4 and 8 quarters of passing results.

**H2 — Cross-company read-through.**
- Build a panel: advertiser-side commentary (consumer apps, gaming, e-commerce, DTC: CAC, budgets, channel mix) and
  platform commentary vs next-quarter surprises of ad platforms.
- Test with deterministic rules on structured extraction; forward shadow only for LLM-extracted fields.
- **Kill:** if hit-rate vs surprise sign <= 55% after >= 60 events, or no improvement over H1 alone.

**H3 — Liquid spin-offs / index changes.**
- Event study on a point-in-time list of spin-offs and S&P index additions/deletions (market cap >= $2B), 2000-2025.
- Rule: fixed entry/exit offsets (e.g. +5d entry, 12m hold), costs 10-20 bps each way, excess vs index.
- Needs: event list + prices incl. delisted names (vendor data).
- **Kill:** cost-adjusted mean excess return CI includes zero on >= 40 events, or concentrated in 2-3 events.

**H4 — Policy/platform events.**
- Catalogue of ~10-15 past events; check whether pre-registered domain predictions (written *without* looking at prices)
  match basket returns. Treat as thesis generation, not a tradable signal, because N is too small.

**H5 — Process/tax/cost.**
- Counterfactual: after-tax, after-cost return of rules-based handling vs naive handling of identical holdings.
- Measured directly each year. No forecasting needed. **Kill:** none; adopt if net-positive.

**H6 — Factor blend.**
- PIT S&P 500 membership (historical constituent lists are reachable via GitHub); quarterly rebalance; turnover cap.
- Compare to index and to factor ETFs, net of costs, 2008-2025, with the survivorship fix from `REMEDIATION_PLAN.md` R1.
- **Kill:** net alpha t-stat < 1.0 or lower than the factor ETF it replaces.

**H7 — Macro themes.** Shadow only; scored on calibration; no capital for >= 3 years.

## 3. Weekly operating rhythm (target 3-6 h/week)

| Cadence | Task | Time |
|---|---|---|
| Weekly | Review agent digest: filings, 8-Ks, policy news, universe price/estimate changes | 60-90 min |
| Monthly | Review forecast log, update theses, check caps/rebalance rules | 90 min |
| Quarterly (earnings season, ~3 wks) | Write forecasts pre-earnings, resolve after, update scoreboard | 4-6 h/wk |
| Annual | Keep/scale/retire each hypothesis by its pre-registered rule | 3-4 h |

Average ~3-4 h/week. If H1 fails its gate, hours drop to ~1/week (process + core only).

## 4. Agent roles (human decides, code computes numbers)

Ingestion (transcripts, filings, policy items) -> Extraction (structured JSON with citations) -> Counter-argument/red-team
-> Scorer (code) -> Memory (forecast log, thesis registry, outcomes). Agents never size positions or trade.
Data candidates: Bigdata.com connector (documents, transcripts, tearsheets, point-in-time search). Open need:
a source for analyst consensus estimates (required for H1's baseline).

## 5. Open items

1. Country, tax residency, account type and broker (decides instruments, tax drag, order sizes).
2. Employer trading policy outcome (which names are off-limits or require pre-clearance).
3. Source for consensus estimates and spin-off/index-change event data.
4. Final universe list for H1 (fixed before first forecast).
