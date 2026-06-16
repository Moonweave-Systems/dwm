# V34 Live Score Review Spec

Status: implemented first adversarial live score review gate in
`scripts/dwm_live_score_review.py`.

## Research and Prior Art

V33 records aggregate live score evidence. V34 adds the adversarial verification
boundary required before a report can use that aggregate. The review separates
confirmed evidence from refuted and unverified claims.

## Product Position and Non-Goals

V34 is a review gate, not a publication gate. It records whether an aggregate is
structurally review-ready, refuted by failed tasks, or still unverified because
no success claim was requested. It does not claim benchmark success.

Non-goals:

- do not execute live model attempts,
- do not rewrite aggregate scores,
- do not accept stale aggregate hashes,
- do not turn review-ready into published success,
- do not publish model-quality claims.

## Workflow Architecture

`scripts/dwm_live_score_review.py` reads a V33 aggregate directory and writes:

- `reviewed-score.json`,
- `status.json`,
- `summary.json` for manifest suites.

The review stores confirmed, refuted, and unverified lists with aggregate and
score source hashes.

## Execution Model

```bash
python scripts/dwm_live_score_review.py review --aggregate out/live-score-aggregates/<aggregate_id> --out out/live-score-reviews/<review_id>
python scripts/dwm_live_score_review.py --manifest fixtures/v34/manifest.json --out out/live-score-reviews/v34-final
```

Every output directory is guarded by a live-score-review ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_LIVE_SCORE_REVIEW_ARTIFACT_MISSING` when aggregate artifacts are missing,
- `ERR_LIVE_SCORE_REVIEW_STALE_AGGREGATE` when aggregate hashes drift,
- `ERR_LIVE_SCORE_REVIEW_TASK_MISMATCH` when aggregate tasks do not match the
  required task set,
- `ERR_LIVE_SCORE_REVIEW_HASH_MISMATCH` when required task or score hashes are
  incomplete or stale.

## Evaluation Fixtures

`fixtures/v34/manifest.json` covers:

- positive: all passed candidate becomes `review-ready`,
- positive: failed aggregate becomes `refuted`,
- positive: non-claimed aggregate remains `unverified`,
- negative: stale aggregate hash is blocked,
- negative: task mismatch is blocked,
- negative: hash mismatch is blocked,
- negative: missing aggregate artifact is blocked.

## Release Plan

V34 prepares the evidence boundary for V35. V35 may produce a final report from
`reviewed-score.json`, but only if it preserves the confirmed/refuted/unverified
separation and does not overclaim benchmark success.
