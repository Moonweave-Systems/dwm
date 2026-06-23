#!/usr/bin/env python3
"""Verify exact-byte integrity of a Keelplane local A1 seal.

This tool validates tamper evidence only. It does not upgrade provenance or
prove provider/model identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath

EXCLUDED = {"hashes/ledger.json", "evidence-manifest.json", "seal.json"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_protocol_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    if any(ord(char) < 32 for char in value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in path.parts)


def discover_regular_files(root: Path, issues: list[str]) -> list[str]:
    discovered: list[str] = []
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        safe_dirs: list[str] = []
        for dirname in sorted(dirnames):
            child = base / dirname
            if child.is_symlink():
                issues.append(f"KP-PATH-UNSAFE symlink directory: {child.relative_to(root).as_posix()}")
            else:
                safe_dirs.append(dirname)
        dirnames[:] = safe_dirs
        for filename in sorted(filenames):
            path = base / filename
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
                issues.append(f"KP-PATH-UNSAFE non-regular path: {relative}")
                continue
            discovered.append(relative)
    return sorted(discovered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    issues: list[str] = []

    if not root.is_dir() or root.is_symlink():
        print(f"error: unsafe evidence root: {root}", file=sys.stderr)
        return 2

    try:
        ledger = json.loads((root / "hashes/ledger.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / "evidence-manifest.json").read_text(encoding="utf-8"))
        seal = json.loads((root / "seal.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"error: cannot load seal inputs: {exc}", file=sys.stderr)
        return 2

    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        issues.append("KP-EVIDENCE-SCHEMA ledger entries is not an array")
        entries = []

    expected: dict[str, dict[str, object]] = {}
    ordered_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            issues.append("KP-EVIDENCE-SCHEMA non-object ledger entry")
            continue
        relative = entry.get("path")
        if not safe_protocol_path(relative):
            issues.append(f"KP-PATH-UNSAFE ledger path: {relative!r}")
            continue
        relative = str(relative)
        if relative in EXCLUDED:
            issues.append(f"KP-EVIDENCE-SCHEMA excluded file in ledger: {relative}")
        if relative in expected:
            issues.append(f"KP-EVIDENCE-SCHEMA duplicate ledger path: {relative}")
            continue
        if not isinstance(entry.get("sha256"), str) or len(str(entry.get("sha256"))) != 64:
            issues.append(f"KP-EVIDENCE-SCHEMA bad digest: {relative}")
        if not isinstance(entry.get("size_bytes"), int) or int(entry.get("size_bytes", -1)) < 0:
            issues.append(f"KP-EVIDENCE-SCHEMA bad size: {relative}")
        expected[relative] = entry
        ordered_paths.append(relative)

    if ordered_paths != sorted(ordered_paths):
        issues.append("KP-EVIDENCE-SCHEMA ledger paths are not sorted")

    actual_all = discover_regular_files(root, issues)
    actual = [relative for relative in actual_all if relative not in EXCLUDED]

    for relative in actual:
        entry = expected.get(relative)
        if entry is None:
            issues.append(f"KP-SEAL-INVALID extra sealed file: {relative}")
            continue
        path = root / relative
        if path.stat().st_size != entry.get("size_bytes"):
            issues.append(f"KP-HASH-MISMATCH size mismatch: {relative}")
        if sha256_file(path) != entry.get("sha256"):
            issues.append(f"KP-HASH-MISMATCH digest mismatch: {relative}")

    for relative in sorted(set(expected) - set(actual)):
        issues.append(f"KP-ARTIFACT-MISSING sealed file: {relative}")

    ledger_sha256 = sha256_file(root / "hashes/ledger.json")
    manifest_sha256 = sha256_file(root / "evidence-manifest.json")
    if ledger_sha256 != seal.get("ledger_sha256"):
        issues.append("KP-SEAL-INVALID seal ledger digest mismatch")
    if ledger_sha256 != manifest.get("ledger", {}).get("sha256"):
        issues.append("KP-SEAL-INVALID manifest ledger digest mismatch")
    if manifest_sha256 != seal.get("manifest_sha256"):
        issues.append("KP-SEAL-INVALID manifest digest mismatch")

    if manifest.get("run_id") != seal.get("run_id") or manifest.get("attempt_id") != seal.get("attempt_id"):
        issues.append("KP-SEAL-INVALID run or attempt identity mismatch")

    path_digest = hashlib.sha256(("\n".join(ordered_paths) + "\n").encode()).hexdigest()
    if path_digest != seal.get("sealed_paths_sha256"):
        issues.append("KP-SEAL-INVALID sealed path digest mismatch")

    plan_reference = manifest.get("plan", {})
    plan_path = plan_reference.get("path")
    if safe_protocol_path(plan_path):
        plan_entry = expected.get(str(plan_path))
        if plan_entry is None:
            issues.append("KP-ARTIFACT-MISSING plan is not sealed")
        elif plan_entry.get("sha256") != plan_reference.get("sha256"):
            issues.append("KP-HASH-MISMATCH plan digest differs from manifest")
    else:
        issues.append("KP-PATH-UNSAFE plan path")

    result = {
        "valid": not issues,
        "decision": "integrity-valid" if not issues else "integrity-invalid",
        "assurance": seal.get("assurance"),
        "issues": issues,
        "sealed_files": len(expected),
        "warning": "A valid local seal proves post-capture byte integrity only.",
    }
    print(json.dumps(result, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
