# V50 Release Candidate Cut Spec

Status: implemented first release candidate cut in
`scripts/dwm_release_candidate.py`.

## Research and Prior Art

V44-V45 protect benchmark publication, V48 gives the operator a daily handoff,
and V49 prevents adapter parity overclaims. V50 combines those safety surfaces
into a release-candidate artifact before any public release or README asset
change.

## Product Position and Non-Goals

V50 is a release candidate cut, not a hosted release. It records whether current
evidence is coherent enough to prepare release notes.

Non-goals:

- do not create a GitHub release,
- do not publish packages,
- do not edit tracked README benchmark assets,
- do not execute live Codex, Claude, or shell adapters,
- do not claim external benchmark superiority or full autonomy.

## Workflow Architecture

`scripts/dwm_release_candidate.py` consumes:

- a V49 `adapter-parity.json` and `status.json`,
- a V48 `operator-loop.json` and `status.json`,
- proposed release-note text, if provided.

It writes:

- `release-candidate.json`,
- `status.json`,
- `release-notes.md`,
- `release-checklist.md`.

The release candidate separates implemented, experimental, and deferred
capabilities. It also verifies that `codex run` remains blocked by the V49
planned-only gate before a live adapter contract exists.

## Execution Model

```bash
python scripts/dwm_release_candidate.py cut --parity out/adapters/<parity_id> --operator out/daily-operator/<operator_id> --out out/release-candidates/<candidate_id>
python scripts/dwm_release_candidate.py --manifest fixtures/v50/manifest.json --out out/release-candidates/v50-final
```

Every output directory is guarded by a release-candidate ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_RELEASE_CANDIDATE_PARITY_MISSING` when parity artifacts are missing,
- `ERR_RELEASE_CANDIDATE_PARITY_STALE` when parity hashes or planned adapter
  blocking drift,
- `ERR_RELEASE_CANDIDATE_OPERATOR_MISSING` when operator artifacts are missing,
- `ERR_RELEASE_CANDIDATE_OPERATOR_STALE` when operator artifacts drift,
- `ERR_RELEASE_CANDIDATE_OVERCLAIM` when release notes make unsupported public
  claims,
- `ERR_RELEASE_CANDIDATE_PATH_UNSAFE` when output paths escape the owned root.

## Evaluation Fixtures

`fixtures/v50/manifest.json` covers:

- positive: coherent V48/V49 inputs produce a release candidate,
- negative: missing parity blocks,
- negative: stale parity blocks,
- negative: stale operator loop blocks,
- negative: unsupported overclaim text blocks.

## Release Plan

V50 gives the next public release a clean preflight artifact. A later release
workflow may publish only after the full contract passes and human review
confirms README claims, benchmark assets, and adapter support labels.
