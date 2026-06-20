# V102 Live Proof 1

Durable tracked record for the first bounded live Codex execution proof. The
generated `out/` bundle remains verification evidence and is not committed.

## Run Command

```bash
python scripts/dwm_live_proof.py run --seed fixtures/live-proof/seed --plan fixtures/live-proof/live-proof-1.workflow.plan.json --out out/live-proofs/live-proof-1 --i-approve-live-codex
```

## Bundle Fields

- `decision`: `live-proof-pass`
- `verification`: `before: red`, `after: green`, `returncode: 0`, `passed: true`
- `review`: `decision: approved`
- `review.checks`: `verification_passed: true`,
  `test_files_unchanged: true`, `source_changed: true`
- `files_touched`: `["live_math.py"]`
- `repo_tracked_diff_unchanged`: `true`
- `dogfood_comparison`: `mode: dwm-controlled`, `status: run`
- `dogfood_comparison.metrics`: `elapsed_seconds: 68.423`,
  `interruptions: 0`, `verification_passed: true`
- `elapsed_seconds`: `68.423`
- `live-proof.json` sha256:
  `4babf8d24c80cfc65dd55a96892854db9fb8471e72ae80e5cc83765602c8c12f`

## Safety Boundary

This record stores one bounded V102 run: live execution n=1 passed; no
direct-agent superiority claim yet. It makes no unrestricted autonomy or
benchmark claim.
