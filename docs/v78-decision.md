# V78 Graph Timing Gate Decision

Decision: keep

Command used:

```bash
python scripts/dwm_graph_timing_gate.py --manifest fixtures/v78/manifest.json --out out/graph-timing/v78-final
```

Generated values:

- `suite_id`: `v78-graph-timing-gate`
- `fixture_count`: 5
- `required_fixture_count`: 5
- `required_passed`: 5
- `passed`: 5
- `failed`: 0
- `decision`: `keep`

V78 keeps graph work honest. It allows process-only visibility when
`dogfood-progress.json` and its SVG evidence are present.
It keeps public benchmark and upward-trend claims blocked behind promotion
evidence.

It does not draw a new graph, edit README assets, publish public benchmark
claims, run queued commands, create worktrees, or execute adapters.
