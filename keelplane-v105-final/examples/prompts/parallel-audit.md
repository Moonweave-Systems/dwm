# Parallel read-only audit prompt

Run a read-only Keelplane `parallel-audit`.

1. Explorer maps surfaces and exact scope.
2. Run correctness/compatibility, security, and adversarial reviewers in
   parallel only after the scope digest is frozen.
3. Each reviewer owns a distinct failure mode and returns findings with evidence.
4. Synthesis deduplicates but does not erase disagreements or unknowns.
5. Do not remediate in this run. Any write becomes a new plan with approval.
6. Capture all review records and the frozen scope digest deterministically.
