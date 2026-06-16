# V17 Dashboard And Approval UI Spec

Status: implemented read-only in `scripts/dwm_hud.py`.

## Research And Prior Art

OMX-style tools are easier to use because operators can see sessions, teams,
and status. DWM needs a product shell that shows trusted evidence, gates, and
next actions without weakening the artifact contract.

## Product Position And Non-Goals

V17 adds a local read-only dashboard/HUD summary over DWM artifacts. Approval
artifact writing remains a later slice.

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
- human gate approval form, planned after read-only HUD proof,
- command preview.

## Execution Model

The first V17 slice is local-first and read-only. It writes only derived
`hud-summary.json` and `hud-summary.md` files under `out/hud/`. A later approval
slice may write approval artifacts only through an explicit tracked approval
schema and only after rendering the evidence being approved.

## Safety And Verification Gates

Every approval must be traceable to a run, packet, evidence set, approver,
timestamp, and allowed output. UI approval cannot authorize worker execution,
merge, deployment, external message, secret access, or dependency installation
unless the matching risk gate explicitly allows it.

## Evaluation Fixtures

- positive: fanout-ready artifacts render as `ready` with worker review as the
  next action,
- positive: ownership conflicts render as `needs_review`,
- negative: failed workers render as `blocked`,
- negative: stale fanout evidence blocks with `ERR_HUD_STALE_EVIDENCE`.

## Release Plan

1. Add read-only local HUD summary.
2. Add fixture-backed HUD contract tests.
3. Add rendered screenshot or DOM contract tests.
4. Add approval artifact writer only after read-only UI is proven.
5. Keep CLI as the authoritative fallback.
