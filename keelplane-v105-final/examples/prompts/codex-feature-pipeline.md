# Codex feature-pipeline prompt

Use the Keelplane `feature-pipeline` profile for this task.

Objective: `<objective>`
Run ID: `<run-id>`
Attempt ID: `<attempt-id>`
Base source snapshot SHA-256: `<snapshot>`

Acceptance claims and falsifiers:

1. `<claim>`
   - Falsifier: `<counterexample/test>`

Rules:

1. Explicitly spawn `kp_explorer` first. Ask it to map the real code path,
   tests, risk triggers, and one writer ownership region.
2. The lead reviews the handoff and either downgrades to direct work or assigns
   one `kp_implementer` with exact write paths.
3. After implementation, freeze and record the current diff/source digest.
4. Run `kp_test_verifier` and `kp_reviewer` against that same digest. They may
   run in parallel.
5. Add `kp_security_reviewer` only for a security trigger. Add
   `kp_adversarial_reviewer` only for a distinct concurrency/stale-state/high-
   consequence falsifier.
6. No child agent may approve a risk gate or write authoritative evidence
   manifest, ledger, or seal files.
7. Treat every KEELPLANE_RESULT as self-report. Do not invent command receipts.
8. Stop if ownership, gate, or snapshot changes; issue a new assignment.
9. At completion, summarize current claims, checks, reviews, blockers, residual
   risk, and paths ready for deterministic Keelplane capture.
