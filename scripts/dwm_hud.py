#!/usr/bin/env python3
"""V17 read-only HUD for DWM artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compile_workflow import (  # noqa: E402
    CompileError,
    canonical_hash,
    canonical_json_text,
    compile_plan,
    read_json,
    write_json_atomic,
    write_text_atomic,
)
from dwm_runner import (  # noqa: E402
    FANOUT_ROOT,
    V1_OUT_ROOT,
    RunnerError,
    fanin,
    fanout,
    rel,
    resolve_fanout_out,
    safe_segment,
    write_fixture_plan,
)


TOOL = "dwm_hud.py"
SCHEMA_VERSION = "1.0"
HUD_VERSION = "17.0.0"
HUD_ROOT = ROOT / "out" / "hud"
SENTINEL = ".dwm_hud-owned.json"


class HudError(ValueError):
    """Structured V17 HUD failure."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        path: Path | str | None = None,
        fixture_id: str | None = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.path = str(path) if path is not None else None
        self.fixture_id = fixture_id

    def to_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.path is not None:
            record["path"] = self.path
        if self.fixture_id is not None:
            record["fixture_id"] = self.fixture_id
        return record


def now_utc() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def reject_traversal(path: Path, *, code: str, message: str) -> None:
    if any(part == ".." for part in path.parts):
        raise HudError(code, message, path=path)


def check_components_not_symlink(path: Path, *, code: str) -> None:
    absolute = path if path.is_absolute() else ROOT / path
    current = Path(absolute.anchor) if absolute.is_absolute() else Path(".")
    parts = absolute.parts[1:] if absolute.is_absolute() else absolute.parts
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise HudError(code, "path contains a symlink", path=current)


def resolve_under(value: str | Path, root: Path, *, label: str) -> Path:
    raw = Path(value)
    reject_traversal(raw, code="ERR_HUD_PATH_UNSAFE", message=f"{label} path must not contain parent traversal")
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise HudError("ERR_HUD_PATH_UNSAFE", f"{label} path must resolve under {root_resolved}", path=value) from exc
    if resolved == root_resolved:
        raise HudError("ERR_HUD_PATH_UNSAFE", f"{label} path must name a directory", path=value)
    check_components_not_symlink(candidate, code="ERR_HUD_PATH_SYMLINK")
    return resolved


def resolve_hud_out(value: str | Path) -> Path:
    return resolve_under(value, HUD_ROOT, label="HUD output")


def ensure_contained(root: Path, path: Path) -> None:
    target = path if path.is_absolute() else root / path
    reject_traversal(path, code="ERR_HUD_PATH_UNSAFE", message="artifact path escapes output directory")
    try:
        target.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise HudError("ERR_HUD_PATH_UNSAFE", "artifact path escapes output directory", path=target) from exc


def read_json_obj(path: Path, *, root: Path, label: str) -> dict[str, Any]:
    ensure_contained(root, path)
    if not path.is_file() or path.is_symlink():
        raise HudError("ERR_HUD_STALE_EVIDENCE", f"{label} is missing or symlinked", path=path)
    try:
        data = json.loads(path.read_text())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HudError("ERR_HUD_STALE_EVIDENCE", f"{label} is malformed: {exc}", path=path) from exc
    if not isinstance(data, dict):
        raise HudError("ERR_HUD_STALE_EVIDENCE", f"{label} root must be an object", path=path)
    return data


def read_owned_sentinel(path: Path) -> dict[str, Any] | None:
    sentinel = path / SENTINEL
    if not sentinel.is_file() or sentinel.is_symlink():
        return None
    try:
        data = json.loads(sentinel.read_text())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def prepare_hud_out(out_dir: Path, hud_id: str, source_dir: Path) -> None:
    if out_dir.exists():
        if out_dir.is_symlink():
            raise HudError("ERR_HUD_PATH_SYMLINK", "HUD output is a symlink", path=out_dir)
        if not out_dir.is_dir():
            raise HudError("ERR_HUD_PATH_UNSAFE", "HUD output is not a directory", path=out_dir)
        sentinel = read_owned_sentinel(out_dir)
        if sentinel is None or sentinel.get("hud_id") != hud_id:
            raise HudError("ERR_HUD_PATH_UNSAFE", "existing HUD output is not HUD-owned", path=out_dir)
        shutil.rmtree(out_dir)
    HUD_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True)
    sentinel = {
        "tool": TOOL,
        "schema_version": SCHEMA_VERSION,
        "hud_version": HUD_VERSION,
        "hud_id": hud_id,
        "source_path": rel(source_dir),
        "created_at": now_utc(),
    }
    write_json_atomic(out_dir / SENTINEL, sentinel, root=out_dir)


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# V17 DWM HUD",
        "",
        f"Decision: `{summary['decision']}`",
        f"Next action: `{summary['next_action']}`",
        f"Source kind: `{summary['source']['kind']}`",
        f"Source status: `{summary['source']['status']}`",
        "",
        "## Evidence",
        "",
        f"- Review queue: {summary['review_queue_count']}",
        f"- Conflicts: {summary['conflict_count']}",
        f"- Failed workers: {len(summary['failed_workers'])}",
        "",
    ]
    if summary["blocked_by"]:
        lines.extend(["## Blocked By", "", *[f"- {item}" for item in summary["blocked_by"]], ""])
    if summary["artifact_paths"]:
        lines.extend(["## Artifacts", "", *[f"- `{path}`" for path in summary["artifact_paths"]], ""])
    return "\n".join(lines)


def summarize_fanout(fanout_dir: Path, out_dir: Path) -> dict[str, Any]:
    fanout_dir = resolve_fanout_out(fanout_dir)
    out_dir = resolve_hud_out(out_dir)
    hud_id = safe_segment(out_dir.name, code="ERR_HUD_PATH_UNSAFE")
    prepare_hud_out(out_dir, hud_id, fanout_dir)
    status = read_json_obj(fanout_dir / "status.json", root=fanout_dir, label="status.json")
    queue = read_json_obj(fanout_dir / "review-queue.json", root=fanout_dir, label="review-queue.json")
    conflicts_obj = read_json_obj(fanout_dir / "conflicts.json", root=fanout_dir, label="conflicts.json")
    fanin_status = read_json_obj(fanout_dir / "fanin-status.json", root=fanout_dir, label="fanin-status.json")
    queue_items = queue.get("items", [])
    conflicts = conflicts_obj.get("conflicts", [])
    if not isinstance(queue_items, list) or not isinstance(conflicts, list):
        raise HudError("ERR_HUD_STALE_EVIDENCE", "fanout review queue or conflict list is malformed", path=fanout_dir)
    failed_workers = status.get("failed_workers", [])
    if not isinstance(failed_workers, list):
        raise HudError("ERR_HUD_STALE_EVIDENCE", "fanout failed_workers is malformed", path=fanout_dir / "status.json")
    if status.get("review_queue_count") != len(queue_items) or fanin_status.get("review_queue_count") != len(queue_items):
        raise HudError("ERR_HUD_STALE_EVIDENCE", "fanout review queue count drifted", path=fanout_dir / "review-queue.json")
    if status.get("conflict_count") != len(conflicts) or fanin_status.get("conflict_count") != len(conflicts):
        raise HudError("ERR_HUD_STALE_EVIDENCE", "fanout conflict count drifted", path=fanout_dir / "conflicts.json")

    blocked_by: list[str] = []
    if failed_workers:
        decision = "blocked"
        next_action = "inspect_failed_workers"
        blocked_by.append("failed-workers")
    elif conflicts:
        decision = "needs_review"
        next_action = "resolve_ownership_conflicts"
        blocked_by.append("ownership-conflicts")
    else:
        decision = "ready"
        next_action = "review_worker_outputs"

    summary = {
        "tool": TOOL,
        "schema_version": SCHEMA_VERSION,
        "hud_version": HUD_VERSION,
        "hud_id": hud_id,
        "created_at": now_utc(),
        "decision": decision,
        "next_action": next_action,
        "blocked_by": blocked_by,
        "source": {
            "kind": "fanout",
            "path": rel(fanout_dir),
            "status": status.get("status"),
            "fanout_id": status.get("fanout_id"),
        },
        "review_queue_count": len(queue_items),
        "conflict_count": len(conflicts),
        "failed_workers": failed_workers,
        "command_preview": None,
        "approval_writer_enabled": False,
        "artifact_paths": [
            rel(fanout_dir / "status.json"),
            rel(fanout_dir / "review-queue.json"),
            rel(fanout_dir / "conflicts.json"),
            rel(fanout_dir / "fanin-status.json"),
        ],
        "source_hashes": {
            "status.json": canonical_hash(status),
            "review-queue.json": canonical_hash(queue),
            "conflicts.json": canonical_hash(conflicts_obj),
            "fanin-status.json": canonical_hash(fanin_status),
        },
    }
    write_json_atomic(out_dir / "hud-summary.json", summary, root=out_dir)
    write_text_atomic(out_dir / "hud-summary.md", render_markdown(summary), root=out_dir)
    return summary


def fanout_workers(kind: str) -> list[dict[str, Any]]:
    if kind == "fanout-conflict":
        return [
            {"id": "inventory-a", "ownership": ["inventory/shared"]},
            {"id": "inventory-b", "ownership": ["inventory/shared"]},
        ]
    if kind == "fanout-failed-worker":
        return [
            {"id": "inventory-a", "ownership": ["inventory/a"]},
            {"id": "inventory-b", "ownership": ["inventory/b"], "fail": True},
        ]
    return [
        {"id": "inventory-a", "ownership": ["inventory/a"]},
        {"id": "inventory-b", "ownership": ["inventory/b"]},
    ]


def run_fixture(fixture: dict[str, Any], suite_dir: Path, temp_root: Path) -> dict[str, Any]:
    fixture_id = fixture["id"]
    try:
        plan_fixture = {"id": fixture_id, "plan": "fixtures/v1/plans/ready-readonly.workflow.plan.json"}
        plan_path = write_fixture_plan(temp_root, plan_fixture)
        v1_run_dir = V1_OUT_ROOT / f"v17-{suite_dir.name}" / fixture_id
        compile_plan(plan_path, v1_run_dir, run_id=f"v17/{fixture_id}", mode="fixture")
        fanout_dir = FANOUT_ROOT / f"v17-{suite_dir.name}-{fixture_id}"
        status = fanout(v1_run_dir, fanout_dir, workers=fanout_workers(str(fixture["kind"])), cap=2)
        fanin(fanout_dir)
        if fixture["kind"] == "stale-fanout":
            status["review_queue_count"] = 99
            write_json_atomic(fanout_dir / "status.json", status, root=fanout_dir)
        out_dir = suite_dir / fixture_id
        try:
            summary = summarize_fanout(fanout_dir, out_dir)
        except HudError as exc:
            expected_error = fixture.get("expected_error")
            if expected_error != exc.code:
                raise
            summary = {
                "decision": "blocked",
                "next_action": "refresh_source_artifacts",
                "error": exc.to_record(),
                "review_queue_count": None,
                "conflict_count": None,
            }
        expected_decision = fixture.get("expected_decision")
        if expected_decision is not None and summary.get("decision") != expected_decision:
            raise HudError("ERR_HUD_FIXTURE_FAILED", f"expected decision {expected_decision}, got {summary.get('decision')}")
        expected_next_action = fixture.get("expected_next_action")
        if expected_next_action is not None and summary.get("next_action") != expected_next_action:
            raise HudError("ERR_HUD_FIXTURE_FAILED", f"expected next action {expected_next_action}, got {summary.get('next_action')}")
        expected_review_queue_count = fixture.get("expected_review_queue_count")
        if expected_review_queue_count is not None and summary.get("review_queue_count") != expected_review_queue_count:
            raise HudError("ERR_HUD_FIXTURE_FAILED", f"expected review queue count {expected_review_queue_count}, got {summary.get('review_queue_count')}")
        expected_conflict_count = fixture.get("expected_conflict_count")
        if expected_conflict_count is not None and summary.get("conflict_count") != expected_conflict_count:
            raise HudError("ERR_HUD_FIXTURE_FAILED", f"expected conflict count {expected_conflict_count}, got {summary.get('conflict_count')}")
        expected_error = fixture.get("expected_error")
        actual_error = summary.get("error", {}).get("code") if isinstance(summary.get("error"), dict) else None
        if expected_error is not None and actual_error != expected_error:
            raise HudError("ERR_HUD_FIXTURE_FAILED", f"expected error {expected_error}, got {actual_error}")
        return {"id": fixture_id, "status": "pass", "required": fixture.get("required", True)}
    except (HudError, RunnerError, CompileError) as exc:
        if isinstance(exc, (HudError, RunnerError)):
            record = exc.to_record()
        else:
            record = {"code": exc.code, "message": exc.message, "path": exc.path}
        record["fixture_id"] = fixture_id
        return {"id": fixture_id, "status": "fail", "required": fixture.get("required", True), "error": record}


def evaluate_manifest(manifest_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    suite_id = Path(out_dir).name
    suite_dir = resolve_hud_out(out_dir)
    if suite_dir.exists():
        sentinel = read_owned_sentinel(suite_dir)
        if sentinel is None or sentinel.get("hud_id") != suite_id:
            raise HudError("ERR_HUD_PATH_UNSAFE", "existing HUD suite is not HUD-owned", path=suite_dir)
        shutil.rmtree(suite_dir)
    suite_dir.mkdir(parents=True)
    write_json_atomic(
        suite_dir / SENTINEL,
        {
            "tool": TOOL,
            "schema_version": SCHEMA_VERSION,
            "hud_version": HUD_VERSION,
            "hud_id": suite_id,
            "source_path": rel(manifest_path),
            "created_at": now_utc(),
        },
        root=suite_dir,
    )
    temp_root = suite_dir / "_fixture-plans"
    temp_root.mkdir()
    fixtures = manifest["fixtures"]
    required_ids = set(manifest["required_fixture_ids"])
    results = [run_fixture(fixture, suite_dir, temp_root) for fixture in fixtures]
    passed = sum(1 for item in results if item["status"] == "pass")
    failures = [item["error"] for item in results if item["status"] == "fail"]
    required_passed = sum(1 for item in results if item["id"] in required_ids and item["status"] == "pass")
    required_failed = [item for item in results if item["id"] in required_ids and item["status"] == "fail"]
    summary = {
        "suite_id": suite_id,
        "fixture_count": len(fixtures),
        "required_fixture_count": len(required_ids),
        "required_passed": required_passed,
        "passed": passed,
        "failed": len(failures),
        "skipped": 0,
        "decision": "keep" if not required_failed and required_ids <= {item["id"] for item in results} else "kill",
        "failures": failures,
        "fixtures": results,
    }
    write_json_atomic(suite_dir / "summary.json", summary, root=suite_dir)
    if summary["decision"] != "keep":
        raise HudError("ERR_HUD_FIXTURE_FAILED", "manifest decision is kill", path=manifest_path)
    return summary


def self_test() -> None:
    HUD_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dwm-hud-self-test-", dir=HUD_ROOT) as tmp:
        summary = evaluate_manifest(ROOT / "fixtures" / "v17" / "manifest.json", Path(tmp) / "hud-self-test")
    if summary["decision"] != "keep":
        raise HudError("ERR_HUD_FIXTURE_FAILED", "HUD self-test manifest did not keep")
    print("dwm_hud self-test: pass")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run")
    parser.add_argument("--out")
    parser.add_argument("--manifest")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        elif args.manifest:
            if not args.out:
                raise HudError("ERR_HUD_PATH_UNSAFE", "--manifest requires --out")
            summary = evaluate_manifest(Path(args.manifest), Path(args.out))
            print(canonical_json_text({key: summary[key] for key in ["suite_id", "fixture_count", "required_fixture_count", "required_passed", "passed", "failed", "skipped", "decision"]}))
        elif args.run:
            if not args.out:
                raise HudError("ERR_HUD_PATH_UNSAFE", "--run requires --out")
            summary = summarize_fanout(Path(args.run), Path(args.out))
            print(canonical_json_text(summary))
        else:
            parser.error("expected --self-test, --manifest, or --run")
    except (HudError, RunnerError, CompileError) as exc:
        record = exc.to_record() if isinstance(exc, (HudError, RunnerError)) else {"code": exc.code, "message": exc.message, "path": exc.path}
        print(canonical_json_text(record), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
