# V17 Dashboard HUD Decision

Decision: keep

Command used to regenerate the V17 summary:

```bash
python scripts/dwm_hud.py --manifest fixtures/v17/manifest.json --out out/hud/v17-final
```

Generated summary values:

- `suite_id`: `v17-final`
- `fixture_count`: 8
- `required_fixture_count`: 8
- `required_passed`: 8
- `passed`: 8
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

This decision covers the HUD summary and hash-bound approval artifact writer.
It does not claim browser UI rendering, hosted dashboard service, approval of
worker execution, or runtime execution authority.
