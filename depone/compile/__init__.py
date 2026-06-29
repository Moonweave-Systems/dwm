"""Compile workflow plans into target framework formats.

Supported targets:
  - conductor: Microsoft Conductor workflow YAML
  - langgraph: stub (not yet implemented in V104.0)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from depone.cli._response import emit_error, emit_result
from depone.compile import agent_fabric, conductor


def run(args: argparse.Namespace) -> None:
    """Dispatch compile to the appropriate target emitter."""
    # Self-test bypasses target requirement
    if getattr(args, "self_test", False):
        conductor.run(args)
        agent_fabric._self_test()
        return

    target = args.target
    if not args.plan:
        emit_error(
            args,
            code="ERR_COMPILE_USAGE",
            message="Usage: depone compile <plan.json> --target conductor [--out workflow.yaml]",
        )

    if target is None:
        emit_error(
            args,
            code="ERR_COMPILE_TARGET_REQUIRED",
            message="--target is required (choices: conductor, langgraph, agent-fabric)",
        )

    if target == "conductor":
        conductor.run(args)
    elif target == "agent-fabric":
        _run_agent_fabric(args)
    elif target == "langgraph":
        emit_error(
            args,
            code="ERR_COMPILE_TARGET_UNIMPLEMENTED",
            message="langgraph compile is not implemented",
        )
    else:
        emit_error(
            args,
            code="ERR_COMPILE_TARGET_UNKNOWN",
            message=f"unknown compile target: {target}",
        )


def _read_json(args: argparse.Namespace, path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        emit_error(
            args,
            code="ERR_COMPILE_READ_JSON",
            message=f"cannot read JSON {path}: {exc}",
            path=path,
        )


def _load_role_contracts(args: argparse.Namespace, paths: list[str]) -> list[dict[str, Any]]:
    role_contracts: list[dict[str, Any]] = []
    if not paths:
        emit_error(
            args,
            code="ERR_COMPILE_ROLES_REQUIRED",
            message="--target agent-fabric requires at least one --roles JSON path",
        )

    for value in paths:
        data = _read_json(args, Path(value))
        if isinstance(data, dict) and isinstance(data.get("roles"), list):
            role_contracts.extend(item for item in data["roles"] if isinstance(item, dict))
        elif isinstance(data, list):
            role_contracts.extend(item for item in data if isinstance(item, dict))
        elif isinstance(data, dict):
            role_contracts.append(data)
        else:
            emit_error(
                args,
                code="ERR_COMPILE_ROLE_CONTRACT_ROOT",
                message=f"role contract JSON root must be an object or list: {value}",
                path=value,
            )

    return role_contracts


def _run_agent_fabric(args: argparse.Namespace) -> None:
    profile = _read_json(args, Path(args.plan))
    if not isinstance(profile, dict):
        emit_error(
            args,
            code="ERR_COMPILE_AGENT_FABRIC_PROFILE",
            message="Agent Fabric profile JSON root must be an object",
            path=args.plan,
        )

    role_contracts = _load_role_contracts(args, list(getattr(args, "roles", [])))
    bundle = agent_fabric.compile_agent_fabric(
        profile,
        str(getattr(args, "harness", "shell")),
        role_contracts,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    emit_result(
        args,
        {
            "command": "compile",
            "decision": "pass",
            "target": "agent-fabric",
            "out": str(out_path),
        },
        human=[f"Agent Fabric bundle written to {out_path}"],
    )
