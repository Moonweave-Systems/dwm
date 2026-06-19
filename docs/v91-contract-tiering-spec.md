# V91 Contract Tiering Spec

Status: implemented release-contract tiering in `scripts/check_contract.py`.

## Research and Prior Art

V70 made long contract runs diagnosable with progress output and fail-closed
timeouts. Later work increased the release command corpus enough that always
running the full contract became slow for iterative development.

V91 adds explicit verification tiers so operators can run a fast smoke check or
a changed-surface check without weakening the full release contract.

## Product Position and Non-Goals

V91 is a verification workflow optimization. It keeps the full contract intact
and adds faster tiers for day-to-day work.

Non-goals:

- do not remove full release commands,
- do not treat smoke or changed tiers as publish approval,
- do not hide timeout failures,
- do not change generated evidence semantics.

## Workflow Architecture

`scripts/check_contract.py` now accepts:

- `--tier smoke`: fixture smoke plus quick package, doctor, whitespace, and
  release-text checks;
- `--tier changed`: fixture smoke plus V88 roadmap reconciliation, V89 command
  safety, V90 activation v2, doctor, and release-text checks;
- `--tier full`: the existing full release command corpus and all decision
  consistency checks.

The default remains `--tier full`, so `python scripts/check_contract.py`
preserves the old behavior.

## Execution Model

```bash
python scripts/check_contract.py --tier smoke
python scripts/check_contract.py --tier changed
python scripts/check_contract.py
```

## Safety and Verification Gates

The tiering gate is fail-closed. A failing smoke or changed tier blocks the
current change. Full release remains required before publishing.

## Evaluation Fixtures

`python scripts/check_contract.py --self-test` covers tier step selection for
`smoke`, `changed`, and `full`.

## Release Plan

V91 documents the faster verification path and keeps full release verification as the publishing boundary.
