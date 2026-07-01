# Team Local Pass Evidence

This directory records the first `team-local` lane that reaches Team Ledger
`pass` from machine artifacts.

Re-run from the repository root:

```bash
python3 -m depone team-local \
  --plan docs/team-local-pass/team-plan.json \
  --allowlist docs/team-local-pass/allowlist.json \
  --repo . \
  --worktree-root /tmp/depone-team-local-pass \
  --base-commit c7b605c16405bef87d783d2244b87838d9526cf4 \
  --out-dir docs/team-local-pass \
  --create-worktree \
  --execute-lanes \
  --json
```

Independent re-validation:

```bash
python3 - <<'PY'
import json
from pathlib import Path
from depone.agent_fabric.team_local import validate_team_local_run_ledger

root = Path("docs/team-local-pass")
ledger = json.loads((root / "team-run-ledger.json").read_text(encoding="utf-8"))
print("decision:", ledger.get("decision"))
print("validate errors:", validate_team_local_run_ledger(ledger, base_dir=Path(".")))
print("team ledger decision:", json.loads((root / "team-ledger-verdict.json").read_text(encoding="utf-8")).get("decision"))
print("evidence-next decision:", json.loads((root / "lane-1" / "evidence-next-verdict.json").read_text(encoding="utf-8")).get("decision"))
PY
```

Expected output:

```text
decision: pass
validate errors: []
team ledger decision: pass
evidence-next decision: continue
```

Honest boundary: this is a local shell lane and does not launch live coding
agents, call live models, or approve merges. It does not raise A2/A3 assurance
or execute commands outside `allowlist.json`. The `evidence-run` CLI may return exit code 2
for A1-local inconclusive assurance while still producing re-validatable
artifacts; `allowed_exit_codes` records that this command was accepted only as
an artifact-generation step. The lane pass is decided by `evidence-next` plus
`worktree-receipt`, not by prose.
