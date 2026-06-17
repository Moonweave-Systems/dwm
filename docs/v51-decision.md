# V51 Decision

Decision: keep.

Command used to verify the canonical demo:

```bash
python scripts/dwm_demo.py --manifest fixtures/v51/manifest.json --out out/demo/v51-final
```

The accepted suite covers `demo.json`, `status.json`, `README.md`, unsafe output
blocking, and non-owned output blocking.

This decision does not claim live adapter execution, source mutation, package
publication, external benchmark superiority, or generated demo output as source
truth.
