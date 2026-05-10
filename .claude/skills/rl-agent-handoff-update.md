---
name: rl-agent-handoff-update
description: Update project handoff and context after RL work — record experiments, decisions, artifacts, and next steps for future sessions.
---

# RL Agent Handoff Update

## When to use this skill

- After completing a phase or major experiment run
- After promoting or rejecting an RL checkpoint
- After production infrastructure steps complete
- Before handing off to another agent or session

## Required context to read first

1. `AGENTS.md` — current state block (will be auto-updated by refresh script)
2. `docs/agent_handoff.md` — deep history (manually update session notes)
3. `docs/ROADMAP.md` — phase status (manually update if phase complete)
4. Completed experiment reports in `artifacts/reports/`

## Workflow

### 1. Identify Material Work

What was completed:
- RL training or evaluation run
- Gate validation and promotion decision
- Production infrastructure step (e.g., feature parity, signal pipeline, drift monitoring)
- Bug fix or diagnostic run
- Baseline change or phase transition

### 2. Update `docs/agent_handoff.md`

Add session note with date:

```markdown
### YYYY-MM-DD — [Phase X.Y] [SHORT_TITLE] — [PROMOTE/REJECT/COMPLETE]

**Context:** [Why this work was done — 1-2 sentences]

**Artifacts:**
- Model: `artifacts/models/rl_*_best.zip` (size)
- Reports: `artifacts/reports/phase_*_evaluation.md`, `*_comparison.csv`

**Results:**
- Gate scorecard: X/8 pass (list failing gates if any)
- Key metrics: Sharpe X.XXX, MaxDD -XX.XX%, CAGR XX.XX%
- Comparison: vs baseline / vs random / vs rule-based

**Decision:**
- [PROMOTE / CONDITIONAL / REJECT]: [rationale in 1 sentence]
- Root cause (if REJECT): [specific failure mode]

**Commands run:**
```bash
.venv/bin/python scripts/train_rl*.py [flags]
.venv/bin/python scripts/run_rl_backtest*.py [flags]
```

**Next steps:**
- [Specific next experiment or phase transition]
```

**Keep notes concise:** <100 lines per session. Reference file paths, not raw data.

### 3. Update `docs/ROADMAP.md` (if phase complete)

If phase status changed:

```markdown
# Before
| **X** | [Phase Name] | 🔄 **ACTIVE** | ... |

# After
| **X** | [Phase Name] | ✅ **COMPLETE — [OUTCOME]** (YYYY-MM-DD) | ... |
```

Update baseline metrics table if new production model promoted.

### 4. Run Refresh Script

Auto-updates both `AGENTS.md` and `CLAUDE.md`:

```bash
bash scripts/refresh_session_context.sh
```

Verify:
- Current State timestamp updated
- Latest commit SHA correct
- Working tree status accurate

## Session Note Template

```markdown
### YYYY-MM-DD — Phase [X.Y] [TITLE] — [OUTCOME]

**Context:** [Why — e.g., "Fixed over-defensiveness by recalibrating λ_dd"]

**Artifacts:**
- Model: `artifacts/models/rl_*_best.zip`
- Report: `artifacts/reports/phase_*_evaluation.md`
- Data: `*_comparison.csv`, `*_regime_breakdown.csv`

**Training:** (if applicable)
- Window: train / val dates
- Best val metric: X.XXX at episode N
- Early stopping: episode M
- Key hyperparams: [list if changed from prior]

**Holdout Results:**

| Policy | Sharpe | MaxDD | CAGR |
|--------|--------|-------|------|
| Baseline | X.XXX | -XX.XX% | XX.XX% |
| Trained RL | X.XXX | -XX.XX% | XX.XX% |

**Gate Scorecard:** X/8 PASS

[List gates with ✅/❌]

**Decision:** [PROMOTE / CONDITIONAL / REJECT] — [rationale]

**Trade-offs:** [e.g., "CAGR sacrifice 2.9pp for 8pp MaxDD improvement"]

**Commands run:**
```bash
.venv/bin/python scripts/... [full command with flags]
```

**Production artifacts:** (if promoted)
- Checkpoint: `artifacts/production/*_promoted.zip`
- Manifest: `artifacts/production/*_manifest.json`

**Next steps:**
- [Actionable next task]
```

## Checks

- [ ] Session note includes date in `### YYYY-MM-DD` format
- [ ] Context explains why (1-2 sentences)
- [ ] Artifacts listed with full paths
- [ ] Gate scorecard complete (if applicable)
- [ ] Decision includes rationale (PROMOTE/CONDITIONAL/REJECT + why)
- [ ] If REJECT, root cause identified
- [ ] Commands include full flags (reproducible)
- [ ] Next steps are actionable
- [ ] Refresh script run
- [ ] No sensitive data logged
- [ ] Notes concise (<100 lines)

## Guardrails

- Do NOT turn `agent_handoff.md` into long notebook — keep notes concise
- Do NOT skip recording REJECT decisions (failures are valuable context)
- Do NOT record in-progress work (only completed experiments)
- Do NOT duplicate ROADMAP content (handoff is session history, ROADMAP is phase status)
- Do NOT modify `AGENTS.md` or `CLAUDE.md` manually — use refresh script
- Do NOT commit `artifacts/` directory (git-ignored)
- Do NOT record raw data or full CSVs (reference file paths only)
- Do NOT skip refresh script after material work
