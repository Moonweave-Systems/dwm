# V33 Live Score Aggregate Decision

Decision: keep

Command used to regenerate the V33 summary:

```bash
python scripts/dwm_live_score_aggregate.py --manifest fixtures/v33/manifest.json --out out/live-score-aggregates/v33-final
```

Generated summary values:

- `suite_id`: `v33-final`
- `fixture_count`: 7
- `required_fixture_count`: 7
- `required_passed`: 7
- `passed`: 7
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

The accepted V33 suite covers `aggregate-score.json`,
`ERR_LIVE_SCORE_AGGREGATE_ARTIFACT_MISSING`,
`ERR_LIVE_SCORE_AGGREGATE_STALE_SCORE`,
`ERR_LIVE_SCORE_AGGREGATE_TASK_MISSING`,
`ERR_LIVE_SCORE_AGGREGATE_TASK_DUPLICATE`, and
`ERR_LIVE_SCORE_AGGREGATE_UNSUPPORTED_CLAIM`.

This decision covers aggregate live score evidence only. It does not claim live
model execution, live Codex task success, Claude execution, OpenCode/OMO
execution, hosted evaluation, adversarially reviewed benchmark scoring, or
benchmark success.
