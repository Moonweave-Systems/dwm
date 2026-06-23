# Keelplane Ecosystem Positioning

## Position

Keelplane should become **policy-as-code and evidence evaluation for AI coding
runs**, not another orchestration, tracing, CI, or signing product.

## What Keelplane reuses

### Native harnesses

Codex and Claude Code provide the model loop, custom agents/subagents,
permissions, tools, sessions, and worktrees. Keelplane emits portable contracts
and imports or observes outputs.

### OpenTelemetry

OpenTelemetry GenAI and agent semantic conventions are appropriate for trace
correlation, agent IDs, operation names, and tool spans. Keelplane should accept
or export compatible trace context where available rather than inventing a
second tracing backend.

A trace is operational telemetry, not proof that a policy was satisfied.
Keelplane binds selected trace/span references to claim evidence.

### W3C Trace Context

`trace_id`, `span_id`, and parent relationships provide cross-system correlation.
They do not authenticate an agent or artifact by themselves.

### in-toto / DSSE / Sigstore / SLSA

These standards provide established statement, envelope, signer, and provenance
models. Keelplane A3 should define a predicate and policy over these formats,
not invent custom signatures.

### CI systems

CI remains the best place for independently observed tests, protected branches,
and release gates. Keelplane should consume CI receipts/attestations and return
a concise claim policy report.

## What Keelplane uniquely owns

1. A coding-workflow plan/run contract that names claims, falsifiers, ownership,
   gates, and required evidence.
2. An assurance-aware normalization layer across local native harnesses.
3. Claim-scoped policy evaluation that distinguishes pass, fail, and
   inconclusive.
4. Activation rules that decide when direct work, a pipeline, or a team is
   justified.
5. A human-readable explanation of why a claim is supported, refuted, stale, or
   unevaluated.

## Explicit non-competition

Keelplane should not try to replace:

- Codex/Claude/OpenCode orchestration;
- LangGraph or distributed workflow scheduling;
- LangSmith/Langfuse/Phoenix-style trace storage;
- GitHub Actions or other CI;
- Sigstore/in-toto signing;
- general-purpose policy engines for infrastructure.

It can integrate with those systems through narrow adapters.

## Product wedge

The first compelling workflow is:

```text
native coding-agent change
  -> deterministic local or runner capture
  -> current-snapshot test + independent review policy
  -> pass/fail/inconclusive with assurance
  -> merge or rework decision
```

This is understandable, testable, and useful before any dashboard or broad
multi-agent runtime exists.
