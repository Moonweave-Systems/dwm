# V39 Benchmark Promotion Spec

Status: implemented first benchmark trend promotion gate in
`scripts/dwm_benchmark_promotion.py`.

## Research and Prior Art

Good public trend graphs are not just charts. They are claims. A README growth
chart needs a gate that checks whether the evidence is old enough, distinct
enough, release-grade, and actually improving. V38 can build a history ledger;
V39 decides whether that ledger is eligible to become a public trend claim.

## Product Position and Non-Goals

V39 prevents DWM from publishing a fake upward graph. It promotes a trend only
when the history is hash-bound and satisfies an explicit policy:

- minimum entry count,
- unique report hashes,
- release source kind,
- non-decreasing score sequence,
- minimum score delta.

Non-goals:

- do not invent missing history points,
- do not promote fixture or ad-hoc histories by default,
- do not hide regressions,
- do not claim external benchmark authority,
- do not edit README automatically.

## Workflow Architecture

`scripts/dwm_benchmark_promotion.py` reads a V38 history directory and writes:

- `promotion.json`,
- `status.json`,
- `promoted-trend.svg`,
- `README-snippet.md`,
- `summary.json` for manifest suites.

The promotion output copies the V38 `trend.svg` only after policy validation.

## Execution Model

```bash
python scripts/dwm_benchmark_promotion.py promote --history out/benchmark-history/<history_id> --out out/benchmark-promotions/<promotion_id>
python scripts/dwm_benchmark_promotion.py --manifest fixtures/v39/manifest.json --out out/benchmark-promotions/v39-final
```

By default, promotion requires at least three entries and a score delta of at
least 100 basis points.

## Safety and Verification Gates

The gate blocks:

- `ERR_BENCHMARK_PROMOTION_ARTIFACT_MISSING` when history artifacts are missing,
- `ERR_BENCHMARK_PROMOTION_STALE_HISTORY` when history/status artifacts drift,
- `ERR_BENCHMARK_PROMOTION_INSUFFICIENT_HISTORY` when there are too few entries,
- `ERR_BENCHMARK_PROMOTION_SOURCE_NOT_RELEASE` when source entries are not
  release-grade,
- `ERR_BENCHMARK_PROMOTION_NOT_UPWARD` when the score sequence regresses,
- `ERR_BENCHMARK_PROMOTION_DELTA_TOO_SMALL` when improvement is too small.

## Evaluation Fixtures

`fixtures/v39/manifest.json` covers:

- positive: release-kind three-point trend can be promoted,
- negative: two entries are insufficient,
- negative: fixture source kind is blocked,
- negative: downward trend is blocked,
- negative: flat trend is blocked,
- negative: stale history is blocked.

## Release Plan

V39 makes README trend publishing honest. A later slice can promote a real
`promotion-ready` artifact into tracked `assets/` after real release histories
exist.
