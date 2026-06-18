# V72 Release Timing History Spec

Status: implemented release timing history ledger in
`scripts/dwm_release_timing_history.py`.

## Research and Prior Art

V71 records one release timing run. That is useful evidence, but it is not yet
a trend source. Public graphs should not be drawn from one run or copied prose,
so V72 adds a source-hashed history ledger before any README trend claim.

## Product Position and Non-Goals

V72 turns timing artifacts into an appendable evidence surface for release
verification cost. It is still an internal process history, not a public
performance benchmark.

Non-goals:

- do not publish upward benchmark claims,
- do not infer direct-agent superiority,
- do not execute release commands,
- do not replace V71 timing capture.

## Workflow Architecture

`scripts/dwm_release_timing_history.py` reads V71 `release-timing.json`
artifacts and writes:

- `timing-history.json`,
- `timing-history.md`,
- `status.json`,
- manifest `summary.json`.

The history record stores sorted timing entries, planned/recorded/blocked
counts, total measured duration, total measured command count, slowest record,
and source hashes.

## Execution Model

Build a history from existing V71 timing artifacts:

```bash
python scripts/dwm_release_timing_history.py build --timing-root out/release-timing --out out/release-timing-history/<history_id>
```

The command is read-only against timing inputs. It does not execute release commands. It only writes under repo-local `out/release-timing-history/`.

## Safety and Verification Gates

The ledger blocks duplicate `timing_id` values, malformed timing artifacts,
unknown timing statuses, unsafe paths, symlinked paths, and empty timing roots.
Blocked timing runs are preserved as evidence; they are not rewritten as
success.

## Evaluation Fixtures

`fixtures/v72/manifest.json` covers:

- mixed planned/recorded/blocked history aggregation,
- duplicate timing id blocking.

## Release Plan

V72 adds history artifacts to the release command corpus. Later graph work can
consume `timing-history.json`, but this slice only records the ledger and keeps
README trend claims gated.
