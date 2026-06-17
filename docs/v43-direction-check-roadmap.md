# V43 Direction Check And Forward Roadmap

Status: direction checkpoint written after V42 benchmark candidate workflow.

## Objective

Decide whether DWM is still moving in a meaningful direction, then lock the
next roadmap so later benchmark graphs reflect real product value instead of
decorative upward lines.

## Current Judgment

DWM is still on a useful path.

The reason is not that the repo has many versions or a polished README. The
reason is that the product has been moving toward a hard control-plane boundary:
plans, packets, adapter commands, receipts, reviews, scores, histories, and
publish candidates are artifacts that can be checked independently of model
claims.

That direction is valuable because modern agent tools tend to converge on the
same operator needs:

- durable local state,
- clear next actions,
- bounded execution,
- review and repair loops,
- replayable evidence,
- safe parallelism,
- honest benchmark reporting.

DWM should not try to win by being a larger agent launcher. It should win by
being the deterministic layer that makes existing launchers, CLIs, and adapters
safer to use on large work.

## Evidence So Far

Implemented surface:

- V0-V3 established workflow design, compilation, execution evidence, review,
  repair preparation, and runtime entry.
- V4-V9 added scheduler, dispatch, worker result review, frontier ingestion,
  and human gate resolution.
- V10-V22 turned the research prototype into a product shell with operator
  guidance, runner/session support, HUD, install checks, adapter registry,
  release gates, role contracts, and dogfood replay.
- V23-V36 created the benchmark and live-evidence path from task materialization
  through graph-ready report artifacts.
- V37-V42 made the public README benchmark path harder to fake: graph artifacts,
  history ledger, promotion gate, release snapshots, ordered series, and a
  pre-publish candidate.

What this proves:

- DWM can represent work as deterministic artifacts.
- DWM can block stale, unsafe, or unsupported claims.
- DWM can prepare graph evidence without manually editing README numbers.
- DWM has enough structure to compare future runs against direct-agent baselines.

What this does not prove yet:

- DWM is better than direct Codex on real user tasks.
- DWM improves throughput on a multi-day project.
- DWM reduces human interruptions in normal use.
- DWM's published graph should be an external benchmark claim.
- DWM has a finished plugin/runtime distribution experience.

## Directional Risks

| Risk | Current state | Required response |
| --- | --- | --- |
| Too much scaffolding, not enough daily use | V42 closes a benchmark-candidate path but does not yet make the user loop effortless | Next slices must reduce operator friction |
| Benchmark theater | Graph pipeline exists before enough real longitudinal data | Keep promotion gates strict and label charts as repo-local evidence |
| Harness clone drift | Adapter surfaces can tempt the repo into becoming a generic launcher | Keep DWM as the artifact control-plane above adapters |
| Spec drift | Docs can sound ahead of runtime | Every roadmap claim needs a command, fixture, or explicitly deferred status |
| Human fatigue | User should not have to keep nudging every tiny step | Add next-action queues and long-run workflow packets |

## Product North Star

DWM should become the local control-plane that lets a user say:

```text
Use the workflow designer to carry this large repo task forward.
```

and then receive:

- a deterministic plan,
- safe first packets,
- bounded execution commands,
- review and repair loops,
- evidence-backed next actions,
- human gates only when risk is real,
- benchmark snapshots that can become honest public graphs.

## Next Roadmap

### V43: Direction Check And Forward Roadmap

Status: this document.

Done means:

- the direction is judged against runtime evidence, not product narrative;
- the remaining gaps are explicit;
- the next roadmap is ordered by user value and benchmark integrity;
- the workflow plan is captured in `docs/v43-direction-check-roadmap.workflow.plan.json`.

### V44: Publish Candidate Review Gate

Purpose: review a V42 benchmark candidate before any tracked README asset is
changed.

Done means:

- read a candidate directory;
- verify candidate, promotion, series, history, and report hashes;
- write `candidate-review.json`;
- block external superiority claims;
- emit a human-readable publish checklist;
- fixture covers ready, stale candidate, missing promotion, overclaim text, and
  insufficient review evidence.

### V45: README Asset Promotion

Purpose: promote an approved candidate into tracked README graph assets.

Done means:

- copy or regenerate only approved graph assets;
- update README snippet from candidate evidence;
- preserve source hash metadata;
- refuse stale candidate review;
- produce a diff summary for human review before commit.

### V46: Long-Run Workflow Queue

Purpose: let DWM continue through a multi-step roadmap without constant user
nudges while still stopping at real gates.

Done means:

- write a queue artifact with ordered roadmap packets;
- mark packet status as pending, ready, blocked, done, or superseded;
- resume from the next safe packet;
- stop only for missing evidence, unsafe action, failing verification, or human
  approval.

### V47: Real Dogfood Task Corpus

Purpose: move benchmark evidence from synthetic fixtures toward real repo work.

Done means:

- define a small corpus of actual DWM maintenance tasks;
- run direct Codex and DWM-controlled paths when safe;
- record time, commands, files touched, verification, interruptions, and review
  findings;
- label results as local dogfood, not external benchmark authority.

### V48: Daily Operator Loop

Purpose: make the product useful outside release tests.

Done means:

- `dwm next` can summarize the next safe action across current runs;
- `dwm status` can show blocked gates and evidence freshness;
- operator docs explain one normal daily loop;
- no benchmark claim is required to use the product.

### V49: Adapter Parity Matrix

Status: first parity matrix implemented in `scripts/dwm_adapters.py`.

Purpose: keep Codex, Claude, shell, and fixture adapter support honest.

Done means:

- document each adapter's supported actions, unsupported actions, auth
  assumptions, isolation behavior, and evidence fields;
- fixtures prove unsupported adapters fail deterministically;
- docs avoid implying equivalent capability where parity does not exist.

### V50: Release Candidate Cut

Purpose: make the next public release based on actual operator value.

Done means:

- full contract passes;
- README reflects implemented surfaces only;
- benchmark graphs are included only if V44-V45 approve them;
- release notes separate implemented, experimental, and deferred capabilities.

## Workflow Design

Patterns:

- Sequential for V43-V45 because publish integrity depends on prior artifacts.
- Pipeline for V46-V48 because roadmap packets can move independently once
  queued.
- Adversarial Verify for benchmark and README claims.
- Human Gate for tracked README asset changes and public release claims.
- Resume And Cache for long-run roadmap execution.

Workers:

- `direction_auditor`: compares roadmap claims against implemented commands and
  artifacts.
- `roadmap_planner`: orders next slices by user value and evidence integrity.
- `claim_reviewer`: blocks unsupported benchmark and README claims.
- `operator_verifier`: runs release checks and records command evidence.

Handoffs:

- `direction-check.md` from auditor to planner;
- `roadmap.json` from planner to queue implementation;
- `candidate-review.json` from reviewer to README promotion;
- `verification-log.md` from verifier to release decision.

Risk gates:

- README asset changes require an approved candidate review.
- External benchmark claims require real comparable runs and clear labels.
- Adapter execution beyond deterministic fixtures requires the normal DWM
  safety gates.
- Long-run queue execution must stop on unsafe actions, credentials, network,
  dependency installation, or public release steps.

## Success Criteria

DWM is moving in the right direction if the next ten slices increase one of
these measurable properties:

- fewer unsupported claims,
- fewer repeated user nudges for safe next steps,
- more real tasks captured as evidence,
- clearer blocked reasons,
- faster recovery after interruption,
- stricter separation between local evidence and public claims.

It is drifting if the next work mostly adds names, diagrams, versions, or graph
polish without making a real run easier to execute, verify, resume, or publish
honestly.
