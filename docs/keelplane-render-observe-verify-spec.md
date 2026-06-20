# Keelplane Render-Observe Verification Type Spec

Status: planned verification type
Date: 2026-06-20

## Research And Prior Art

Idea handed off from the `fivetaku/fablize` plugin (plugin itself not adopted:
duplicates the existing harness/Keelplane and adds a third-party hook surface).
The transferable kernel: a task that produces a renderable/executable artifact
must not be declared complete on "I created it" — it needs evidence of actually
running/observing the artifact. fablize enforced this via hooks
(`gate_post_tool.py` / `gate_stop.py`); Keelplane implements the same effect as a
PHASE GATE, adding no hook surface.

Reuse, do not reinvent: `scripts/dwm_dogfood_chart_render.py` already renders SVG
charts; the `figure-verifier` and `scientific-visualization` skills already check
"does the figure show the claimed values." This stage composes that logic; it
does not build a new renderer.

## Product Position And Non-Goals

This is NOT a new gate or layer. It is one new VERIFICATION TYPE that extends the
loop's existing rule ("verify is an observation, not a claim") to visual/render
artifacts. For executable code the rule is already enforced: the loop's
`verification_command` must actually run and pass for `verified-complete`, and a
fault run stops at `failed`. So for code, this spec only makes the rule explicit;
the new work is for renderable artifacts.

Non-Goals:
- Do NOT make the gate a non-deterministic screenshot/vision check. The GATE is a
  deterministic observation assertion; a rendered image is captured as EVIDENCE
  only.
- Do NOT add a hook surface; this is a phase gate.
- Do NOT reimplement chart rendering or figure verification; compose existing
  scripts/skills.
- Do NOT widen to every artifact type at once; scope to SVG/chart first.
- No superiority/autonomy claim.

## Architecture (no new loop mechanism)

The loop already runs an arbitrary `verification_command` against the worker's
output, and the verification is loop-owned and immutable (the worker cannot edit
it). The render-observe type is therefore just a loop-owned immutable test that:

1. takes the worker-produced artifact (e.g. a generated SVG/chart),
2. renders/parses it deterministically (parse the SVG XML; no browser, no vision),
3. asserts the OBSERVED content matches the declared input. To avoid fragile
   pixel-scale inversion (renderer-dependent), the plan declares an OUTPUT
   CONTRACT requiring the chart to embed its data observably (data-* attributes
   or text/data labels); the assertion extracts those embedded values and
   compares to the input. The worker must satisfy the contract, not a particular
   renderer.
4. fails if the artifact merely exists, is empty, or encodes wrong values.

Scope of the deterministic gate (H2): this covers PARSEABLE-DATA artifacts
(data charts/SVGs whose values can be extracted from text/embedded data).
Interactive/visual correctness (games, UI, "does it work when rendered") is
inherently non-deterministic and is handled as OPT-IN LIVE EVIDENCE (screenshot
/ headless render / vision), never as the deterministic keep gate. The first
slice does data charts only; UI/game live-evidence is a later, evidence-only
path.

The rendered artifact (SVG, or an optional PNG/screenshot) is written into the
evidence bundle as observation evidence; the PASS/FAIL gate is the deterministic
assertion in step 3.

## Execution Model

- A render-observe phase declares: the target artifact path, the input data, and
  the loop-owned immutable assertion test (parse + value-match).
- The loop runs it exactly like any verification: restore the immutable test,
  run it, gate on result. "Created" alone fails because the test asserts values,
  not file existence.
- Evidence: the generated artifact (and an optional opt-in live render image) is
  captured in the run's evidence; the deterministic assertion is the gate.

## Safety And Verification Gates

- The gate stays deterministic (parse text, compare numbers) so it joins the
  keep gate with no network, no browser, no codex.
- An optional live browser/headless render that produces a screenshot is
  EVIDENCE only and opt-in; it never becomes the deterministic keep gate.
- Same immutable-verification protections as the loop: the assertion test is
  restored before each verify, plugin autoload disabled, verification-affecting
  new files fail the phase. The worker cannot game the value assertion.

## Evaluation Fixtures

A chart task fixture proving the type is real, not a file-existence check:
- correct chart (SVG bars/points encode the input values) -> assertion PASS;
- "created but wrong": a chart whose encoded values do NOT match the input ->
  assertion FAIL;
- empty/placeholder artifact -> assertion FAIL.

These run deterministically (parse the generated SVG, compare to input) in the
keep gate, no codex/browser.

## Implementation Plan

1. A reusable render-observe assertion helper: parse a generated SVG/chart and
   compare its encoded values to declared input data (reuse the existing chart
   render/parse code; align with figure-verifier's consistency check).
2. A loop fixture (`fixtures/keelplane-render/`) with the three cases above,
   wired as a render-observe verification type for the loop's deterministic keep
   gate (no codex, no browser).
3. Document the verification type in the loop spec: "renderable artifact ->
   verification must render + assert observed content; 'created' is FAIL."
4. Capture the generated artifact in the evidence bundle; keep an optional
   opt-in live render (screenshot) as evidence only.

## Open Questions

- Whether HTML/UI artifacts (needing a real DOM) get a deterministic parse path
  or stay opt-in live-evidence until a later slice.
- Whether the render-observe assertion should call `figure-verifier` directly or
  embed a minimal parser for the keep gate's determinism.
- Whether to add a PNG rasterization step for human-facing evidence or keep SVG
  text only.
