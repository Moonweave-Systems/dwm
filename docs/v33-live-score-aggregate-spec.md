# V33 Live Score Aggregate Spec

Status: implemented first live score aggregate gate in
`scripts/dwm_live_score_aggregate.py`.

## Research and Prior Art

V32 records task-level score evidence. V33 adds the first aggregate gate across
the required benchmark task set. It aggregates score artifacts without claiming
final benchmark success.

## Product Position and Non-Goals

V33 records aggregate score evidence for all required tasks. It can produce a
success candidate only when explicitly requested and every required task has a
passed score. Even then, `benchmark_success_claimed` remains false until the V34
adversarial review gate.

Non-goals:

- do not execute live model attempts,
- do not score missing tasks,
- do not tolerate duplicate task scores,
- do not claim benchmark success before adversarial review,
- do not publish model-quality claims.

## Workflow Architecture

`scripts/dwm_live_score_aggregate.py` reads one V32 score directory per required
task and writes:

- `aggregate-score.json`,
- `status.json`,
- `summary.json` for manifest suites.

The aggregate stores per-task score hashes and the required task-id hash.

## Execution Model

```bash
python scripts/dwm_live_score_aggregate.py aggregate --score-dir out/live-scores/<score_id> --out out/live-score-aggregates/<aggregate_id>
python scripts/dwm_live_score_aggregate.py --manifest fixtures/v33/manifest.json --out out/live-score-aggregates/v33-final
```

Use repeated `--score-dir` arguments for multiple task scores. Add
`--claim-success` only when the caller wants the gate to block failed task
scores as unsupported claims.

## Safety and Verification Gates

The gate blocks:

- `ERR_LIVE_SCORE_AGGREGATE_ARTIFACT_MISSING` when score artifacts are missing,
- `ERR_LIVE_SCORE_AGGREGATE_STALE_SCORE` when score hashes drift or score
  artifacts are malformed,
- `ERR_LIVE_SCORE_AGGREGATE_TASK_MISSING` when a required task has no score,
- `ERR_LIVE_SCORE_AGGREGATE_TASK_DUPLICATE` when a task has duplicate scores,
- `ERR_LIVE_SCORE_AGGREGATE_UNSUPPORTED_CLAIM` when success is requested with
  failed tasks.

## Evaluation Fixtures

`fixtures/v33/manifest.json` covers:

- positive: all required tasks pass and a success candidate is recorded,
- positive: failed task aggregate is recorded when success is not claimed,
- negative: missing required task is blocked,
- negative: duplicate task is blocked,
- negative: stale score hash is blocked,
- negative: unsupported success claim is blocked,
- negative: missing score artifact is blocked.

## Release Plan

V33 finishes the first aggregate scoring layer. V34 must adversarially review
`aggregate-score.json` before any benchmark success claim is allowed.
