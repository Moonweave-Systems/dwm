# Team Local Pass Lane Fixture

This directory contains a re-validatable `python3 -m depone team-local` pass-lane
fixture. The lane runs only ordered argv-allowlisted local commands, captures a
real `evidence-run` bundle, revalidates it with `evidence-next`, writes a
read-only `worktree-receipt.json`, and lets Team Ledger fan-in decide `pass`.

Boundary: this fixture does not launch Codex, Claude, OpenCode, OMX workers,
live models, or coding-agent sessions. It does not execute unlisted shell
commands, approve merges, or raise assurance.
