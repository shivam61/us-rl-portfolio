# Agent Handoff — Deep Context

Last updated: 2026-04-28T09:12:58+00:00

This is the deep-history document for all agents. Keep `AGENTS.md` short and put long-form notes here.

## What Belongs Here

- Material experiment outcomes
- Decisions that change future work
- Active risks, caveats, and follow-up tasks
- Useful commands that the next agent is likely to need

## Current Baseline Convention

- **sp100 (44 tickers)** = research baseline / dev universe / fast iteration track
- **sp500 (503 tickers)** = validation baseline / system benchmark / locked comparison track
- Historical notes may say "baseline" loosely; verify the universe before comparing metrics

## Current Recommended Workflow

1. Read `AGENTS.md`.
2. Read `docs/ROADMAP.md`.
3. Read this file only if prior experiment history or handoff detail is needed.

## Session Notes

### 2026-04-28

- Shared agent-state migration planned: replace Claude-only context persistence with repo-level `AGENTS.md` plus a generic refresh script.
- Existing Claude implementation currently updates `CLAUDE.md` and `docs/session_handoff.md` through `scripts/save_context.sh` and `.claude/settings.json`.
- Target design keeps the auto-loaded context small and moves deep history into this file.
