# V35 Live Report Spec

Status: implemented first live benchmark report gate in
`scripts/dwm_live_report.py`.

## Research and Prior Art

V34 separates confirmed, refuted, and unverified live score evidence. V35 turns
that reviewed evidence into a report artifact and adds graph-ready metrics for a
future README benchmark chart.

## Product Position and Non-Goals

V35 is a publication gate for DWM's own benchmark evidence pipeline. It may
record `benchmark_success_claimed: true` only when `--publish-claim` is explicit
and the V34 review is `review-ready`. It does not claim general model
superiority or hosted benchmark coverage.

Non-goals:

- do not execute live model attempts,
- do not publish refuted or unverified evidence as success,
- do not generate README graphics yet,
- do not claim Codex, Claude, OpenCode, or OMO model quality superiority,
- do not accept stale review hashes.

## Workflow Architecture

`scripts/dwm_live_report.py` reads a V34 review directory and writes:

- `report.json`,
- `report.md`,
- `status.json`,
- `summary.json` for manifest suites.

`report.json` includes `graph_metrics` for future README benchmark charts.

## Execution Model

```bash
python scripts/dwm_live_report.py publish --review out/live-score-reviews/<review_id> --out out/live-reports/<report_id>
python scripts/dwm_live_report.py publish --review out/live-score-reviews/<review_id> --out out/live-reports/<report_id> --publish-claim
python scripts/dwm_live_report.py --manifest fixtures/v35/manifest.json --out out/live-reports/v35-final
```

Every output directory is guarded by a live-report ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_LIVE_REPORT_ARTIFACT_MISSING` when review artifacts are missing,
- `ERR_LIVE_REPORT_STALE_REVIEW` when expected review hash does not match,
- `ERR_LIVE_REPORT_HASH_MISMATCH` when review source hashes are incomplete,
- `ERR_LIVE_REPORT_UNSUPPORTED_CLAIM` when claim publication is requested
  without `review-ready` evidence.

## Evaluation Fixtures

`fixtures/v35/manifest.json` covers:

- positive: review-ready evidence can publish an explicit benchmark claim,
- positive: refuted evidence can be reported without claiming success,
- positive: unverified evidence can be reported without claiming success,
- negative: unsupported claim is blocked,
- negative: stale review hash is blocked,
- negative: review hash mismatch is blocked,
- negative: missing review artifact is blocked.

## Release Plan

V35 closes the first live scoring workflow. A later README visualization should
read `report.json.graph_metrics` rather than recomputing benchmark values from
logs or prose.
