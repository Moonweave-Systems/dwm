# Team Launch Preflight

This directory is reserved for the first non-executing `team-launch-preflight`
fixture set. The command is the bridge between `team-dry-run` planning artifacts
and a future lane launcher, but it is still a preflight gate only.

## Current status

The checked-in fixture JSON files are intentionally absent until
`python3 -m depone team-launch-preflight` is available in the CLI. Do not copy
older Team Ledger or team dry-run artifacts into this directory to satisfy the
contract. Once the command exists, generate the artifacts from the command:

```bash
BASE_COMMIT=$(python3 - <<'PY'
import json
print(json.load(open("docs/team-dry-run/team-dry-run.json"))["base_commit"])
PY
)
python3 -m depone team-launch-preflight \
  --team-dry-run docs/team-dry-run/team-dry-run.json \
  --repo . \
  --base-commit "$BASE_COMMIT" \
  --launch-intent plan-only \
  --out docs/team-launch-preflight/team-launch-preflight.json \
  --team-ledger-out docs/team-launch-preflight/team-ledger.json \
  --json
python3 -m depone team-ledger \
  --ledger docs/team-launch-preflight/team-ledger.json \
  --out docs/team-launch-preflight/team-ledger-verdict.json \
  --json
```

Expected generated files after the CLI lands:

- `team-launch-preflight.json`
- `team-ledger.json`
- `team-ledger-verdict.json`

## Honest boundary

Team launch preflight does not launch agents, does not create worktrees, does
not execute lane commands, and does not prove task completion. Planned lanes
remain blocked until machine evidence exists and Team Ledger fan-in validates
that evidence.

`team-ledger.json` in this directory must be generated from the preflight
command, not copied from the older dry-run fixture. The preflight and ledger
artifacts must match on lane ids, evidence directories, planned worktrees, and
worktree receipt paths.
