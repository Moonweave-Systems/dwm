# V42 Benchmark Candidate Spec

Status: implemented first benchmark publish candidate workflow in
`scripts/dwm_benchmark_candidate.py`.

## Research and Prior Art

After a benchmark series is built, the next useful artifact is not a README edit.
It is a publish candidate: a promotion-ready bundle that proves the series
passed the public-claim gate and can be reviewed before any tracked asset is
changed.

## Product Position and Non-Goals

V42 connects V41 series output to V39 promotion. It creates a candidate only
when the series history clears the promotion gate.

Non-goals:

- do not edit README,
- do not copy assets into `assets/`,
- do not bypass V39 promotion policy,
- do not accept stale series artifacts,
- do not claim external benchmark authority.

## Workflow Architecture

`scripts/dwm_benchmark_candidate.py` reads a V41 series directory and writes:

- `candidate.json`,
- `status.json`,
- `README-snippet.md`,
- a V39 promotion directory under `out/benchmark-promotions/`,
- `summary.json` for manifest suites.

The candidate records the series path, history path, promotion path, release
ids, trend metrics, README embed string, and source hashes.

## Execution Model

```bash
python scripts/dwm_benchmark_candidate.py make --series out/benchmark-series/<series_id> --out out/benchmark-candidates/<candidate_id>
python scripts/dwm_benchmark_candidate.py --manifest fixtures/v42/manifest.json --out out/benchmark-candidates/v42-final
```

Every output directory is guarded by a benchmark-candidate ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_BENCHMARK_CANDIDATE_ARTIFACT_MISSING` when series artifacts are missing,
- `ERR_BENCHMARK_CANDIDATE_STALE_SERIES` when series/status artifacts drift,
- `ERR_BENCHMARK_CANDIDATE_PROMOTION_NOT_UPWARD` when the underlying history
  regresses,
- `ERR_BENCHMARK_CANDIDATE_PROMOTION_DELTA_TOO_SMALL` when improvement is below
  the promotion threshold.

## Evaluation Fixtures

`fixtures/v42/manifest.json` covers:

- positive: promotion-ready series creates a candidate,
- negative: downward trend is blocked,
- negative: flat or too-small delta is blocked,
- negative: stale series is blocked,
- negative: missing series artifacts are blocked.

## Release Plan

V42 creates the final pre-publish artifact. A later workflow can promote a
reviewed candidate into tracked README assets.
