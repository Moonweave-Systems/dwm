# V47 Real Dogfood Corpus Decision

Decision: keep

Command used to regenerate the V47 summary:

```bash
python scripts/dwm_dogfood_corpus.py --manifest fixtures/v47/manifest.json --out out/dogfood-corpus/v47-final
```

Generated summary values:

- `suite_id`: `v47-final`
- `fixture_count`: 5
- `required_fixture_count`: 5
- `required_passed`: 5
- `passed`: 5
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

The accepted V47 suite covers `dogfood-corpus.json`, `queue-packets.json`,
linked V46 `queue.json`, `ERR_DOGFOOD_CORPUS_REQUIRED_TASK_MISSING`,
`ERR_DOGFOOD_CORPUS_UNSAFE_TASK`, `ERR_DOGFOOD_CORPUS_PUBLIC_CLAIM`, and
`ERR_DOGFOOD_CORPUS_EVIDENCE_MISSING`.

This decision covers local dogfood corpus recording only. It does not execute
attempts, claim external benchmark authority, publish README graphs, or treat
`not-run` comparison slots as results.
