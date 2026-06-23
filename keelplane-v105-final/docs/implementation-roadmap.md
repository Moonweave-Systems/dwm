# Keelplane V105 Implementation Roadmap

## Governing rule

Stop adding one-script-per-concept meta layers. Complete this vertical loop:

```text
plan -> capture -> verify -> report
```

Use SemVer for package releases; V105 remains an internal milestone label.

## Milestone 0 — Freeze trust contract and stop false pass

Deliver product boundary, threat model, evidence protocol/schemas, decision +
assurance vocabulary, team profiles, evaluation spec.

Immediate code change: a required claim/adversarial item without a real
evaluator must be inconclusive, never pass.

Exit:

- known-good, contradicted, and missing-evaluator fixtures;
- no legacy test relies on path existence as claim verification.

## Milestone 1 — Harden generic discovery

Replace whole-file content loading with streaming metadata/digest collection.
Add path containment, symlink/special-file rejection, count/size/depth limits,
collision checks, and TOCTOU detection.

Exit:

- threat-model path/size fixtures pass;
- no binary hex expansion;
- content capture is allowlisted.

## Milestone 2 — Evidence manifest v1 + A1 capture

Implement deterministic local capture:

```bash
keelplane capture --plan ... --repo ... --run-id ... --out ...
```

Collect exact plan bytes, repository head/status/diffs/untracked index, imported
self-reports/reviews/receipts, ledger, manifest, local seal.

Exit:

- tamper/extra/missing file invalidates seal;
- producer cannot write observer-owned paths in reference runner setup;
- local report states A1 limitations.

## Milestone 3 — Policy engine and report

Implement claim selectors, required origin/assurance, stale snapshot detection,
action-bound gates, observable budgets, stable issue codes, and Markdown report.

Exit:

- decision + assurance authoritative;
- legacy verdict rendered only for compatibility;
- missing evidence is inconclusive;
- failed command/hash mismatch/gate violation is fail.

## Milestone 4 — Reference native packs

Ship Codex and Claude project-scoped agents, non-destructive installer,
profiles, prompts, schemas, capability fragments, and compatibility tests.

Do not auto-enable Claude Agent Teams or modify global config.

Exit:

- install/dry-run/conflict/uninstall receipt tests;
- agents parse under documented formats;
- no API key/model/provider/bypass settings.

## Milestone 5 — Native lowering

Implement `codex-native` and `claude-native` runbook compilation with capability
report and critical-loss failure.

Exit:

- deterministic outputs;
- exact/approximated/omitted/unsupported classification;
- required gate/verification cannot be silently dropped.

## Milestone 6 — Dogfood evaluation

Run the paired corpus from `evaluation-spec-v1.md`.

Exit:

- raw results and failures preserved;
- activation policy adjusted from evidence;
- unhelpful roles removed;
- no public superiority claim without adequate data.

## Milestone 7 — Optional A2 runner

Only after A1 is useful: process/workspace custody, timeouts, stdout/stderr,
append-only attempts, worktree boundaries, command receipts.

## Milestone 8 — Optional A3 attestation

Add in-toto/DSSE/Sigstore-compatible predicate/envelope and CI verification.
Do not invent custom signatures.

## Explicitly deferred

- dashboard/HUD expansion;
- more personas;
- automatic model router;
- more compiler targets;
- cloud service;
- public benchmark graph;
- more readiness/meta score layers.
