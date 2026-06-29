from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from depone.agent_fabric.claim_gate import canonical_hash
from depone.agent_fabric.observe import (
    build_separated_observer_capture,
    canonical_json_pretty,
    enforce_path_outside_runner_sandbox,
    write_observer_capture,
)
from depone.cli._response import EXIT_INTERNAL, emit_error, emit_result
from depone.agent_fabric.paired_run import PairedRunError
from depone.agent_fabric.seal import seal_capture


DEFAULT_SEAL_KEY_ID = "observer-held-key"


def _seal_path_for_capture(out_path: Path) -> Path:
    return out_path.expanduser().resolve(strict=False).with_suffix(".seal.json")


def _observer_seal_config(args: argparse.Namespace) -> tuple[bytes, str] | None:
    key_file = str(getattr(args, "seal_key_file", "") or "")
    env_key = os.environ.get("DEPONE_OBSERVER_SEAL_KEY")
    key_id = (
        str(getattr(args, "seal_key_id", "") or "")
        or os.environ.get("DEPONE_OBSERVER_SEAL_KEY_ID", "")
        or DEFAULT_SEAL_KEY_ID
    )
    if key_file:
        key_path = enforce_path_outside_runner_sandbox(
            runner_sandbox=Path(str(getattr(args, "runner_sandbox", ""))),
            path=Path(key_file),
            label="--seal-key-file",
        )
        return key_path.read_bytes(), key_id
    if env_key is not None:
        return env_key.encode("utf-8"), key_id
    return None


def run(args: argparse.Namespace) -> None:
    if getattr(args, "self_test", False):
        _self_test()
        return

    command = list(getattr(args, "verification_command", []) or [])
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        emit_error(
            args,
            code="ERR_OBSERVE_USAGE",
            message=(
                "Usage: depone observe --runner-sandbox <dir> "
                "--source-fixture-hash <hash> --out <observer-capture.json> "
                "--log <verify-log.json> -- <verification command>"
            ),
        )
    if not str(getattr(args, "runner_sandbox", "")):
        emit_error(
            args,
            code="ERR_OBSERVE_RUNNER_SANDBOX_REQUIRED",
            message="--runner-sandbox is required",
        )
    if not str(getattr(args, "source_fixture_hash", "")):
        emit_error(
            args,
            code="ERR_OBSERVE_SOURCE_FIXTURE_HASH_REQUIRED",
            message="--source-fixture-hash is required",
        )

    try:
        seal_config = _observer_seal_config(args)
        capture = build_separated_observer_capture(
            runner_sandbox=Path(str(getattr(args, "runner_sandbox", ""))),
            source_fixture_hash=str(getattr(args, "source_fixture_hash", "")),
            verification_command=command,
            out_path=Path(str(getattr(args, "out", ""))),
            log_path=Path(str(getattr(args, "log", ""))),
            timeout_seconds=int(getattr(args, "timeout_seconds", 120)),
        )
        out_path = Path(str(getattr(args, "out")))
        capture_hash = write_observer_capture(out_path, capture)
        seal: dict[str, object] | None = None
        seal_path: Path | None = None
        if seal_config is not None:
            key, key_id = seal_config
            seal = seal_capture(capture, key, key_id=key_id)
            seal_path = _seal_path_for_capture(out_path)
            seal_path.write_text(canonical_json_pretty(seal), encoding="utf-8")
    except PairedRunError as exc:
        record = exc.to_record()
        emit_error(
            args,
            code=str(record.get("code", "ERR_OBSERVER_CAPTURE_FAILED")),
            message=str(record.get("message", exc)),
            path=record.get("path"),
        )
    except Exception as exc:
        emit_error(
            args,
            code="ERR_OBSERVER_CAPTURE_FAILED",
            message=str(exc),
            exit_code=EXIT_INTERNAL,
        )

    payload = {
        "command": "observe",
        "decision": "pass",
        "out": str(Path(str(getattr(args, "out")))),
        "log": str(Path(str(getattr(args, "log")))),
        "observer_capture_hash": capture_hash,
        "canonical_hash": canonical_hash(capture),
        "seal": str(seal_path) if seal_path is not None else None,
    }
    human = [
        f"Observer capture written to {Path(str(getattr(args, 'out')))}",
        f"  observer_capture_hash: {capture_hash}",
        f"  canonical_hash: {canonical_hash(capture)}",
    ]
    if seal is not None and seal_path is not None:
        human.extend(
            [
                f"  observer_capture_seal: {seal_path}",
                f"  seal_value: {seal['value']}",
            ]
        )
    emit_result(args, payload, human=human)


def _self_test() -> None:
    from depone.agent_fabric.observe import _self_test as observe_self_test

    observe_self_test()
