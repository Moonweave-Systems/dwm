# V1 First-Slice Compiler Spec

Status: draft
Date: 2026-06-14

## Purpose

V0.5 proved that `dynamic-workflow-designer` can emit deterministic,
schema-valid workflow plans and evaluate them against a tracked fixture corpus.
V1 should close the next practical gap without pretending to be a full workflow
runtime: compile an activated `workflow.plan.json` into one inspectable
first-slice packet plus the files needed to audit, manually hand off, block, or
revalidate that first-slice packet safely.

V1 is a packet compiler, not a runner. It does not execute shell commands,
spawn subagents, advance between phases, or mark work complete. Those behaviors
belong to V2 after the file contract is proven.

## Product Position

| Layer | Responsibility | V1 stance |
| --- | --- | --- |
| `workflow-router` | choose the smallest suitable workflow | unchanged |
| `dynamic-workflow-designer` | design phases, workers, gates, handoffs | source of `workflow.plan.json` |
| V1 first-slice compiler | materialize the first inspectable packet and safety files | implement now |
| Future runtime | durable orchestration, packet advancement, monitoring, subagent scheduling | defer |

V1 should make a workflow easier to start after context loss. It should not
claim Claude Dynamic Workflow-style orchestration. The measurable value is that
another Codex agent can open a run directory, read `README.md`, inspect the
first-slice prompt and packet JSON, see blocked gates, and know whether manual
handoff is safe or blocked.

## Goals

- Accept only activated V0.5 `workflow.plan.json` artifacts.
- Compile the plan's `execution_path.first_slice` into one packet JSON and one
  prompt Markdown file.
- Preserve enough plan graph context to explain where the first slice sits,
  without compiling the whole workflow into runnable packets.
- Emit deterministic gate, handoff, and packet identifiers.
- Store canonical hashes for plan, packet, prompt, first-slice inputs, handoff
  schemas, and approval state.
- Block risky first slices by default with machine-readable approval state.
- Emit structured error codes for every rejected compile, resume-check, and
  self-test case.
- Provide deterministic self-tests and fixtures that fail for weak prompt/packet
  agreement, stale resume state, unsafe output paths, and unapproved risk gates.

## Non-Goals

- Do not automatically spawn subagents.
- Do not execute shell commands from the plan.
- Do not execute validation commands listed in handoff schemas.
- Do not compile all phases into runnable packets.
- Do not maintain `running`, `completed`, or `failed` status.
- Do not implement a viewer, background daemon, or persistent service.
- Do not treat a compiled packet as evidence that workflow work has been done.
- Do not vendor Claude Dynamic Workflow runtimes.

## Scope Boundary

V1 compiles only the first slice:

- Input must be an activated V0.5 plan.
- Downgrade artifacts are rejected. There is no `--allow-downgrade` path in V1.
- Exactly one inspectable packet is generated: `001-first-slice`.
- Later phases, workers, barriers, and handoffs are copied as context and schema
  references, not as runnable packet state.
- `ready` means "safe to hand off manually after reading the packet." It does
  not mean the compiler will run or dispatch it.

V2 owns:

- packet-to-packet advancement
- automatic worker scheduling
- execution evidence ingestion
- status transitions for running/completed/failed work
- durable resume from completed intermediate outputs
- dashboard or viewer

## Command Contract

V1 adds one stdlib-only script:

```bash
python scripts/compile_workflow.py --plan workflow.plan.json --out out/v1/<run_id>
```

Required modes:

```bash
python scripts/compile_workflow.py --plan workflow.plan.json --out out/v1/<run_id> --mode compile
python scripts/compile_workflow.py --resume out/v1/<run_id>
python scripts/compile_workflow.py --manifest fixtures/v1/manifest.json --out out/v1/<suite_id>
python scripts/compile_workflow.py --self-test
```

Mode semantics:

- `--mode compile`: validate the plan, clear or create a fresh run directory,
  write all V1 artifacts, and exit without executing anything.
- `--resume`: read an existing run directory, recompute hashes, update only
  `status.json` and `resume.md`, and exit without executing anything.
- `--manifest`: run a tracked V1 fixture manifest, compile or resume-check each
  fixture in deterministic fixture subdirectories, write
  `out/v1/<suite_id>/summary.json`, and fail if any required fixture is missing,
  skipped, or failed.
- `--self-test`: run positive and negative in-memory cases plus tracked V1
  fixtures once they exist.

There is no `first-slice` execution mode in V1. The first slice is compiled, not
run.

## Output Path Safety

By default, `--out` must resolve under the repository-local `out/v1/` directory.
The compiler must use resolved real paths for containment checks. The same
containment and ownership rules apply to `--resume` before it writes
`status.json` or `resume.md`.

The compiler must reject:

- `.`
- repository root
- `out/`
- `out/v1/`
- paths outside repository-local `out/v1/`
- any symlink in the run-directory path, even if it points inside `out/v1/`
- existing non-directory paths
- existing directories that do not contain `.compile_workflow-owned.json`
- existing directories whose ownership sentinel has a different `run_id` or
  `tool`

The compiler may create a new selected `out/v1/<run_id>` directory. It may
clear and recreate an existing selected run directory only when that directory
contains `.compile_workflow-owned.json` with:

- `tool`: `"compile_workflow.py"`
- `schema_version`: `"1.0"`
- `run_id`: matching the requested run ID

It must not delete any path outside that resolved, compiler-owned run directory.

Future versions may add an explicit unsafe external output override, but V1 does
not include it.

## Generated Artifact Tree

Given an activated plan:

```text
workflow.plan.json
```

The compiler writes:

```text
out/v1/<run_id>/
├── .compile_workflow-owned.json
├── README.md
├── run.json
├── status.json
├── resume.md
├── plan.snapshot.json
├── plan.sha256
├── packets/
│   ├── 001-first-slice.packet.json
│   └── 001-first-slice.prompt.md
├── handoffs/
│   └── <handoff-id>.schema.json
├── gates/
│   ├── approval-state.json
│   └── <gate-id>.approval.md
└── context/
    ├── phases.json
    ├── workers.json
    └── parallelism.json
```

`README.md` is the operator entry point. It must name the packet prompt to read
first, the blocked gates, the allowed next manual action, and the fact that V1
does not execute the workflow. If any packet is `blocked-risk-gate`, the README
must say that V1 has no machine approval path; the operator must return to the
user or wait for V2 tooling before treating the packet as safe to execute.

`.compile_workflow-owned.json` is the deletion sentinel. It must be written as
canonical JSON with these fields:

- `tool`: `"compile_workflow.py"`
- `schema_version`: `"1.0"`
- `run_id`
- `created_at`

## Canonical Hashing

All compiler hashes use SHA-256 over UTF-8 bytes.

Canonical JSON means JSON serialized with sorted object keys, no insignificant
whitespace, LF line endings, and deterministic ordering for arrays whose schema
defines a sort key. Arrays without an explicit sort key keep source order.

Hash preimages:

- `plan_hash`: canonical JSON of `plan.snapshot.json`.
- `prompt_hash`: exact UTF-8 bytes of the generated prompt Markdown after CRLF
  normalization to LF. The prompt must contain the literal placeholder
  `{{PROMPT_SHA256}}`; the compiler does not substitute the prompt hash into the
  prompt body.
- `packet_hash`: canonical packet JSON. Packet JSON includes `prompt_hash` and
  does not include `packet_hash`, so there is no cycle.
- `input_snapshot_hash`: canonical JSON of `input_snapshots`, sorted by
  `input_label`.
- `handoff_schema_hash`: canonical JSON of the handoff schema file.
- `approval_state_hash`: canonical JSON of `gates/approval-state.json`.
- `gate_approval_hash`: canonical JSON of one gate record inside
  `approval-state.json`.

## Deterministic IDs

All IDs are derived from canonical JSON plus source position:

- packet ID: always `001-first-slice`
- handoff ID: `handoff-<zero-padded-index>-<sha8(canonical_handoff_json)>`
- gate ID: `gate-<zero-padded-index>-<sha8(canonical_gate_json)>`
- synthetic gate ID:
  `gate-synthetic-<risk-category>-<sha8(canonical_detection_record)>`

For source handoffs and gates, the source index is the item order in
`workflow.plan.json`; the hash is computed from the canonical JSON object after
sorting object keys. Reordering handoffs or gates is therefore a semantic change
for V1 resume purposes and invalidates related snapshots.

Synthetic gates are generated only for detected risk categories that do not have
a matching source gate. Their detection record must include `risk_category`,
`source_field`, `source_id`, and `normalized_token`.

## Validation Interface

`compile_workflow.py` must validate plans by importing the existing stdlib
validator function from `scripts/evaluate_plan.py`:

```python
from evaluate_plan import EvaluationError, validate_plan
```

The compiler must call `validate_plan(plan)` before generating artifacts. It
must not shell out to `evaluate_plan.py` for validation, and it must not duplicate
the V0.5 schema rules.

If `evaluate_plan.py` changes its public validation function, this spec and the
compiler must be updated in the same change.

## `run.json`

Required fields:

- `run_id`
- `schema_version`: `"1.0"`
- `created_at`
- `source_plan_path`
- `plan_hash`
- `compiler_version`
- `mode`: `"compile"`
- `risk_policy`: `"block-all"`
- `status_path`
- `packet_paths`
- `approval_state_path`

`risk_policy` is fixed to `block-all` in V1. Approved execution is outside V1;
approval files exist only to make manual gates explicit and machine-checkable.
`run.json` is immutable after compile. `--resume` must not edit `run.json`; it
records its result only in `status.json` and `resume.md`.

## `status.json`

Required fields:

- `run_id`
- `plan_hash`
- `resume_state`: `fresh`, `resumable`, or `invalidated`
- `packet_statuses`
- `handoff_statuses`
- `gate_statuses`
- `snapshots`
- `invalidators`
- `last_resume_checked_at`: timestamp or `null`
- `last_resume_result`: `null`, `resumable`, or `invalidated`

`snapshots` schema:

- `plan_hash`
- `packet_hashes`: object keyed by packet ID
- `prompt_hashes`: object keyed by prompt path
- `input_snapshot_hashes`: object keyed by packet ID
- `handoff_schema_hashes`: object keyed by handoff ID
- `approval_state_hash`
- `gate_approval_hashes`: object keyed by gate ID
- `compiler_version`

Packet status schema:

- `packet_id`
- `status`: `ready`, `blocked-risk-gate`, or `invalidated`
- `reason`
- `packet_hash`
- `prompt_hash`
- `input_snapshot_hash`
- `gate_snapshot_hash`

Handoff status schema:

- `handoff_id`
- `schema_hash`
- `source_index`

Gate status schema:

- `gate_id`
- `trigger`
- `status`: `blocked`, `not-required`, or `invalidated`
- `approval_hash`
- `source`: `plan` or `compiler-synthetic`
- `source_index`: integer or `null`
- `risk_category`

V1 status never records `running`, `completed`, or `failed`. Those states require
execution evidence and belong to V2.

## Packet JSON

`packets/001-first-slice.packet.json` required fields:

- `packet_id`: `001-first-slice`
- `source_plan_id`
- `source_first_slice`
- `objective`
- `surface_refs`
- `phase_context`
- `worker_refs`
- `allowed_tools`
- `forbidden_actions`
- `risk_gate_refs`
- `handoff_refs`
- `verification`
- `completion_check`
- `input_snapshots`
- `input_snapshot_hash`
- `prompt_contract`
- `prompt_path`
- `prompt_hash`

`phase_context` must include phase IDs, `depends_on`, and whether a phase is
included for context only. `worker_refs` can list multiple workers; V1 must not
collapse multi-worker phases into a single `worker_id`.

First-slice derivation is deliberately conservative:

- `source_first_slice` is exactly `execution_path.first_slice` from the source
  plan.
- V1 does not infer that one phase or worker owns the first slice.
- `phase_context` includes every source phase in original order with
  `context_only: true`.
- `worker_refs` includes every source worker in original order with
  `context_only: true`.
- `handoff_refs` includes every generated handoff ID in source order with
  `context_only: true`.
- `risk_gate_refs` includes every generated gate ID in source order; status
  decides whether each gate is required for this packet.

This avoids fabricating executable assignment semantics that do not exist in the
V0.5 plan schema.

`input_snapshots` schema:

- `input_label`
- `input_kind`: `literal`, `path`, `glob`, `url`, or `unknown`
- `normalized_value`
- `hash`
- `exists_at_compile_time`
- `snapshot_entries`

V0.5 first-slice inputs are arbitrary labels, so V1 treats all inputs as
`literal` unless they match one of these deterministic recognizers:

- `workflow.plan.json`: the source plan path.
- `blueprint.md`: a sibling blueprint path if one exists; otherwise literal.
- `original prompt`: the source prompt text when available; otherwise literal.
- `repository path`: the repository root path.
- strings beginning with `path:`: path input after trimming the prefix.
- strings beginning with `glob:`: glob input after trimming the prefix.

For `literal` and `url` inputs, `snapshot_entries` contains one record with the
normalized value and its hash. For `path` inputs, `snapshot_entries` contains one
record `{ "path", "exists", "sha256" }`; `sha256` is `null` when the path is
missing or is a directory. Directories are not recursively hashed in V1 and must
be called out in `resume.md`. For `glob` inputs, the compiler expands matching
files, sorts them by POSIX-style relative path, and hashes canonical JSON of
records `{ "path", "exists", "sha256" }`. Bare directories inside a glob result
are recorded with `sha256: null`.

## Packet Prompt

`packets/001-first-slice.prompt.md` must use these exact headings:

```markdown
# Packet 001-first-slice
## Objective
## Inputs
## Ownership
## Allowed Tools
## Forbidden Actions
## Risk Gates
## Required Output
## Verification
## Handoff Context
## Stop Conditions
```

The prompt must include the packet ID, source plan ID, prompt hash placeholder,
all forbidden actions, all referenced gate IDs, and the completion check. The
compiler must verify prompt/packet agreement structurally by checking these
heading sections and mirrored IDs, not by loose substring search alone.

The prompt must also include one fenced JSON block under `## Handoff Context`
with info string `packet_contract_digest`. The compiler parses this block and
compares it against packet JSON before writing final artifacts.

Required digest fields:

- `packet_id`
- `source_plan_id`
- `objective`
- `input_snapshot_hash`
- `allowed_tools`
- `forbidden_actions`
- `risk_gate_refs`
- `handoff_refs`
- `verification`
- `completion_check`

The digest values must equal the corresponding packet JSON values after
canonical JSON normalization. Mismatch is a compile failure with
`ERR_PROMPT_PACKET_DRIFT`.

## Approval State

`gates/approval-state.json` is canonical. Markdown files are human-readable
views only.

Required top-level fields:

- `run_id`
- `plan_hash`
- `risk_policy`: `"block-all"`
- `gates`

Each gate record requires:

- `gate_id`
- `trigger`
- `risk_category`
- `source`: `plan` or `compiler-synthetic`
- `safe_default`
- `requires_user_approval`
- `status`: `blocked` or `not-required`
- `approved`: `false`
- `approval_source`: `null`

V1 never treats hand-edited Markdown as approval. Even if a user edits
`*.approval.md`, `approval-state.json` remains blocked unless a future V2 command
changes it. This avoids surprising execution behavior.

## Risk Model

The compiler uses a closed risk category vocabulary:

- `write`
- `shell-process`
- `network`
- `dependency-install`
- `database-migration`
- `production-deploy`
- `public-api-change`
- `external-message`
- `paid-api`
- `secret-access`
- `history-rewrite`
- `delete`

Risk detection uses only structured source fields and exact normalized tokens.
Normalization lowercases text and treats spaces, underscores, and hyphens as the
same separator. It must not use broad prose substring search.

Structured risk sources:

- `surfaces[].access_mode` other than `read-only` maps to `write`.
- `workers[].tool_permissions.write: true` maps to `write`.
- `workers[].tool_permissions.shell: true` maps to `shell-process`.
- `workers[].tool_permissions.network: true` maps to `network`.
- non-empty `workers[].tool_permissions.mcp_connectors` maps to
  `external-message` unless the connector is explicitly read-only in the plan.
- `workers[].tool_permissions.requires_escalation_for[]` tokens map to the risk
  vocabulary.
- `risk_gates[].trigger` tokens map to the risk vocabulary.
- `execution_path.first_slice.instruction`,
  `execution_path.first_slice.expected_output`, and
  `execution_path.first_slice.completion_check` are scanned only for exact
  normalized risk tokens from the vocabulary.

A source gate matches a detected category only when its normalized `trigger`
contains the exact normalized category token. Otherwise the detected category
requires a synthetic gate.

If any structured source maps to a risk category, packet status is
`blocked-risk-gate` and at least one gate status must be `blocked`. If the plan
does not contain a matching source gate for a detected category, the compiler
must emit a synthetic blocked gate for that category. Otherwise packet status is
`ready` and all gate statuses are `not-required`.

V1 has no approval command. A blocked packet remains blocked even if a human
edits Markdown approval notes.

## Resume Check

`--resume out/v1/<run_id>` recomputes:

- plan hash from `plan.snapshot.json`
- packet JSON hash
- prompt hash
- input snapshot hash
- handoff schema hashes
- approval-state hash

It then updates only `status.json` and `resume.md`.

Resume outcomes:

- `resumable`: all stored hashes match recomputed hashes
- `invalidated`: any hash differs, any required artifact is missing, or the
  current compiler version cannot parse the run

`invalidators` must be a list of structured records:

- `kind`: `plan`, `packet`, `prompt`, `input`, `handoff`, `gate`, or `compiler`
- `id`
- `code`
- `expected_hash`
- `actual_hash`
- `message`

V1 does not resume completed work. It only tells the operator whether the
compiled first-slice packet is still trustworthy.

Required resume invalidator codes:

- `ERR_RESUME_STALE_PLAN`
- `ERR_RESUME_STALE_PACKET`
- `ERR_RESUME_STALE_PROMPT`
- `ERR_RESUME_STALE_INPUT`
- `ERR_RESUME_STALE_HANDOFF`
- `ERR_RESUME_STALE_GATE`
- `ERR_RESUME_STALE_COMPILER`
- `ERR_RESUME_MISSING_ARTIFACT`

## Compile Errors

Compile and fixture failures must be structured as `CompileError` records:

- `code`
- `message`
- `path`: optional source or output path
- `fixture_id`: optional fixture ID

Required error codes:

- `ERR_PLAN_DOWNGRADE`: input is a downgrade artifact, not an activated plan.
- `ERR_PLAN_INVALID`: V0.5 plan validation failed.
- `ERR_OUT_PATH_UNSAFE`: output or resume path is outside the allowed V1 area or
  is a forbidden root.
- `ERR_OUT_PATH_SYMLINK`: any path component in the run-directory path is a
  symlink.
- `ERR_OUT_PATH_NOT_OWNED`: existing run directory lacks a matching ownership
  sentinel.
- `ERR_PROMPT_PACKET_DRIFT`: prompt digest and packet JSON disagree.
- `ERR_RISK_GATE_BLOCKED`: fixture expected a ready packet but the compiler
  correctly blocked a risk gate, or a fixture expected a blocked gate that was
  not blocked.
- `ERR_RESUME_STALE_PLAN`
- `ERR_RESUME_STALE_PACKET`
- `ERR_RESUME_STALE_PROMPT`
- `ERR_RESUME_STALE_INPUT`
- `ERR_RESUME_STALE_HANDOFF`
- `ERR_RESUME_STALE_GATE`
- `ERR_RESUME_STALE_COMPILER`
- `ERR_RESUME_MISSING_ARTIFACT`
- `ERR_SELF_TEST_WRONG_REASON`: a negative self-test failed, but not for the
  expected code.

## Evaluation

Add fixtures under `fixtures/v1/` when the compiler exists.

Minimum fixture set:

- positive: activated repo-wide migration compiles first-slice packet
- positive: read-only research plan compiles ready first-slice packet
- negative: downgrade artifact is rejected
- negative: output path outside `out/v1/<run_id>` is rejected
- negative: symlink escape from `out/v1/` is rejected
- risk: one fixture for each closed risk category becomes `blocked-risk-gate`
- drift: prompt/packet mismatch is rejected by self-test
- resume: untouched run remains `resumable` with empty `invalidators`
- resume: modified plan hash invalidates run
- resume: modified packet hash invalidates run
- resume: modified prompt hash invalidates run
- resume: modified input snapshot invalidates run
- resume: modified gate approval-state hash invalidates run
- resume: missing handoff schema invalidates run

Each fixture must validate:

- generated file set
- deterministic IDs
- status values
- blocked risk gates
- prompt/packet structural agreement
- resume invalidation reasons
- exact `CompileError.code` or invalidator `code`

`fixtures/v1/manifest.json` must list required fixture IDs explicitly. Fixture
IDs must be unique. A skipped fixture is a failure. The manifest run writes
`out/v1/<suite_id>/summary.json`.

## Self-Test Requirements

`scripts/compile_workflow.py --self-test` must include:

- one valid activated plan compile
- downgrade rejection
- unsafe output path rejection
- symlink escape rejection
- one blocked gate case for each closed risk category
- prompt/packet drift failure
- clean resume returns `resumable`
- stale plan hash resume failure
- stale packet hash resume failure
- stale prompt hash resume failure
- stale input hash resume failure
- stale gate hash resume failure
- missing handoff schema resume failure

The self-test must fail for the exact reason under test. It must not count a
failure caused by an unrelated missing required field as a pass.

## Decision Gate

The compiler must write `out/v1/<suite_id>/summary.json` for manifest runs with:

- `suite_id`
- `fixture_count`
- `passed`
- `failed`
- `skipped`
- `decision`: `keep` or `kill`
- `failures`

`docs/v1-decision.md` may record `keep` only when all required V1 fixtures pass,
all existing V0/V0.5 release checks still pass, and the generated summary has
`decision: "keep"`. The decision doc must name the exact manifest command used
to regenerate the summary.

## Acceptance Criteria

V1 is releasable when:

- `scripts/compile_workflow.py --self-test` passes.
- `python scripts/compile_workflow.py --manifest fixtures/v1/manifest.json --out
  out/v1/<suite_id>` passes and writes `summary.json`.
- Existing V0/V0.5 checks still pass.
- Required V1 fixtures pass through the compiler.
- Generated packet prompts structurally agree with packet JSON.
- Risky first slices are blocked in `approval-state.json` and `status.json`.
- Resume checks invalidate stale plan, prompt, input, handoff, gate, or compiler
  state.
- README documents compile and resume-check commands.
- `docs/v1-decision.md` records keep/kill from `summary.json`.

## Implementation Slices

1. Add `scripts/compile_workflow.py --self-test` with plan validation, activated
   plan enforcement, output path safety, and deterministic hashing.
2. Generate `run.json`, `plan.snapshot.json`, `plan.sha256`, `README.md`, and
   `status.json` from one activated V0.5 sample plan.
3. Generate `001-first-slice.packet.json` and `001-first-slice.prompt.md` with
   structural prompt/packet agreement checks.
4. Generate deterministic handoff schemas and `approval-state.json`.
5. Add risk-gate blocking for first-slice forbidden actions, shell/process
   execution, and risky worker permissions.
6. Add `--resume` mode that validates hashes and writes structured
   invalidators.
7. Add V1 fixtures, fixture summary generation, and `docs/v1-decision.md`.
8. Update `SKILL.md` only if the compiler changes the expected output contract.

## Open Questions

- Should V2 add a command that writes approvals into `approval-state.json`, or
  should approvals remain outside the local compiler forever?
- Should V2 compile all phase-worker pairs into packets, or should it require a
  V1.1 schema bump that adds packet IDs directly to `workflow.plan.json`?
- Should V2 introduce a viewer, or is textual `README.md` plus `status.json`
  enough for one more measured step?
