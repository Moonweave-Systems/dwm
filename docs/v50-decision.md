# V50 Decision

Decision: keep.

Command used to verify the release candidate cut:

```bash
python scripts/dwm_release_candidate.py --manifest fixtures/v50/manifest.json --out out/release-candidates/v50-final
```

The accepted suite covers `release-candidate.json`, `release-notes.md`,
`release-checklist.md`, missing parity, stale parity, stale operator loop, and
unsupported release-note overclaims.

This decision does not claim a hosted release, package publication, README asset
mutation, external benchmark superiority, live adapter execution, or full
autonomous runtime behavior.
