# V49 Decision

Decision: keep.

V49 implements the first adapter parity matrix. The accepted suite is:

```bash
python scripts/dwm_adapters.py --manifest fixtures/v49/manifest.json --out out/adapters/v49-final
```

The suite records `adapter-parity.json`, `adapter-parity.md`, and `status.json`
for the matrix output. It also proves deterministic blocking for planned-only
Codex run, unsupported shell network capability, unknown adapters, and missing
parity metadata.

This decision does not claim live Codex, Claude, or shell adapter execution. It
does not claim equivalent adapter capability. Planned adapters remain blocked
before live execution until a later adapter contract and smoke evidence prove
auth, isolation, transcript, and verification behavior.
