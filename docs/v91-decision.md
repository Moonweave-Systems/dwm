# V91 Decision

Decision: keep.

Commands used to verify release-contract tiering:

```bash
python scripts/check_contract.py --self-test
python scripts/check_contract.py --tier smoke
python scripts/check_contract.py --tier changed
```

Generated values:

- `smoke`: pass
- `changed`: pass
- `full_default`: preserved by `python scripts/check_contract.py`
- `decision`: `keep`

This decision makes iterative verification faster without treating smoke or
changed tiers as publish approval. Full release verification remains the
publish boundary.
