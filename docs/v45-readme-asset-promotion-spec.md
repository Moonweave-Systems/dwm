# V45 README Asset Promotion Spec

Status: implemented first README asset promotion bundle in
`scripts/dwm_readme_asset_promotion.py`.

## Research and Prior Art

V44 proves a benchmark candidate review is approved, but a release workflow
still needs a controlled promotion boundary before tracked README assets change.
The useful first slice is an asset promotion bundle: copy the approved graph
asset into a reviewable output directory, write metadata, and produce a diff
summary that a human can inspect before tracked files are changed.

## Product Position and Non-Goals

V45 consumes `candidate-review.json` and creates an asset-promotion bundle.

Non-goals:

- do not commit tracked assets,
- do not edit README directly,
- do not claim external benchmark authority,
- do not bypass V44 review approval,
- do not accept stale review, candidate, promotion, or asset evidence.

## Workflow Architecture

`scripts/dwm_readme_asset_promotion.py` reads a V44 review directory and writes:

- `asset-promotion.json`,
- `status.json`,
- `dwm-benchmark-trend.svg`,
- `dwm-benchmark-trend.json`,
- `README-snippet.md`,
- `asset-diff.md`,
- `summary.json` for manifest suites.

The bundle proposes tracked targets under `assets/` but writes only under
`out/readme-asset-promotions/`. `asset-diff.md` is the handoff for human review
before any tracked README asset is modified.

## Execution Model

```bash
python scripts/dwm_readme_asset_promotion.py promote --review out/benchmark-candidate-reviews/<review_id> --out out/readme-asset-promotions/<promotion_id>
python scripts/dwm_readme_asset_promotion.py --manifest fixtures/v45/manifest.json --out out/readme-asset-promotions/v45-final
```

Every output directory is guarded by an asset-promotion ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_README_ASSET_PROMOTION_ARTIFACT_MISSING` when review artifacts are missing,
- `ERR_README_ASSET_PROMOTION_STALE_REVIEW` when review/status artifacts drift,
- `ERR_README_ASSET_PROMOTION_REVIEW_NOT_APPROVED` when review status is not approved,
- `ERR_README_ASSET_PROMOTION_OVERCLAIM` when blocked claim terms remain,
- `ERR_README_ASSET_PROMOTION_CANDIDATE_MISSING` when candidate evidence is missing,
- `ERR_README_ASSET_PROMOTION_PROMOTION_MISSING` when promotion evidence is missing,
- `ERR_README_ASSET_PROMOTION_ASSET_MISSING` when the approved SVG is missing,
- `ERR_README_ASSET_PROMOTION_HASH_MISMATCH` when review hashes no longer match source artifacts.

## Evaluation Fixtures

`fixtures/v45/manifest.json` covers:

- positive: approved review creates an asset-promotion bundle,
- negative: stale review is blocked,
- negative: missing approved asset is blocked,
- negative: hash drift is blocked,
- negative: non-approved review is blocked,
- negative: overclaim terms are blocked.

## Release Plan

V45 produces a reviewable bundle only. A later public release step may copy the
bundle into tracked `assets/` and update README after human inspection of
`asset-diff.md`.
