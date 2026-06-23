#!/usr/bin/env python3
"""Create an A1 local-observed Keelplane evidence snapshot.

This reference collector never runs agents or task/verification commands. It
observes the current Git repository state, imports explicitly supplied records
as untrusted staging artifacts, then creates a hash ledger and local seal.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import mimetypes
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path

VERSION = "0.2.0"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    before = path.stat()
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    after = path.stat()
    identity_before = (before.st_size, before.st_mtime_ns, getattr(before, "st_ino", None))
    identity_after = (after.st_size, after.st_mtime_ns, getattr(after, "st_ino", None))
    if identity_before != identity_after:
        raise RuntimeError(f"file changed while hashing: {path}")
    return h.hexdigest()


def run_git(repo: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        stderr = completed.stderr.decode(errors="replace")
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return completed.stdout


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def validate_regular_file(path: Path, *, max_bytes: int) -> int:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"unsafe import: {path}")
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError(f"import is not a regular file: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"import exceeds per-file limit ({size} > {max_bytes}): {path}")
    return size


def import_records(
    sources: list[str],
    *,
    destination_root: Path,
    max_file_bytes: int,
    remaining_total_bytes: int,
) -> tuple[list[str], int]:
    imported_paths: list[str] = []
    consumed = 0
    for index, source_text in enumerate(sources, 1):
        source = Path(source_text).expanduser().resolve()
        size = validate_regular_file(source, max_bytes=max_file_bytes)
        if consumed + size > remaining_total_bytes:
            raise ValueError("imports exceed total byte limit")
        destination = destination_root / f"{index:03d}-{source.name}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        imported_paths.append(destination.as_posix())
        consumed += size
    return imported_paths, consumed


def iter_sealed_files(root: Path):
    excluded = {"hashes/ledger.json", "evidence-manifest.json", "seal.json"}
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
            raise RuntimeError(f"unsafe sealed path: {relative}")
        yield relative, path


def media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--run-contract")
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--attempt-id", default="attempt-01")
    parser.add_argument("--harness", default="unknown")
    parser.add_argument("--harness-version")
    parser.add_argument(
        "--auth-mode",
        choices=["subscription-declared", "api-key-declared", "unknown"],
        default="unknown",
    )
    parser.add_argument("--include-diff", action="store_true")
    parser.add_argument("--agent-result", action="append", default=[])
    parser.add_argument("--review", action="append", default=[])
    parser.add_argument("--command-receipt", action="append", default=[])
    parser.add_argument("--gate-event", action="append", default=[])
    parser.add_argument("--redaction-policy")
    parser.add_argument("--retention", choices=["ephemeral", "project", "release"], default="project")
    parser.add_argument("--max-import-bytes", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--max-total-import-bytes", type=int, default=50 * 1024 * 1024)
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    plan = Path(args.plan).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    if not repo.is_dir() or repo.is_symlink():
        print(f"error: invalid repository directory: {repo}", file=sys.stderr)
        return 2
    if not plan.is_file() or plan.is_symlink():
        print(f"error: invalid plan file: {plan}", file=sys.stderr)
        return 2
    if out.exists():
        print(f"error: output must not exist: {out}", file=sys.stderr)
        return 2

    try:
        plan_object = json.loads(plan.read_text(encoding="utf-8"))
        if not isinstance(plan_object, dict):
            raise ValueError("plan root is not an object")
    except Exception as exc:
        print(f"error: plan is not valid JSON: {exc}", file=sys.stderr)
        return 2

    run_contract: Path | None = None
    if args.run_contract:
        run_contract = Path(args.run_contract).expanduser().resolve()
        try:
            validate_regular_file(run_contract, max_bytes=args.max_import_bytes)
            contract_object = json.loads(run_contract.read_text(encoding="utf-8"))
            if not isinstance(contract_object, dict):
                raise ValueError("run contract root is not an object")
        except Exception as exc:
            print(f"error: invalid run contract: {exc}", file=sys.stderr)
            return 2

    # Observe the repository before creating a possibly in-repository evidence root.
    try:
        repository_root = run_git(repo, "rev-parse", "--show-toplevel").strip().decode()
        head = run_git(repo, "rev-parse", "HEAD").strip().decode()
        status = run_git(repo, "status", "--porcelain=v2", "-z")
        index_diff = run_git(repo, "diff", "--cached", "--binary", "--no-ext-diff")
        worktree_diff = run_git(repo, "diff", "--binary", "--no-ext-diff")
        untracked = run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
        git_version = subprocess.run(
            ["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
        ).stdout.decode(errors="replace").strip()
        try:
            submodules = run_git(repo, "submodule", "status", "--recursive")
        except RuntimeError:
            submodules = b""
    except Exception as exc:
        print(f"error: repository observation failed: {exc}", file=sys.stderr)
        return 2

    snapshot_material = b"\0".join(
        [head.encode(), status, index_diff, worktree_diff, untracked, submodules]
    )
    snapshot_sha256 = digest_bytes(snapshot_material)

    out.mkdir(parents=True)
    write_bytes(out / "plan/workflow.plan.json", plan.read_bytes())
    if run_contract is not None:
        write_bytes(out / "plan/run-contract.json", run_contract.read_bytes())

    write_bytes(out / "observed/repository/head.txt", (head + "\n").encode())
    write_bytes(out / "observed/repository/status.bin", status)
    write_bytes(out / "observed/repository/untracked-files.bin", untracked)
    write_bytes(out / "observed/repository/submodules.txt", submodules)

    diff_summary: dict[str, dict[str, object]] = {}
    for name, data in (("diff-index", index_diff), ("diff-worktree", worktree_diff)):
        diff_summary[name] = {
            "sha256": digest_bytes(data),
            "size_bytes": len(data),
            "captured_content": bool(args.include_diff),
        }
        if args.include_diff:
            write_bytes(out / f"observed/repository/{name}.patch", data)
    write_bytes(
        out / "observed/repository/diff-summary.json",
        (json.dumps(diff_summary, indent=2, sort_keys=True) + "\n").encode(),
    )

    redaction_policy_sha256: str | None = None
    if args.redaction_policy:
        redaction_source = Path(args.redaction_policy).expanduser().resolve()
        try:
            validate_regular_file(redaction_source, max_bytes=args.max_import_bytes)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        write_bytes(out / "observed/policies/redaction-policy.json", redaction_source.read_bytes())
        redaction_policy_sha256 = digest_file(out / "observed/policies/redaction-policy.json")

    imported_refs: dict[str, list[str]] = {
        "agent_results": [],
        "reviews": [],
        "commands": [],
        "gates": [],
    }
    total_imported = 0
    import_specs = [
        ("agent_results", args.agent_result, out / "staging/agent-results"),
        ("reviews", args.review, out / "staging/reviews"),
        ("commands", args.command_receipt, out / "staging/command-receipts"),
        ("gates", args.gate_event, out / "staging/gates"),
    ]
    try:
        for key, sources, destination in import_specs:
            refs, consumed = import_records(
                sources,
                destination_root=destination,
                max_file_bytes=args.max_import_bytes,
                remaining_total_bytes=args.max_total_import_bytes - total_imported,
            )
            imported_refs[key] = [Path(ref).relative_to(out).as_posix() for ref in refs]
            total_imported += consumed
    except ValueError as exc:
        shutil.rmtree(out, ignore_errors=True)
        print(f"error: {exc}", file=sys.stderr)
        return 2

    entries: list[dict[str, object]] = []
    artifacts: list[dict[str, object]] = []
    for relative, path in iter_sealed_files(out):
        file_digest = digest_file(path)
        size = path.stat().st_size
        entries.append({"path": relative, "sha256": file_digest, "size_bytes": size})
        origin = "local-observed" if relative.startswith(("observed/", "plan/")) else "imported"
        artifacts.append(
            {
                "artifact_id": f"file:{relative}",
                "path": relative,
                "sha256": file_digest,
                "size_bytes": size,
                "media_type": media_type(path),
                "origin": origin,
                "redacted": relative == "observed/policies/redaction-policy.json",
            }
        )

    ledger = {"schema_version": "1.0.0", "algorithm": "sha256", "entries": entries}
    write_bytes(
        out / "hashes/ledger.json",
        (json.dumps(ledger, indent=2, sort_keys=True) + "\n").encode(),
    )
    ledger_sha256 = digest_file(out / "hashes/ledger.json")

    plan_reference = {
        "path": "plan/workflow.plan.json",
        "sha256": digest_file(out / "plan/workflow.plan.json"),
    }
    contract_reference = None
    if run_contract is not None:
        contract_reference = {
            "path": "plan/run-contract.json",
            "sha256": digest_file(out / "plan/run-contract.json"),
        }

    manifest = {
        "schema_version": "1.0.0",
        "run_id": args.run_id,
        "attempt_id": args.attempt_id,
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "decision_state": "not-evaluated",
        "assurance": "A1-local-observed",
        "plan": plan_reference,
        "run_contract": contract_reference,
        "subject": {
            "kind": "git-repository",
            "repository": ".",
            "repository_label": Path(repository_root).name,
            "repository_locator_sha256": digest_bytes(repository_root.encode()),
            "head": head,
            "dirty": bool(status),
            "snapshot_sha256": snapshot_sha256,
            "status_sha256": digest_bytes(status),
            "index_diff_sha256": digest_bytes(index_diff),
            "worktree_diff_sha256": digest_bytes(worktree_diff),
            "untracked_sha256": digest_bytes(untracked),
            "submodules_sha256": digest_bytes(submodules),
        },
        "collector": {
            "name": "keelplane-capture-local",
            "version": VERSION,
            "origin": "local-observed",
            "platform": platform.platform(),
            "python": platform.python_version(),
            "git": git_version,
        },
        "harness": {
            "name": args.harness,
            "version": args.harness_version,
            "auth_mode": args.auth_mode,
            "session_refs": [],
        },
        "invocations": [],
        "artifacts": artifacts,
        "commands": imported_refs["commands"],
        "reviews": imported_refs["reviews"],
        "gates": imported_refs["gates"],
        "agent_results": imported_refs["agent_results"],
        "budgets": [],
        "redaction": {
            "policy_sha256": redaction_policy_sha256,
            "content_capture": "allowlisted-content" if args.include_diff else "metadata-only",
        },
        "retention": args.retention,
        "ledger": {"path": "hashes/ledger.json", "sha256": ledger_sha256},
        "event_log": None,
        "attestations": [],
        "warnings": [
            "A1 local observation does not prove provider or model identity.",
            "Imported staging records remain imported or self-reported.",
            "This capture is a point-in-time repository snapshot, not process custody.",
        ],
    }
    write_bytes(
        out / "evidence-manifest.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    )
    manifest_sha256 = digest_file(out / "evidence-manifest.json")

    sealed_paths_sha256 = digest_bytes(("\n".join(entry["path"] for entry in entries) + "\n").encode())
    seal = {
        "schema_version": "1.0.0",
        "run_id": args.run_id,
        "attempt_id": args.attempt_id,
        "manifest_sha256": manifest_sha256,
        "ledger_sha256": ledger_sha256,
        "sealed_paths_sha256": sealed_paths_sha256,
        "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sealer": {
            "name": "keelplane-capture-local",
            "version": VERSION,
            "origin": "local-observed",
        },
        "signature": None,
        "assurance": "A1-local-observed",
    }
    write_bytes(out / "seal.json", (json.dumps(seal, indent=2, sort_keys=True) + "\n").encode())

    print(
        json.dumps(
            {
                "out": str(out),
                "run_id": args.run_id,
                "attempt_id": args.attempt_id,
                "assurance": "A1-local-observed",
                "snapshot_sha256": snapshot_sha256,
                "sealed_files": len(entries),
                "include_diff": args.include_diff,
                "imported_bytes": total_imported,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
