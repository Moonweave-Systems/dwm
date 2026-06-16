# V17 Dashboard HUD Decision

Decision: keep

Command used to regenerate the V17 summary:

```bash
python scripts/dwm_hud.py --manifest fixtures/v17/manifest.json --out out/hud/v17-final
```

Generated summary values:

- `suite_id`: `v17-final`
- `fixture_count`: 4
- `required_fixture_count`: 4
- `required_passed`: 4
- `passed`: 4
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

This decision covers the read-only HUD summary only. It does not claim browser
UI rendering, approval artifact writing, hosted dashboard service, or runtime
execution authority.
