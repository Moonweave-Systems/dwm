# V51 Canonical Demo Spec

Status: implemented first canonical demo in `scripts/dwm_demo.py`.

## Research and Prior Art

The repo now has a broad set of deterministic surfaces, but new users still need
one command that shows the product loop without reading every V-numbered spec.
V51 turns the V49/V50 review feedback into a source-bound local demo.

## Product Position and Non-Goals

V51 is a deterministic demo runner. It demonstrates DWM's artifact-first product
path without executing live adapters or mutating source files.

Non-goals:

- do not run live Codex, Claude, or shell adapters,
- do not publish a package or GitHub release,
- do not edit tracked benchmark assets,
- do not claim direct-agent superiority,
- do not make the demo output a source of truth.

## Workflow Architecture

`scripts/dwm_demo.py run` writes:

- `demo.json`,
- `status.json`,
- `README.md`.

The demo runs deterministic local commands:

- product-shell plan request,
- first-slice compiler fixture,
- one-packet review fixture,
- adapter parity matrix,
- dogfood corpus,
- daily operator loop,
- release candidate cut.

## Execution Model

```bash
python scripts/dwm_demo.py run --out out/demo/<demo_id>
python scripts/dwm_demo.py --manifest fixtures/v51/manifest.json --out out/demo/v51-final
```

Every demo output directory is guarded by a demo ownership sentinel. Child
artifacts are written under their existing owned `out/` roots.

## Safety and Verification Gates

The gate blocks:

- `ERR_DEMO_PATH_UNSAFE` when output paths escape `out/demo/` or reuse a
  non-owned directory,
- `ERR_DEMO_PATH_SYMLINK` when the output path contains symlinks,
- `ERR_DEMO_COMMAND_FAILED` when a deterministic demo command fails.

## Evaluation Fixtures

`fixtures/v51/manifest.json` covers:

- positive: canonical demo creates `demo.json`, `status.json`, and `README.md`,
- negative: unsafe output root is blocked,
- negative: non-owned output directory is blocked.

## Release Plan

V51 makes README Quickstart point to one concrete demo command. Later README
work can further move internal command lists below the user-facing demo and
normal loop.
