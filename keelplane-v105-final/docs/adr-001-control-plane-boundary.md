# ADR-001: Core Is a Policy/Evidence Plane; Runner Is Optional

Status: Proposed final

## Context

Keelplane documentation alternated between “does not execute agents” and a DWM
roadmap containing Codex execution, worktrees, fan-out, and repair loops.

## Decision

- Keelplane Core does not implement a model loop or task-command runtime.
- Keelplane Capture may observe/import facts.
- An optional Keelplane Runner may launch external native harnesses under a run
  contract and own process/evidence custody.
- Native harnesses continue to own reasoning, tools, session, auth, sandbox,
  and provider/model behavior.

## Consequences

This preserves existing runner work without mislabeling Keelplane as a model
runtime. Reports must distinguish Core policy, local capture, runner-observed,
and externally attested evidence.
