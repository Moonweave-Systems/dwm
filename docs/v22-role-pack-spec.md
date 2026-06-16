# V22 Role Pack Spec

Status: implemented first role pack contract in `scripts/dwm_roles.py`.

## Research and Prior Art

Agent harnesses often treat roles as prompt flavor. DWM needs roles to be
contracts: each role must declare allowed tools, output schema, evidence
obligations, and a trust boundary before it can be used by a runner or harness
adapter.

## Product Position and Non-Goals

V22 makes the role pack inspectable and testable. It does not execute roles,
spawn workers, repair findings, call live models, or decide workflow success.

Required roles:

- `planner`,
- `explorer`,
- `worker`,
- `reviewer`,
- `verifier`,
- `operator`.

## Workflow Architecture

`packaging/dwm-roles.json` is the role registry. Each role must include:

- `id`,
- `purpose`,
- `allowed_tools`,
- `output_schema`,
- `evidence_obligations`,
- `trust_boundary`.

`scripts/dwm_roles.py` validates the registry, prints role contracts, and runs
the V22 fixture manifest.

## Execution Model

The role validator supports:

```bash
python scripts/dwm_roles.py registry
python scripts/dwm_roles.py role --role worker
python scripts/dwm_roles.py --manifest fixtures/v22/manifest.json --out out/roles/v22-final
```

The validator writes only fixture summary artifacts under `out/roles/`.

## Safety and Verification Gates

The role contract blocks:

- `ERR_ROLE_PERMISSION_ESCALATION` when a role declares risky tools such as
  network, secret, production, database, dependency, delete, external message,
  or history rewrite without a gate,
- `ERR_ROLE_OUTPUT_SCHEMA_MISSING` when output schema or evidence obligations
  are missing,
- `ERR_ROLE_REVIEWER_SELF_REPAIR` when reviewer can repair its own findings.

## Evaluation Fixtures

`fixtures/v22/manifest.json` covers:

- positive: full role registry is valid,
- positive: worker role contract is inspectable,
- negative: permission escalation is blocked,
- negative: missing output schema is blocked,
- negative: reviewer self-repair is blocked.

## Release Plan

V22 role contracts are prerequisites for later harness benchmarks and live
adapter execution. Future slices can bind these roles to Codex, Claude,
OpenCode/OMO, or shell adapters only after benchmark gates prove the evidence
model remains stronger than direct harness use.
