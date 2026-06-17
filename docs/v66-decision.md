# V66 Decision

Decision: keep.

Command used to verify dogfood process progress graphing:

```bash
python scripts/dwm_dogfood_progress.py --manifest fixtures/v66/manifest.json --out out/dogfood-progress/v66-final
```

The accepted suite covers `dogfood-progress.json`, `dogfood-progress.svg`,
`dogfood-progress.md`, partial progress rendering, full progress rendering, and
stale artifact blocking.

This decision does not claim upward performance, README benchmark promotion,
public benchmark readiness, external benchmark authority, or generated `out/`
directories as source truth.
