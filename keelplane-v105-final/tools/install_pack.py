#!/usr/bin/env python3
"""Non-destructive, project-scoped installer for Keelplane reference packs."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_destination(target: Path, destination: Path) -> Path:
    """Reject destinations that escape target or traverse an existing symlink."""
    target = target.resolve()
    try:
        relative = destination.relative_to(target)
    except ValueError as exc:
        raise ValueError(f"destination escapes target: {destination}") from exc

    current = target
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError(f"destination parent is a symlink: {current}")
    if destination.exists() and destination.is_symlink():
        raise ValueError(f"destination is a symlink: {destination}")
    return destination


def copy_managed(
    source: Path,
    destination: Path,
    *,
    target: Path,
    dry_run: bool,
    force_generated: bool,
    events: list[dict[str, object]],
) -> None:
    try:
        safe_destination(target, destination)
    except ValueError as exc:
        events.append({"path": str(destination), "action": "conflict", "reason": str(exc)})
        return

    existed = destination.exists()
    if existed:
        if not destination.is_file():
            events.append({"path": str(destination), "action": "conflict", "reason": "not-a-file"})
            return
        destination_hash = sha256_file(destination)
        source_hash = sha256_file(source)
        if destination_hash == source_hash:
            events.append({"path": str(destination), "action": "unchanged", "sha256": destination_hash})
            return
        if not force_generated:
            events.append({"path": str(destination), "action": "conflict", "reason": "different-content"})
            return
    else:
        source_hash = sha256_file(source)

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        safe_destination(target, destination)
        shutil.copy2(source, destination)

    events.append(
        {
            "path": str(destination),
            "action": "replace-managed" if existed else "install",
            "sha256": source_hash,
        }
    )


def copy_tree(
    source_root: Path,
    destination_root: Path,
    *,
    target: Path,
    dry_run: bool,
    force_generated: bool,
    events: list[dict[str, object]],
) -> None:
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        copy_managed(
            source,
            destination_root / source.relative_to(source_root),
            target=target,
            dry_run=dry_run,
            force_generated=force_generated,
            events=events,
        )


def uninstall(target: Path, dry_run: bool) -> int:
    receipt = target / ".keelplane/team/install-receipt.json"
    if not receipt.is_file() or receipt.is_symlink():
        print(f"error: safe receipt not found: {receipt}", file=sys.stderr)
        return 2

    data = json.loads(receipt.read_text(encoding="utf-8"))
    kept: list[str] = []
    removed: list[str] = []

    for item in reversed(data.get("managed_files", [])):
        raw_relative = item.get("relative_path")
        expected_hash = item.get("sha256")
        if not isinstance(raw_relative, str) or not isinstance(expected_hash, str):
            kept.append(f"invalid receipt entry: {item!r}")
            continue
        candidate = target / raw_relative
        try:
            safe_destination(target, candidate)
        except ValueError:
            kept.append(str(candidate))
            continue
        if not candidate.exists():
            continue
        if candidate.is_file() and sha256_file(candidate) == expected_hash:
            if not dry_run:
                candidate.unlink()
            removed.append(str(candidate))
        else:
            kept.append(str(candidate))

    # Preserve the receipt when modified files remain so uninstall can be retried.
    if not dry_run and not kept and receipt.exists():
        receipt.unlink()

    print(json.dumps({"removed": removed, "kept_modified": kept, "dry_run": dry_run}, indent=2))
    return 0 if not kept else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--harness", choices=["codex", "claude", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--force-generated",
        action="store_true",
        help="replace conflicting generated agents, schemas, profiles, and fragments",
    )
    parser.add_argument(
        "--create-root-instructions",
        action="store_true",
        help="create AGENTS.md/CLAUDE.md only when the respective root file is absent",
    )
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir() or target.is_symlink():
        print(f"error: target is not a safe directory: {target}", file=sys.stderr)
        return 2
    if args.uninstall:
        return uninstall(target, args.dry_run)

    events: list[dict[str, object]] = []
    fragments = target / ".keelplane/install-fragments"
    team = target / ".keelplane/team"

    copy_tree(
        ROOT / "profiles",
        team / "profiles",
        target=target,
        dry_run=args.dry_run,
        force_generated=args.force_generated,
        events=events,
    )
    copy_tree(
        ROOT / "schemas",
        team / "schemas",
        target=target,
        dry_run=args.dry_run,
        force_generated=args.force_generated,
        events=events,
    )

    harnesses = {"codex", "claude"} if args.harness == "both" else {args.harness}
    if "codex" in harnesses:
        copy_tree(
            ROOT / "packs/codex/.codex/agents",
            target / ".codex/agents",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        copy_managed(
            ROOT / "packs/codex/AGENTS.keelplane.md",
            fragments / "AGENTS.keelplane.md",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        copy_managed(
            ROOT / "packs/codex/.codex/config.fragment.toml",
            fragments / "codex-config.fragment.toml",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        if args.create_root_instructions and not (target / "AGENTS.md").exists():
            copy_managed(
                ROOT / "packs/codex/AGENTS.keelplane.md",
                target / "AGENTS.md",
                target=target,
                dry_run=args.dry_run,
                force_generated=False,
                events=events,
            )

    if "claude" in harnesses:
        copy_tree(
            ROOT / "packs/claude/.claude/agents",
            target / ".claude/agents",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        copy_managed(
            ROOT / "packs/claude/CLAUDE.keelplane.md",
            fragments / "CLAUDE.keelplane.md",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        copy_managed(
            ROOT / "packs/claude/.claude/settings.agent-teams.fragment.json",
            fragments / "claude-agent-teams.settings.fragment.json",
            target=target,
            dry_run=args.dry_run,
            force_generated=args.force_generated,
            events=events,
        )
        if args.create_root_instructions and not (target / "CLAUDE.md").exists():
            copy_managed(
                ROOT / "packs/claude/CLAUDE.keelplane.md",
                target / "CLAUDE.md",
                target=target,
                dry_run=args.dry_run,
                force_generated=False,
                events=events,
            )

    conflicts = [event for event in events if event["action"] == "conflict"]
    managed_files: list[dict[str, str]] = []
    for event in events:
        if event["action"] not in {"install", "replace-managed", "unchanged"} or "sha256" not in event:
            continue
        event_path = Path(str(event["path"]))
        try:
            relative = event_path.relative_to(target).as_posix()
        except ValueError:
            continue
        managed_files.append({"relative_path": relative, "sha256": str(event["sha256"])})

    receipt = {
        "schema_version": "1.0.0",
        "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "target": str(target),
        "harness": args.harness,
        "managed_files": managed_files,
        "events": events,
        "notes": [
            "Instruction and configuration fragments require manual review and merge.",
            "Claude Agent Teams remains opt-in and is not automatically enabled.",
        ],
    }
    receipt_path = team / "install-receipt.json"
    if not args.dry_run:
        try:
            safe_destination(target, receipt_path)
        except ValueError as exc:
            print(f"error: unsafe receipt destination: {exc}", file=sys.stderr)
            return 2
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "target": str(target),
                "dry_run": args.dry_run,
                "events": events,
                "receipt": str(receipt_path),
                "conflicts": len(conflicts),
            },
            indent=2,
        )
    )
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
