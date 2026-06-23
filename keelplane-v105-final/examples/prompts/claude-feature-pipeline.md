# Claude Code feature-pipeline prompt

Follow the Keelplane `feature-pipeline` profile.

Objective: `<objective>`
Run/attempt: `<run-id>` / `<attempt-id>`
Base snapshot: `<snapshot>`
Acceptance claims/falsifiers: `<list>`

1. Delegate read-only mapping to `kp-explorer`.
2. Choose the smallest route. For a nontrivial single ownership region, assign
   `kp-implementer` exact write paths and forbidden effects.
3. Freeze the post-implementation diff/source digest.
4. Delegate `kp-test-verifier` and `kp-code-reviewer` against the same digest.
5. Conditionally use `kp-security-reviewer` or `kp-adversarial-reviewer` only
   for distinct failure modes.
6. Prefer blind-first review: do not provide implementation rationale before
   the reviewer's initial findings.
7. Do not use Agent Teams unless there are two independent workstreams with a
   frozen interface and integration owner.
8. Agent outputs are self-reports; deterministic Keelplane capture owns the
   manifest, ledger, seal, and assurance.
9. End with claims, observed/imported evidence references, unresolved gates,
   residual risks, and the exact current snapshot digest.
