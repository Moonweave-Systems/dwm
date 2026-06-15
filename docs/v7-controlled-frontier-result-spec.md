# V7 Controlled Frontier Result Spec

Status: first slice implemented
Date: 2026-06-15

## Purpose

V7 executes one allowlisted fixture worker from a trusted V6.5 frontier dispatch
and records the result under owned `out/v7/`.

This slice proves that the loop can continue past V6.5 without opening
arbitrary execution:

```text
V6.5 release_decision dispatch
-> V7 controlled fixture result
-> future V7.5 review
-> future V6-style ingestion
```

## Workflow Design

Source plan: `docs/v7-controlled-frontier-result.workflow.plan.json`.

Patterns:

- Sequential
- Resume And Cache
- Adversarial Verify

Phases:

1. Dispatch validation: require an owned V6.5 dispatch with clean resume.
2. Fixture execution: run only the allowlisted `release-decision` fixture inside
   `out/v7/<run_id>/work/`.
3. Result recording: write result, output hashes, status, and resume docs.

## Command Contract

```bash
python scripts/run_frontier_result.py --dispatch out/v6.5/<run_id> --out out/v7/<run_id> --fixture release-decision
python scripts/run_frontier_result.py --resume out/v7/<run_id>
python scripts/run_frontier_result.py --self-test
```

## Accepted Inputs

V7 accepts only:

- an owned V6.5 dispatch directory,
- `status.json` with `status: prepared`,
- clean V6.5 resume,
- dispatch phase `release_decision`,
- expected output `release-decision.md`,
- fixture id `release-decision`.

V7 rejects:

- stale or malformed dispatch artifacts,
- unsupported fixture ids,
- dispatches not prepared by `dispatch_frontier.py`,
- produced output paths outside owned `work/`,
- symlinked output directories or leaf files.

## Output Model

```text
out/v7/<run_id>/
├── .run_frontier_result-owned.json
├── result.json
├── stdout.txt
├── stderr.txt
├── hashes.json
├── status.json
├── resume.md
└── work/
    └── release-decision.md
```

## First Slice Rules

For the dogfood result, V7 should produce `release-decision.md` for
`release_decision`.

Executed status requires:

1. V6.5 status is `prepared`.
2. V6.5 resume is `resumable`.
3. Dispatch phase is `release_decision`.
4. Fixture expected output is `release-decision.md`.
5. The output exists under owned `work/` and its hash matches `hashes.json`.
6. Resume recomputes dispatch, packet, prompt, result, stdout, stderr, and
   produced output hashes.

## Non-Goals

- Do not execute arbitrary commands.
- Do not call Codex CLI, OMX, subagents, network APIs, or paid APIs.
- Do not write result files into the repository root.
- Do not review or ingest `release-decision.md` yet.

## Release Criteria

The slice is `keep` only if:

- `python scripts/run_frontier_result.py --self-test` passes,
- dogfood run over `out/v6.5/v32-semantic-dogfood` returns `executed`,
- clean resume returns `resume_state: resumable`,
- tampered output invalidates resume,
- no arbitrary backend execution is introduced.
