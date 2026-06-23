# Keelplane V105 Final Design and Native Agent Pack

This bundle is the corrected, transplant-ready proposal for Keelplane's next
slice.

```text
Codex / Claude Code
  own model execution, tools, sessions, permissions, sandboxes, and worktrees

Keelplane reference profiles
  define a small team and portable handoff contracts

Keelplane capture / adapters
  observe or import execution facts with an explicit trust origin

Keelplane Core
  validates plans, evaluates evidence policy, and renders decision + assurance
```

The central correction is simple: **agents do not certify their own work**.
Agent outputs are claims. Deterministic capture, independent checks, and explicit
provenance determine what can be trusted.

## Read in this order

1. `AUDIT-KO.md` — full Korean audit of philosophy, direction, design gaps, and omissions.
2. `FINAL-REVIEW.md` — validation record and remaining limitations.
3. `docs/product-direction-v105.md` — upstream-ready product specification.
4. `docs/threat-model-v1.md` — trust boundaries and attacks.
5. `docs/evidence-protocol-v1.md` — evidence, provenance, assurance, and seal.
6. `docs/agent-team-spec-v1.md` — minimal effective agent-team contract.
7. `docs/evaluation-spec-v1.md` — how to prove real productivity and quality value.
8. `docs/implementation-roadmap.md` — small vertical implementation order.
9. `docs/integration-guide-ko.md` — practical transplant instructions.
10. `docs/upstream-gap-map.md` — file-by-file Keelplane change map.
11. `docs/ecosystem-positioning.md` — what to integrate with instead of rebuilding.

## Included assets

- Six Codex custom agents under `packs/codex/.codex/agents/`.
- Seven Claude Code subagents under `packs/claude/.claude/agents/`, including an
  optional worktree implementer.
- Safe project instruction and configuration fragments.
- Five execution profiles.
- Ten JSON Schemas for profiles, compile/run contracts, events, results,
  receipts, reviews, gates, manifests, and seals.
- Ready-to-paste orchestration prompts and sample records.
- A non-destructive project-scoped installer.
- A standard-library-only local A1 evidence-capture reference tool.
- A seal verifier, structural validator, and six integration/security tests.

No exact model IDs, API keys, provider routes, global settings, third-party MCP
servers, or permission-bypass modes are installed.

## Validate

Runtime/reference tools use only the Python standard library. Full schema tests
use `jsonschema` as a development dependency.

```bash
python -m pip install -r requirements-dev.txt
python tools/validate_bundle.py
python -m unittest discover -s tests -v
```

## Install into another repository

```bash
python tools/install_pack.py \
  --target /path/to/repository \
  --harness both \
  --dry-run

python tools/install_pack.py \
  --target /path/to/repository \
  --harness both
```

The installer does not overwrite root `AGENTS.md`, root `CLAUDE.md`, existing
agent definitions, `.codex/config.toml`, or Claude settings. Merge fragments are
staged under `.keelplane/install-fragments/`, and an install receipt is written.
Modified managed files are preserved during uninstall.

## Local evidence capture prototype

```bash
python tools/capture_local.py \
  --repo /path/to/repository \
  --plan /path/to/workflow.plan.json \
  --run-id auth-fix-001 \
  --harness codex \
  --out /path/to/repository/.keelplane/runs/auth-fix-001/attempt-01

python tools/verify_seal.py \
  /path/to/repository/.keelplane/runs/auth-fix-001/attempt-01
```

This produces **A1-local-observed** evidence. The seal detects post-capture byte
changes; it does not prove provider identity, command process custody, or resist
a malicious local administrator.

## Recommended first profile

Use `feature-pipeline` for a nontrivial one-writer task:

```text
lead
  -> explorer
  -> one implementer
  -> test verifier + fresh code reviewer
  -> conditional security/adversarial reviewer
  -> deterministic Keelplane capture
```

Use `direct-small-fix` when a team would add more coordination than value.
Use `cross-harness-review` for a medium/high-risk change when both Codex and
Claude Code are available.

## Status

This is a specification, reference pack, schemas, and prototype tooling. It is
not an upstream patch and makes no productivity claim until the paired
evaluation in `docs/evaluation-spec-v1.md` is run.
