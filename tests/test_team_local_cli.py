from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TeamLocalCliTests(unittest.TestCase):
    def test_self_test_exits_zero(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "depone", "team-local", "--self-test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("team-local --self-test: pass", completed.stdout)

    def test_missing_plan_json_error(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "depone", "team-local", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 3)
        self.assertIn("ERR_TEAM_LOCAL_PLAN_REQUIRED", completed.stdout)

    def test_plan_with_command_ids_smoke_blocks_without_execution(self) -> None:
        repo_root = Path.cwd()
        base_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout.strip()
        with tempfile.TemporaryDirectory(prefix="depone-team-local-cli-") as temp_text:
            temp = Path(temp_text)
            plan_path = temp / "plan.json"
            allowlist_path = temp / "allowlist.json"
            out_dir = Path("out")
            plan_path.write_text(
                json.dumps(
                    {
                        "leader_objective": "CLI command_ids smoke",
                        "base_commit": base_commit,
                        "lanes": [
                            {
                                "lane_id": "lane-1",
                                "objective": "Parse ordered command ids",
                                "runner_adapter_kind": "shell",
                                "team_adapter_kind": "depone-native",
                                "planned_worktree": "lane-1-worktree",
                                "command_ids": ["ok"],
                                "touched_files": ["README.md"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            allowlist_path.write_text(
                json.dumps({"commands": [{"id": "ok", "argv": ["python3", "-c", "print('ok')"]}]}),
                encoding="utf-8",
            )
            env = {**__import__("os").environ, "PYTHONPATH": str(repo_root)}
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "depone",
                    "team-local",
                    "--plan",
                    str(plan_path),
                    "--allowlist",
                    str(allowlist_path),
                    "--repo",
                    str(repo_root),
                    "--worktree-root",
                    str(temp / "worktrees"),
                    "--out-dir",
                    str(out_dir),
                    "--json",
                ],
                cwd=temp,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("blocked", payload["decision"])
            self.assertEqual("out/team-run-ledger.json", payload["out"])


if __name__ == "__main__":
    unittest.main()
