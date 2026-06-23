from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args: object, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, *map(str, args)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


class BundleTests(unittest.TestCase):
    def test_bundle_validation(self) -> None:
        completed = run(ROOT / "tools/validate_bundle.py")
        self.assertTrue(json.loads(completed.stdout)["valid"])

    def test_non_destructive_install_and_clean_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "AGENTS.md").write_text("existing\n", encoding="utf-8")
            (target / "CLAUDE.md").write_text("existing\n", encoding="utf-8")

            install = run(ROOT / "tools/install_pack.py", "--target", target, "--harness", "both")
            install_result = json.loads(install.stdout)
            self.assertEqual(install_result["conflicts"], 0)
            self.assertEqual((target / "AGENTS.md").read_text(), "existing\n")
            self.assertEqual((target / "CLAUDE.md").read_text(), "existing\n")
            self.assertTrue((target / ".codex/agents/kp-explorer.toml").is_file())
            self.assertTrue((target / ".claude/agents/kp-explorer.md").is_file())
            self.assertTrue((target / ".keelplane/install-fragments/codex-config.fragment.toml").is_file())
            receipt = target / ".keelplane/team/install-receipt.json"
            self.assertTrue(receipt.is_file())

            uninstall = run(ROOT / "tools/install_pack.py", "--target", target, "--uninstall")
            self.assertEqual(json.loads(uninstall.stdout)["kept_modified"], [])
            self.assertFalse((target / ".codex/agents/kp-explorer.toml").exists())
            self.assertEqual((target / "AGENTS.md").read_text(), "existing\n")
            self.assertEqual((target / "CLAUDE.md").read_text(), "existing\n")

    def test_uninstall_preserves_modified_file_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            run(ROOT / "tools/install_pack.py", "--target", target, "--harness", "codex")
            modified = target / ".codex/agents/kp-explorer.toml"
            modified.write_text(modified.read_text() + "\n# user modification\n")
            completed = run(ROOT / "tools/install_pack.py", "--target", target, "--uninstall", check=False)
            self.assertNotEqual(completed.returncode, 0)
            result = json.loads(completed.stdout)
            self.assertIn(str(modified), result["kept_modified"])
            self.assertTrue((target / ".keelplane/team/install-receipt.json").is_file())

    def test_installer_rejects_symlink_parent(self) -> None:
        if not hasattr(Path, "symlink_to"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            outside = root / "outside"
            target.mkdir()
            outside.mkdir()
            try:
                (target / ".codex").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation not permitted")
            completed = run(
                ROOT / "tools/install_pack.py",
                "--target",
                target,
                "--harness",
                "codex",
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(any(outside.rglob("*.toml")))

    def test_capture_schema_seal_and_tamper_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            (repo / "a.txt").write_text("one\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True)
            (repo / "a.txt").write_text("two\n", encoding="utf-8")

            plan = root / "plan.json"
            plan.write_text('{"schema_version":"0.5","objective":"demo"}\n', encoding="utf-8")
            out = root / "evidence"
            run(
                ROOT / "tools/capture_local.py",
                "--repo",
                repo,
                "--plan",
                plan,
                "--out",
                out,
                "--run-id",
                "demo",
                "--harness",
                "codex",
                "--auth-mode",
                "subscription-declared",
            )

            manifest = json.loads((out / "evidence-manifest.json").read_text())
            seal = json.loads((out / "seal.json").read_text())
            manifest_schema = json.loads((ROOT / "schemas/evidence-manifest.schema.json").read_text())
            seal_schema = json.loads((ROOT / "schemas/seal.schema.json").read_text())
            jsonschema.Draft202012Validator(manifest_schema, format_checker=jsonschema.FormatChecker()).validate(manifest)
            jsonschema.Draft202012Validator(seal_schema, format_checker=jsonschema.FormatChecker()).validate(seal)
            self.assertNotIn(str(repo.resolve()), json.dumps(manifest))

            valid = run(ROOT / "tools/verify_seal.py", out)
            self.assertTrue(json.loads(valid.stdout)["valid"])
            (out / "observed/repository/head.txt").write_text("tampered\n", encoding="utf-8")
            invalid = run(ROOT / "tools/verify_seal.py", out, check=False)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertFalse(json.loads(invalid.stdout)["valid"])

    def test_duplicate_ledger_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            (repo / "a.txt").write_text("one\n")
            subprocess.run(["git", "-C", str(repo), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True)
            plan = root / "plan.json"
            plan.write_text('{"schema_version":"0.5","objective":"demo"}\n')
            out = root / "evidence"
            run(ROOT / "tools/capture_local.py", "--repo", repo, "--plan", plan, "--out", out, "--run-id", "demo")
            ledger_path = out / "hashes/ledger.json"
            ledger = json.loads(ledger_path.read_text())
            ledger["entries"].append(dict(ledger["entries"][0]))
            ledger_path.write_text(json.dumps(ledger, indent=2) + "\n")
            completed = run(ROOT / "tools/verify_seal.py", out, check=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertTrue(any("duplicate ledger path" in issue for issue in json.loads(completed.stdout)["issues"]))


if __name__ == "__main__":
    unittest.main()
