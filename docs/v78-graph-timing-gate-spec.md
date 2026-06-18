# V78 Graph Timing Gate Spec

Status: implemented graph timing gate in `scripts/dwm_graph_timing_gate.py`.

V78 answers the graph timing question without forcing a new graph. It classifies
three graph surfaces:

- `process_progress`: local visibility of process completion and evidence
  collection state.
- `local_benchmark_candidate`: reviewed local candidate evidence that can be
  inspected, but not promoted as a public claim.
- `public_benchmark_trend`: a public upward benchmark graph. This remains
  blocked until promotion evidence exists.

## Scope

The gate reads existing artifacts from `out/`:

- `dogfood-progress.json`
- `graph-readiness.json`
- `queue-preflight.json`

It writes `graph-timing.json`, `graph-timing.md`, `status.json`, and manifest
`summary.json` under `out/graph-timing/`. It does not draw a new graph, edit
README assets, publish public claims, execute queued commands, create
worktrees, or run adapters.

## Safety Policy

Process progress may be visible only with the safe label
`Process progress, not benchmark performance`. A process progress artifact with
`public_readme_ready: true` is treated as an overclaim unless a separate public
promotion receipt exists.

The public benchmark trend is blocked by default with
`ERR_GRAPH_TIMING_PUBLIC_PROMOTION_MISSING`. Missing process progress,
incomplete pair-series readiness, or stale queue preflight add explicit blocker
codes. This keeps the README from showing a fake upward trend while still
allowing honest process visibility.

## Evaluation Fixtures

`fixtures/v78/manifest.json` covers:

- ready process progress producing `progress-only-visible`;
- missing process progress blocking all graph visibility;
- process progress overclaim blocking visibility;
- insufficient benchmark readiness still allowing process progress visibility;
- missing preflight keeping public benchmark promotion blocked.

The fixture suite materializes its own SVG evidence so it does not depend on
generated `out/` state.

## Release Commands

```bash
python scripts/dwm_graph_timing_gate.py --self-test
python scripts/dwm_graph_timing_gate.py --manifest fixtures/v78/manifest.json --out out/graph-timing/v78-final
python scripts/dwm_graph_timing_gate.py check --progress out/dogfood-progress/local-v66-current/dogfood-progress.json --readiness out/dogfood-pair-series/local-v64-selected-series/graph-readiness.json --preflight out/large-workflow-queue-preflight/v77-canonical/queue-preflight.json --out out/graph-timing/v78-canonical
```

The canonical check should produce `decision: progress-only-visible` until a
real benchmark promotion gate exists.
