# V71 Decision

Decision: keep.

Command used to verify release timing:

```bash
python scripts/dwm_release_timing.py --manifest fixtures/v71/manifest.json --out out/release-timing/v71-final
```

Generated values:

- `suite_id`: `v71-release-timing`
- `fixture_count`: 3
- `required_passed`: 3
- `decision`: `keep`
- `artifacts`: `release-timing.json`, `release-timing.md`, `status.json`, `summary.json`

This decision covers release command inventory, bounded measurement, timeout blocking, source hash recording, and operator-readable timing output. It does not claim the full release corpus is fast and does not publish an upward benchmark claim.
