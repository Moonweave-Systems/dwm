# Team shell lane launch fixture

This directory contains the first machine fixture for `depone team-shell-lane-launch`.

The command is selected by `command_id` from `allowlist.json` and executed as an
argv list with `subprocess.run(..., shell=False)`. The adapter does not accept or
concatenate arbitrary shell command strings. `receipt.json` records the resolved
`cwd`, argv, exit code, stdout/stderr SHA-256 hashes, and transcript path/hash;
`transcript.json` contains the captured stdout/stderr text.

The fixture deliberately uses a harmless local Python one-liner and does not
launch Codex, Claude, OpenCode, live models, or team workers.
