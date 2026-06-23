# ADR-003: Agents Cannot Seal Their Own Evidence

Status: Proposed final

## Context

The first pack included an Evidence Curator agent that could write under the
evidence root. That collapses producer and auditor custody.

## Decision

- Agent results remain self-reported staging artifacts.
- Deterministic capture or a bounded runner writes observed records, ledger,
  manifest, and seal.
- Final reports separate decision from assurance.
- A local seal proves only post-capture byte integrity under local assumptions.

## Consequences

The evidence-curator agent is removed. The pack gains deterministic capture and
seal-verification tooling instead.
