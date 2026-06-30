# Team shell lane launch fixture

This directory contains the first machine fixture for
`python3 -m depone team-shell-lane-launch`.

The command is selected by `command_id` from `allowlist.json` and executed as an
argv list with `subprocess.run(..., shell=False)`. The adapter does not accept or
concatenate arbitrary shell command strings. `receipt.json` records the resolved
`cwd`, argv, exit code, stdout/stderr SHA-256 hashes, transcript path/hash, `agent_contract_hash`, and `agent_contract` facts;
`transcript.json` contains the captured stdout/stderr text.

Contract terms: `subprocess.run(..., shell=False)`; does not accept or concatenate arbitrary shell command strings; does not launch Codex, Claude, OpenCode; does not raise assurance; does not claim A2/container isolation; binds a V22 role id; records `agent_contract_hash` from `packaging/depone-agent-operating-contract.json`.

Regenerate the fixture with:

```bash
python3 -m depone team-shell-lane-launch \
  --allowlist docs/team-shell-lane-launch/allowlist.json \
  --command-id fixture-echo \
  --cwd . \
  --out docs/team-shell-lane-launch/receipt.json \
  --transcript docs/team-shell-lane-launch/transcript.json \
  --agent-role-id operator \
  --json
```

Generated files:

- `allowlist.json` — explicit argv allowlist for this fixture.
- `receipt.json` — machine receipt for the selected command, including the V22 role id and contract hash binding.
- `transcript.json` — captured stdout/stderr text for the selected command.

## Honest boundary

This is shell-only A1-style local evidence. It executes the allowlisted local
argv command, but it does not launch Codex, Claude, OpenCode, live models, team
workers, or a scheduler. It does not raise assurance, does not claim
A2/container isolation, and does not prove lane task completion.

Residual: the committed receipt records the absolute `cwd` of the capture host.
A fresh clone can revalidate the JSON shape and boundary fields, but should
re-run the command to recreate host-local receipt paths and hashes.
