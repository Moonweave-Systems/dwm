# V35 Live Report Decision

Decision: keep

Command used to regenerate the V35 summary:

```bash
python scripts/dwm_live_report.py --manifest fixtures/v35/manifest.json --out out/live-reports/v35-final
```

Generated summary values:

- `suite_id`: `v35-final`
- `fixture_count`: 7
- `required_fixture_count`: 7
- `required_passed`: 7
- `passed`: 7
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

The accepted V35 suite covers `report.json`, `report.md`,
`ERR_LIVE_REPORT_ARTIFACT_MISSING`, `ERR_LIVE_REPORT_STALE_REVIEW`,
`ERR_LIVE_REPORT_HASH_MISMATCH`, and `ERR_LIVE_REPORT_UNSUPPORTED_CLAIM`.

This decision covers the first live benchmark report gate only. It does not
claim live model execution, live Codex task superiority, Claude superiority,
OpenCode/OMO superiority, hosted evaluation, or external benchmark authority.
