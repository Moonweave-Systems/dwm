# Keelplane Native Team Operating Rules

These rules supplement the repository's existing Claude guidance.

## Boundary

- Claude Code executes; Keelplane plans/captures/verifies.
- Do not add API keys, provider routes, third-party MCP, or exact model pins.
- Agent/subagent output is self-report until observed or imported.
- Never claim a Keelplane pass/verified result without a policy report.
- Agents do not write authoritative manifest, ledger, or seal files.

## Team selection

- Localized task: main session, focused checks, fresh review when warranted.
- Medium task: `kp-explorer` -> `kp-implementer` ->
  `kp-test-verifier` + `kp-code-reviewer`.
- Sensitive task: conditionally add `kp-security-reviewer`.
- Distinct falsifier need: conditionally add `kp-adversarial-reviewer`.
- Use `kp-worktree-implementer` only for an independent ownership slice.
- True Agent Teams remain opt-in/experimental and are only for independent
  workstreams with stable interfaces and an integration owner.

Do not use teams for same-file edits or tightly sequential work.

## Lead duties

Restate acceptance claims/falsifiers, choose the smallest profile, pass explicit
context because subagents do not inherit all conversation history, assign one
writer per ownership region, freeze shared interfaces, define checks/gates, and
wait for required current-snapshot handoffs.

## Gates

Stop for action-bound approval before dependency/network/secret/database/
production/external messaging/destructive/history-rewrite/public API effects.
Never enable bypass permissions as a project default.

## Evidence

Each subagent finishes with fenced `KEELPLANE_RESULT` JSON matching the installed
agent-result schema. Record run/attempt/invocation, source snapshot, scope,
claims, artifact/command references, blockers, and origin. Never invent a
receipt, exit code, approval, hash, or evidence path.

Reviews are blind-first when possible and bind to the current diff/source
digest. Deterministic capture, not an evidence-curator agent, creates the
manifest, ledger, seal, and assurance label.

## Completion

Acceptance claims, observed checks, current review, action-bound gates, evidence
capture, and residual risk must be resolved. Agent agreement alone is not
completion.
