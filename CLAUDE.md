# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.
All repo rules, workflow rules, save rules, file lookup order, roadmap-first behavior, and git workflow requirements are governed by `AGENTS.md`.
Do not treat this file as an independent source of repo instructions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-29T05:18:10+00:00
- Branch: `main`
- Working tree: 12 changed path(s)
- Dirty paths sample: `M docs/ROADMAP.md`, ` M docs/agent_handoff.md`, ` M docs/phases/phase_a.md`, `?? artifacts/reports/phase_a4_benchmarks.csv`, `?? artifacts/reports/phase_a4_blend_metrics.csv`
- Latest commit: `47ff631f 2026-04-29 test phase a3 multi sleeve alpha`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Read `AGENTS.md` first and follow it as the canonical instruction file for this repo.
- Use `docs/agent_handoff.md` only when deep history is required, following the pattern defined by `AGENTS.md`.
- Refresh state with `bash scripts/refresh_session_context.sh`.
- Do not add Claude-specific repo rules here unless they are purely compatibility notes that point back to `AGENTS.md`.
