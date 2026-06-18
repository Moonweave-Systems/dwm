# V71 Release Timing Spec

Status: implemented release command timing planner and bounded measurement
recorder in `scripts/dwm_release_timing.py`.

## Research and Prior Art

V70 made long-running release contracts visible by printing progress and
failing timed-out child commands. The next gap is historical cost evidence:
operators can see where a run is stuck, but the repo did not have a structured
artifact for command inventory, measured duration, timeout, and source hashes.

## Product Position and Non-Goals

V71 records release verification cost as deterministic evidence. It supports a
plan-only mode for command inventory and a bounded measure mode for explicit
profiling.

Non-goals:

- do not rerun the full release corpus by default,
- do not treat timeout as success,
- do not publish an upward benchmark claim,
- do not replace `scripts/check_contract.py`.

## Workflow Architecture

The canonical command source remains `scripts/dwm.py:RELEASE_COMMANDS`.
`scripts/dwm_release_timing.py` writes:

- `release-timing.json`,
- `release-timing.md`,
- `status.json`,
- manifest `summary.json`.

Each command record includes command text, command hash, duration, return code,
timeout status, stdout hash, stderr hash, and source hashes.

## Execution Model

Default `plan` mode does not execute release commands:

```bash
python scripts/dwm_release_timing.py plan --out out/release-timing/<timing_id>
```

Bounded measurement must be explicit:

```bash
python scripts/dwm_release_timing.py measure --limit 3 --out out/release-timing/<timing_id>
```

The manifest fixture uses short local Python commands so the contract can prove
the schema without paying the full release-corpus runtime cost.

## Safety and Verification Gates

Timeouts and non-zero exits produce `release-timing-blocked`. Plan-only output
uses `release-timing-planned` and records `measured_count: 0`. Output paths must
resolve under repo-local `out/release-timing/` and existing directories must
carry the V71 ownership sentinel before replacement.

## Evaluation Fixtures

`fixtures/v71/manifest.json` covers:

- release command inventory without execution,
- bounded successful measurement,
- timeout blocking.

## Release Plan

V71 adds timing artifacts to the release command corpus and command reference.
Future slices can aggregate these artifacts into trend history, but V71 itself
only records local verification cost evidence.
