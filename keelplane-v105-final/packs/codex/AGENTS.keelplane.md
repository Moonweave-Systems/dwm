# Keelplane Native Team Operating Rules

These rules supplement repository-specific instructions; repository and user
requirements remain authoritative.

## Boundary

- Codex executes; Keelplane plans/captures/verifies.
- Do not add API keys, provider routing, third-party MCP, or exact model pins.
- Agent output is a claim, not observed evidence.
- Never claim `pass`/`verified` without a Keelplane policy report.
- Agents do not write authoritative manifest, ledger, or seal files.

## Smallest effective shape

- Localized task: direct work + focused check + fresh review when warranted.
- Medium task: `kp_explorer` -> one `kp_implementer` ->
  `kp_test_verifier` + `kp_reviewer`.
- Security trigger: add `kp_security_reviewer`.
- Distinct falsifier need: add `kp_adversarial_reviewer`.
- Parallel writers only for stable interfaces, disjoint ownership, worktrees,
  and an integration owner.
- Same-file/tightly sequential work is never a parallel-writer team.

Codex subagents must be requested explicitly. Child agents do not spawn more
agents unless the parent contract explicitly allows it.

## Ownership

Before parallel implementation, define writer paths/module boundaries, shared
interfaces, one integration owner, forbidden paths, source snapshot, and fan-in
checks. Worktree isolation does not prevent semantic conflicts.

## Risk gates

Require action-bound user approval for dependencies, network, secrets, database,
production/external messaging, destructive operations, history rewrite, or
public API breakage. Approval binds plan, attempt, action digest, scope, and
expiry; a generic marker is insufficient.

## Handoff and evidence

Finish each custom agent invocation with fenced `KEELPLANE_RESULT` JSON matching
`.keelplane/team/schemas/agent-result.schema.json` when installed. Record run,
attempt, invocation, source snapshot, scope, claims, references, and blockers.
Set origin to `self-reported` unless a trusted collector/runner assigns another
origin. Never invent command receipts, exit codes, approvals, hashes, or paths.

Tests/reviews bind to the current source or diff digest. Stale results cannot
complete the task. Deterministic Keelplane capture creates authoritative
manifest/ledger/seal.

## Completion

Completion requires acceptance claims evaluated under policy, required observed
receipts, current-snapshot review, resolved gates, valid evidence capture, and
explicit residual risk. Agent consensus is not completion.
