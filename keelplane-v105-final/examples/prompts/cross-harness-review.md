# Cross-harness blind-first review packet

Use this packet in the reviewer harness, not the producer session.

Run: `<run-id>` / `<attempt-id>`
Producer harness: `<codex-or-claude>`
Reviewer harness: `<other-harness>`
Scope/source digest: `<sha256>`
Objective: `<objective>`
Acceptance claims: `<claims>`
Falsifiers: `<falsifiers>`
Diff/source paths: `<paths>`
Observed command receipts: `<refs>`

Review the artifacts before reading any producer rationale. Try to reject the
change on correctness, regression, compatibility, data-integrity, missing-test,
and task-specific failure modes. Findings must be evidence-backed and bound to
the supplied digest. Mark stale/missing inputs inconclusive.

Return a review record conforming to `.keelplane/team/schemas/review.schema.json`. Set
`same_harness_as_producer` to false; set model separation to true/false only if
actually known, otherwise `unknown`. Do not edit files or approve gates.
