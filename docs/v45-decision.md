# V45 README Asset Promotion Decision

Decision: keep

Command used to regenerate the V45 summary:

```bash
python scripts/dwm_readme_asset_promotion.py --manifest fixtures/v45/manifest.json --out out/readme-asset-promotions/v45-final
```

Generated summary values:

- `suite_id`: `v45-final`
- `fixture_count`: 6
- `required_fixture_count`: 6
- `required_passed`: 6
- `passed`: 6
- `failed`: 0
- `skipped`: 0
- `decision`: `keep`

The accepted V45 suite covers `asset-promotion.json`, `asset-diff.md`,
`README-snippet.md`, `ERR_README_ASSET_PROMOTION_STALE_REVIEW`,
`ERR_README_ASSET_PROMOTION_ASSET_MISSING`,
`ERR_README_ASSET_PROMOTION_HASH_MISMATCH`,
`ERR_README_ASSET_PROMOTION_REVIEW_NOT_APPROVED`, and
`ERR_README_ASSET_PROMOTION_OVERCLAIM`.

This decision covers a reviewable README asset promotion bundle only. It does
not edit tracked README assets, commit assets, claim external benchmark
authority, claim model superiority, or perform autonomous release.
