# Claude Compatibility Context

Claude should use [`AGENTS.md`](./AGENTS.md) as the primary repo entry point.
All repo rules, workflow rules, save rules, file lookup order, roadmap-first behavior, and git workflow requirements are governed by `AGENTS.md`.
Do not treat this file as an independent source of repo instructions.

<!-- CURRENT_STATE_START -->
## Current State — 2026-04-29T05:53:24+00:00
- Branch: `main`
- Working tree: 22 changed path(s)
- Dirty paths sample: `M artifacts/reports/phase_a4_blend_metrics.csv`, ` M artifacts/reports/phase_a4_correlation_matrix.csv`, ` M artifacts/reports/phase_a4_data_availability.csv`, ` M artifacts/reports/phase_a4_defensive_sleeve_results.md`, ` M artifacts/reports/phase_a4_overlap_report.csv`
- Latest commit: `22ae12f7 2026-04-29 test phase a4 defensive sleeve`
- Active jobs: none detected
- Deep handoff: `docs/agent_handoff.md`
- Refresh command: `bash scripts/refresh_session_context.sh`
<!-- CURRENT_STATE_END -->

## Rules

- Read `AGENTS.md` first and follow it as the canonical instruction file for this repo.
- Use `docs/agent_handoff.md` only when deep history is required, following the pattern defined by `AGENTS.md`.
- Refresh state with `bash scripts/refresh_session_context.sh`.
- Do not add Claude-specific repo rules here unless they are purely compatibility notes that point back to `AGENTS.md`.
