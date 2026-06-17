# V54 Dogfood Attempts Spec

Status: implemented first measured dogfood comparison ledger in
`scripts/dwm_dogfood_attempts.py`.

## Research and Prior Art

V47 created dogfood comparison slots, but every slot intentionally stayed
`not-run`. V54 starts the real measurement path without pretending that DWM has
already won anything.

The key product move is small but important: DWM can now record measured local
attempt receipts for `direct-codex` and `dwm-controlled` modes, bind them to
evidence files, and block unsupported public claims.

## Product Position and Non-Goals

V54 is a receipt recorder and comparison ledger. It does not execute Codex,
Claude, shell, or any live adapter.

Non-goals:

- do not execute attempts automatically,
- do not publish README benchmark graphs,
- do not claim direct-agent superiority,
- do not accept missing evidence files,
- do not accept external benchmark or model-superiority claims.

## Workflow Architecture

The command is:

```bash
python scripts/dwm_dogfood_attempts.py record --corpus out/dogfood-corpus/<corpus_id> --attempts attempts.json --out out/dogfood-attempts/<attempt_id>
```

It reads:

- `dogfood-corpus.json`,
- a measured attempt receipt file.

Each receipt records:

- `task_id`,
- `mode` as `direct-codex` or `dwm-controlled`,
- repo-relative `evidence_path`,
- `elapsed_seconds`,
- `interruptions`,
- `verification_passed`,
- `command_count`.

It writes:

- `dogfood-attempts.json`,
- `comparison-ledger.json`,
- `status.json`,
- `README.md`.

## Safety and Verification Gates

The gate blocks:

- `ERR_DOGFOOD_ATTEMPTS_UNKNOWN_TASK` for tasks outside the corpus,
- `ERR_DOGFOOD_ATTEMPTS_EVIDENCE_MISSING` for missing or unsafe evidence paths,
- `ERR_DOGFOOD_ATTEMPTS_METRIC_INVALID` for malformed measurement values,
- `ERR_DOGFOOD_ATTEMPTS_OVERCLAIM` for public benchmark or superiority claims,
- `ERR_DOGFOOD_ATTEMPTS_PATH_UNSAFE` for output path escapes.

## Evaluation Fixtures

`fixtures/v54/manifest.json` covers:

- positive: one measured local attempt is recorded,
- negative: unknown task is blocked,
- negative: missing evidence is blocked,
- negative: invalid metrics are blocked,
- negative: overclaim text is blocked.

## Release Plan

V54 creates the first real input for future benchmark graphs. The next graph
work should consume this ledger only after multiple measured attempts exist and
should keep local dogfood evidence separate from public external benchmark
claims.
