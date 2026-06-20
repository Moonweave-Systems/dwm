# Keelplane Auto-Planning Stage Spec

Status: planned series stage
Date: 2026-06-20

## Research And Prior Art

The autonomous loop currently needs a hand-authored plan (per-phase target files,
prompts, and the loop-owned immutable verification) for every task — high
friction. OMO's "Ultra Work" auto-plans from a bare objective. Keelplane's
`SKILL.md` design contract IS a planner: it already turns an objective into
phases, workers, handoffs, and verification. This stage runs that planner to
produce a loop-consumable plan, lowering the friction to start a real task.

## The Trust-Anchor Decision (the load-bearing choice)

The loop's trust bottoms out at HUMAN-authored immutable acceptance tests (a
phase is verified only because a test the worker cannot edit passed). If the
planner GENERATED those tests, the trust anchor would become model-authored and
the whole "verified means something" guarantee would weaken.

Therefore: the planner generates the PLAN STRUCTURE only (phases, target files,
per-phase prompts, and which acceptance test gates each phase). The HUMAN
provides the acceptance tests. Input is `objective + acceptance tests`, not
`objective -> everything`. This keeps the loop's trust model intact while still
removing the decomposition friction.

## Product Position And Non-Goals

A new STAGE on the spine (objective + tests -> plan), feeding the existing loop.
Not a new mechanism; reuse the `compile_workflow` plan schema and the SKILL.md
design contract.

Non-Goals:
- Do NOT auto-generate the acceptance tests / the verification gate. Tests stay
  human-authored (trust anchor).
- Do NOT make the loop execute the generated plan automatically without the human
  seeing it; the generated plan is reviewable before a run.
- Do NOT touch V94-V101, run_workflow.py, or the loop/promote/render stages'
  gates.
- No superiority/autonomy claim.

## Architecture (new stage, artifact contract)

- Input artifact: `objective` (text) + declared human acceptance test files +
  declared target file paths.
- Worker: a planner agent guided by the SKILL.md design contract. It decomposes
  the objective into ordered phases, each declaring target files, a per-phase
  prompt, and which acceptance test(s) gate that phase.
- Output artifact: a loop-consumable plan (the loop manifest + per-phase
  `workflow.plan.json`) plus a hash-bound planning record linking objective ->
  plan.
- The existing loop consumes the plan unchanged.

## Execution Model

1. Human supplies objective + acceptance test files + target paths.
2. Planner agent emits the phase decomposition (opt-in, LLM, non-deterministic).
3. Deterministic validation (the gate): the emitted plan must (a) compile via
   `compile_workflow`, (b) reference ONLY the declared human acceptance tests as
   verification (no model-authored gate), (c) bound each phase to declared target
   files, (d) cover the acceptance tests across phases. Reject otherwise.
4. The validated plan is handed to the loop (a normal run).

## Path Split (deterministic vs live)

| Path | In keep gate? | Backend |
| --- | --- | --- |
| Plan validation (compiles, references human tests, bounded, covers tests) | Yes | deterministic, no agent |
| Plan generation (planner agent) | No | opt-in LLM |

The keep gate proves the VALIDATOR rejects a bad plan (model-authored gate, won't
compile, unbounded targets, uncovered tests) and accepts a good one — with no
agent, deterministically. Generation stays opt-in/live.

## Safety And Verification Gates

- The validator is the gate; a generated plan that references any
  non-human-declared verification file is REJECTED (the worker can never end up
  authoring its own gate).
- Plan generation is opt-in; the human reviews the generated plan before any loop
  run executes it.
- Reuse the loop's downstream safety (immutable verification, bounded worktree).

## Evaluation Fixtures

Deterministic validator fixtures (no agent):
- a good plan (references the declared human tests, compiles, bounded) -> ACCEPT;
- a plan whose verification points at a non-declared / model-authored file ->
  REJECT;
- a plan that does not compile -> REJECT;
- a plan that leaves an acceptance test uncovered -> REJECT.

## Implementation Plan

1. Plan validator (deterministic): given a plan + the declared human acceptance
   tests + target paths, assert compile + test-reference-only + bounded + covered.
   Joins the keep gate via fixtures above.
2. Planner invocation (opt-in): run the SKILL.md design contract as an agent over
   `objective + tests + targets` to emit the phase decomposition; record a
   hash-bound planning artifact.
3. Wire: `objective + tests -> planner -> validator -> loop`. The first live
   milestone auto-plans one small real task whose human tests already exist, then
   runs the loop on the generated plan.

## Open Questions

- Whether the planner may SUGGEST draft acceptance tests for explicit human
  approval (still human-ratified, not model-trusted) as a later convenience.
- How much decomposition is right (one phase vs many) for a given objective.
- Whether multiple planner attempts are scored/selected (judge panel) before
  validation.
