# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.
All repo rules, workflow rules, save rules, file lookup order, roadmap-first behavior, and git workflow requirements are governed by `AGENTS.md`.
Do not treat this file as an independent source of repo instructions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-05-02T10:00:31+00:00
- Branch: `main`
- Working tree: 5 changed path(s)
- Dirty paths sample: `?? artifacts/reports/phase_c1_run.log`, `?? artifacts/reports/phase_c1_run2.log`, `?? artifacts/reports/phase_c2_run.log`, `?? artifacts/reports/phase_d5_training_log_run.log`, `?? artifacts/reports/phase_d6_run.log`
- Latest commit: `473a1766 2026-05-02 close Phase D (REJECT) and open Phase E — RL Regime Controller v2`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Read `AGENTS.md` first and follow it as the canonical instruction file for this repo.
- Use `docs/agent_handoff.md` only when deep history is required, following the pattern defined by `AGENTS.md`.
- Refresh state with `bash scripts/refresh_session_context.sh`.
- Do not add Claude-specific repo rules here unless they are purely compatibility notes that point back to `AGENTS.md`.
