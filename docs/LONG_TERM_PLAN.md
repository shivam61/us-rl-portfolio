# Long-Term Plan — Core + Risk Sleeve + Agent-Researched Themes

Status: DRAFT for discussion (2026-10-23). Supersedes the RL-centred direction; see `REMEDIATION_PLAN.md`
for why. Not investment advice. All assumptions below are placeholders until confirmed (see Open Questions).

## 1. Objective and constraints (assumed)

- Goal: maximise long-run *after-cost, after-tax* compounding, subject to a drawdown the owner can sit through.
- Horizon >= 10 years. Long-only, no leverage, no shorting. Review cadence quarterly (annual for core).
- Cadence is set by the signal's half-life (themes: quarters to years), **not** loosened or tightened based on
  results — choosing cadence by outcomes is tuning.
- Written Investment Policy Statement (IPS) is frozen before any money moves: allocation bands, max satellite size,
  max single-name weight, max shift per quarter, kill/scale rules.

## 2. Wealth-creation levers (ranked by size of effect and by how much you control)

Illustration: $50K start, $1K/month, 20 years, 7% baseline -> ~$714K.

| # | Lever | Effect on that example | Controllable? | Edge needed? |
|---|---|---|---|---|
| 1 | Savings rate / contributions | +$500/month = +$260K | Fully | No |
| 2 | Asset allocation (equity share vs horizon) | Dominant driver of return *and* risk | Fully | No |
| 3 | Costs and taxes (fees, spreads, turnover, account type, harvesting) | 1pp annual drag = -$92K | Mostly | No |
| 4 | Behaviour (stay invested, rebalance by rule, no panic selling) | Avoids the largest losses | Via rules | No |
| 5 | Volatility drag / drawdown control (geometric return ~ arithmetic - sigma^2/2) | 8% arithmetic: 6.0% geo at 20% vol vs 7.3% at 12% vol | Via sleeve design | No |
| 6 | Diversified risk premia (value, quality, small-cap value, international) | Modest, uneven | Yes | Weak |
| 7 | Thematic / stock selection by agents | +1pp annual = +$108K, but could be negative | Partly | **Strong — unproven** |

Design implication: levers 1–5 need no forecasting skill and are worth more than lever 7. Build them first.
Lever 7 gets a capped slice and must earn more capital through evidence.

## 3. Portfolio architecture

| Sleeve | Target (band) | Content | Rebalance |
|---|---|---|---|
| Core | 60–75% | Broad low-cost equity index (US + international per owner), optional bonds per horizon | Annual / bands |
| Risk sleeve | 10–20% | Rule-based trend / risk-managed exposure (ETFs: duration, gold, cash, equity trend filter) | Monthly signal, quarterly trade |
| Factor tilt | 5–10% | Value/quality/momentum/small-cap-value ETFs or simple rule-based screen on a PIT universe | Quarterly |
| Theme sleeve | 5–15% (hard cap) | Agent-researched themes, implemented via ETFs or 5–15-name baskets | Quarterly, max shift per quarter |

Hard rules: theme sleeve cap; max shift +/-2% of total portfolio per quarter; max 5% single stock; no theme > 40%
of the sleeve; new money goes to the most underweight sleeve first (cheap, tax-friendly rebalancing).

## 4. Quarterly agent workflow (theme sleeve)

Can agents "identify the next theme and move the portfolio"? They can do the research steps well; they cannot be
trusted to *time* rotations. Themes are public by the time they are recognised, so the pipeline must test
expectations vs valuation, not just story quality.

1. **Regime agent** — summarises rates, growth, inflation, liquidity, policy; outputs structured regime notes with sources.
2. **Theme-discovery agents (2–3, different prompts/data)** — propose themes with a 2–5-year thesis, key drivers,
   beneficiaries (first and second order), and 3 falsifiable "I'm wrong if" conditions with dates.
3. **Dossier builder** — for each theme, *code* (not LLM) computes: price trend, valuation vs own history,
   estimate revisions, ETF flows/crowding, concentration, correlation to core.
4. **Red-team agent** — argues the bear case and finds what is already priced in.
5. **Committee aggregator** — fixed rubric (thesis strength, evidence quality, valuation/crowding penalty,
   diversification vs existing book). Outputs a proposed delta inside the IPS bounds.
6. **Human approval** — owner signs; nothing executes automatically.
7. **Execution + logging** — orders, then memory write.

Agents may not: size positions outside the bounds, override caps, trade on their own, or change the rubric.

## 5. Memory (history of analysed themes and stocks)

Tables (SQLite/parquet, append-only):
- `theme_registry`: theme, first_seen, thesis, drivers, kill_criteria, status (watch/active/retired), review_due.
- `stock_registry`: ticker, last_analysed, rubric scores, thesis hash, source hashes, price_at_analysis, re-analyse trigger
  (earnings, 90 days, kill-criterion hit).
- `forecasts`: every claim as a dated, resolvable statement with a probability.
- `decisions`: proposed vs approved vs executed, sizes, reasons.
- `outcomes`: filled automatically at 1, 4, 8, 12 quarters.

## 6. How we know it works (evaluation designed first)

Returns need years, so add faster feedback:
- **Calibration (resolves in 1–4 quarters):** agents must state probabilities for observable fundamentals
  (revenue growth, estimate revisions, margin, guidance). Score with Brier score vs a naive baseline.
  Agents that cannot beat the base rate on fundamentals should not be trusted on themes.
- **Return scorecard (3- and 5-year):** each theme sleeve vs (a) core index, (b) random baskets drawn from the same
  universe/size, (c) naive "last year's best theme" momentum, (d) the same sleeve *without* agent review.
- **Sample size reality:** detecting 3% alpha at 10% tracking error takes decades; so the decision rule is asymmetric —
  *cut* quickly on clear failure (e.g. calibration worse than baseline for 4 quarters, or sleeve under core by > X with
  worse risk), *scale* slowly (only after >= 3 years, >= N independent themes, lower CI bound > 0).
- **Look-ahead:** LLMs know history, so historical backtests of agent picks are contaminated. Allowed uses of replay:
  only windows after the model's training cutoff, with date-bounded document retrieval (as-of search), to debug
  process, not to claim performance. Proof comes from forward shadow + live results.

## 7. Phases and gates

| Phase | Duration | Deliverable | Gate to proceed |
|---|---|---|---|
| P0 Decide | 1–2 wks | IPS, account/tax setup, assumptions confirmed | Owner sign-off |
| P1 Foundation | 1–2 mo | Core + risk sleeve live (ETFs), tracking vs benchmark, cost/tax report | Runs a full quarter without manual fixes |
| P2 Data + memory | 1–2 mo | PIT-safe data for factor screen (fix survivorship), memory tables, scorecard code | Reproducible; unit tests on PIT, turnover, scoring |
| P3 Agents in shadow | 2 quarters | Full quarterly workflow, paper decisions only, forecasts logged | Calibration >= baseline; no rule violations |
| P4 Small live | 4+ quarters | Theme sleeve at <= 5%, then up to cap if gates hold | Meets scale rules in section 6 |
| P5 Annual review | yearly | Keep / scale / retire each sleeve by pre-registered rules | Written decision |

## 8. What happens to the current repo

- Retire: RL controller, G.4 auto-switching, H-gate paper trading as currently defined.
- Keep and reuse: leakage-safe feature code, audit trail pattern, paper-trading ops/journal (as the logging layer),
  trend-sleeve logic (as risk-sleeve prototype once validated vs simple trend rules).
- Fix before reuse: survivorship-free universe (R1), turnover units, hard-coded NAV in journal generation.

## 9. Main risks

Narrative bias and recency in agent output; crowded themes bought late; correlated agents (same model) giving false
consensus; hallucinated figures (mitigate: numbers computed by code, cited sources); tax drag from turnover;
concentration; operational mistakes (human approval + order checks); regime change making a sleeve irrelevant.

## 10. Open questions (decide before P0)

1. Country/tax regime and account type (taxable vs tax-advantaged); brokerage and instruments available.
2. Monthly contribution amount and total investable capital; withdrawal horizon.
3. Max drawdown the owner can tolerate without selling.
4. US-only, or include India/other markets (data and cost implications)?
5. Appetite for single stocks vs ETF-only implementation of themes.
