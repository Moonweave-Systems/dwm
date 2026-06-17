# V58 Dogfood Pair Series Spec

Status: implemented first dogfood pair series and graph-readiness gate in
`scripts/dwm_dogfood_pair_series.py`.

## Research and Prior Art

V57 created a gated comparison pair. A single pair is useful evidence, but it is
not enough for a README graph or a public trend. V58 collects local dogfood
pairs into a series and records whether graph promotion is blocked.

## Product Position and Non-Goals

V58 is a series and readiness gate. It does not draw or publish a graph.

Non-goals:

- do not publish README benchmark graphs,
- do not claim DWM beats direct Codex,
- do not accept stale comparison pairs,
- do not accept pair-level graph readiness claims,
- do not treat fewer than three pairs as graph-ready.

## Workflow Architecture

The command is:

```bash
python scripts/dwm_dogfood_pair_series.py build --pair-root out/dogfood-pairs --out out/dogfood-pair-series/<series_id>
```

It reads `comparison-pair.json` and `pair-status.json` from dogfood pair
directories.

It writes:

- `pair-series.json`,
- `pair-series.md`,
- `graph-readiness.json`,
- `status.json`.

## Safety and Verification Gates

The gate blocks:

- `ERR_DOGFOOD_PAIR_SERIES_DUPLICATE_PAIR` when pair hashes repeat,
- `ERR_DOGFOOD_PAIR_SERIES_STALE_PAIR` when `comparison-pair.json` and
  `pair-status.json` drift,
- `ERR_DOGFOOD_PAIR_SERIES_OVERCLAIM` when a pair claims graph readiness,
- `ERR_DOGFOOD_PAIR_SERIES_UNVERIFIED_PAIR` when either mode failed
  verification.

A series with fewer than three pairs is still recorded, but
`graph-readiness.json` includes `ERR_DOGFOOD_PAIR_SERIES_INSUFFICIENT_PAIRS`.

## Evaluation Fixtures

`fixtures/v58/manifest.json` covers:

- positive: three unique pairs record a graph-ready local review series,
- positive: one pair records a blocked readiness reason,
- negative: duplicate pairs are blocked,
- negative: stale pairs are blocked,
- negative: overclaiming pairs are blocked.

## Release Plan

V58 moves the project from one pair to a series gate. A later slice can use
series artifacts to create a local-only chart candidate, but public README graph
promotion still needs a separate review gate.
