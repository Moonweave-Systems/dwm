# V49 Adapter Parity Matrix Spec

Status: implemented first adapter parity matrix in `scripts/dwm_adapters.py`.

## Research and Prior Art

V19 created the adapter registry and V27 added safe adapter smoke evidence, but
the product surface can still be misread as equivalent support for Codex,
Claude, shell, and fixture adapters. V49 makes parity explicit before V50 release
candidate work: every adapter must declare its support level, auth assumption,
isolation model, evidence fields, supported actions, planned actions, and
unsupported risk actions.

## Product Position and Non-Goals

V49 is a parity and overclaim gate. It records what each adapter can do today
and what remains planned or unsupported.

Non-goals:

- do not execute live Codex, Claude, shell, or external model adapters,
- do not treat `planned` as `supported`,
- do not promote fixture-only support as external adapter parity,
- do not auto-install, authenticate, or mutate global adapter configuration,
- do not allow risk capabilities to bypass DWM gates.

## Workflow Architecture

`packaging/dwm-adapters.json` is the source registry. V49 requires every adapter
entry to include:

- `support_level`: `supported`, `planned`, `fixture-only`, or `unsupported`,
- `auth_assumption`,
- `isolation`,
- `mode`,
- `lifecycle`,
- complete risk capability booleans,
- normalized transcript and evidence schema.

`scripts/dwm_adapters.py parity` writes:

- `adapter-parity.json`,
- `adapter-parity.md`,
- `status.json`.

The generated matrix includes adapter hashes, registry hash, supported actions,
planned actions, unsupported actions, evidence fields, and overclaim blocks.

## Execution Model

```bash
python scripts/dwm_adapters.py parity --out out/adapters/<parity_id>
python scripts/dwm_adapters.py action-check --adapter codex --action run
python scripts/dwm_adapters.py --manifest fixtures/v49/manifest.json --out out/adapters/v49-final
```

`action-check` is a policy check, not an execution command. `fixture run` is
allowed only as fixture-scoped evidence. `codex run` remains blocked as
planned-only until a live adapter contract is verified.

## Safety and Verification Gates

The gate blocks:

- `ERR_ADAPTER_PARITY_INCOMPLETE` when an adapter lacks parity metadata,
- `ERR_ADAPTER_PARITY_UNKNOWN_ADAPTER` when a caller names an unknown adapter,
- `ERR_ADAPTER_PARITY_UNSUPPORTED_ACTION` when the adapter does not support an
  action or risk capability,
- `ERR_ADAPTER_PARITY_PLANNED_ONLY` when a planned adapter action is requested
  before live support exists.

V49 preserves the safe default: record the matrix, block unsupported actions,
and require a later human-reviewed adapter contract before live execution.

## Evaluation Fixtures

`fixtures/v49/manifest.json` covers:

- positive: adapter parity matrix is recorded,
- positive: fixture-scoped run is allowed,
- negative: Codex live run is planned-only and blocked,
- negative: shell network capability is unsupported and blocked,
- negative: unknown adapter is blocked,
- negative: missing parity metadata is blocked.

## Release Plan

V49 closes the adapter ambiguity before V50. V50 can use the V49 matrix as
release evidence, while README simplification and canonical demos can point to
this matrix instead of implying equal adapter support.
