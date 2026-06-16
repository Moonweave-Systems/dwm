# V17 Dashboard And Approval UI Spec

Status: implemented in `scripts/dwm_hud.py`.

## Research And Prior Art

OMX-style tools are easier to use because operators can see sessions, teams,
and status. DWM needs a product shell that shows trusted evidence, gates, and
next actions without weakening the artifact contract.

## Product Position And Non-Goals

V17 adds a local dashboard/HUD summary over DWM artifacts plus a narrow,
hash-bound approval artifact writer for HUD evidence review.

Non-goals:

- do not make UI state authoritative,
- do not approve gates from untracked chat messages,
- do not hide raw artifacts,
- do not require a hosted service.

## Workflow Architecture

The dashboard reads DWM artifacts and exposes:

- run list,
- current recommendation,
- trust checks,
- evidence browser,
- review queue,
- human gate approval form,
- command preview.

## Execution Model

The V17 slice is local-first. It writes derived `hud-summary.json` and
`hud-summary.md` files under `out/hud/`, then may write `approval.json` and
`approval.md` only for ready HUD summaries whose source hashes still match the
rendered evidence.

## Safety And Verification Gates

Every approval must be traceable to a run, packet, evidence set, approver,
timestamp, and allowed output. UI approval cannot authorize worker execution,
merge, deployment, external message, secret access, or dependency installation
unless the matching risk gate explicitly allows it.

V17 approvals may approve only `hud-summary.md`. They must include the required
safety attestation:

`no worker execution, merge, deployment, external message, secret access, or dependency installation is approved by this artifact`

## Evaluation Fixtures

- positive: fanout-ready artifacts render as `ready` with worker review as the
  next action,
- positive: ownership conflicts render as `needs_review`,
- negative: failed workers render as `blocked`,
- negative: stale fanout evidence blocks with `ERR_HUD_STALE_EVIDENCE`,
- positive: ready HUD summary writes `approval.json`,
- negative: blocked HUD summary refuses approval with
  `ERR_HUD_APPROVAL_SOURCE_BLOCKED`,
- negative: stale source hashes refuse approval with `ERR_HUD_STALE_EVIDENCE`,
- negative: unsafe attestations refuse approval with `ERR_HUD_APPROVAL_UNSAFE`.

## Release Plan

1. Add read-only local HUD summary.
2. Add fixture-backed HUD contract tests.
3. Add hash-bound approval artifact writer.
4. Add rendered screenshot or DOM contract tests.
5. Keep CLI as the authoritative fallback.
