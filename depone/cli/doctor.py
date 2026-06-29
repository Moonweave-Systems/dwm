from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from depone import __version__
from depone._resources import resource_text
from depone.cli._response import emit_result, EXIT_FAILED


def build_report() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    version_ok = sys.version_info >= (3, 10)
    add("python-version", version_ok, sys.version.split()[0])

    try:
        text = resource_text("fixtures/agent_fabric/reference_adapter_shell.json")
        add("package-fixture", bool(text.strip()), "reference_adapter_shell.json")
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        add("package-fixture", False, str(exc))

    try:
        with tempfile.TemporaryDirectory(prefix="depone-doctor-") as temp_dir:
            probe = Path(temp_dir) / "probe.txt"
            probe.write_text("ok\n", encoding="utf-8")
            add("temp-write", probe.read_text(encoding="utf-8").strip() == "ok", temp_dir)
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        add("temp-write", False, str(exc))

    stdout_encoding = sys.stdout.encoding or ""
    stderr_encoding = sys.stderr.encoding or ""
    console_warning = not (
        "utf" in stdout_encoding.lower() or stdout_encoding.lower() == "cp65001"
    )
    add(
        "console-encoding",
        True,
        f"stdout={stdout_encoding or 'unknown'} stderr={stderr_encoding or 'unknown'}",
    )

    ok = all(bool(item["ok"]) for item in checks)
    return {
        "command": "doctor",
        "version": __version__,
        "decision": "pass" if ok else "fail",
        "ok": ok,
        "checks": checks,
        "warnings": (
            ["stdout is not UTF-8; human output is ASCII-safe, JSON escapes non-ASCII"]
            if console_warning
            else []
        ),
    }


def run(args: argparse.Namespace) -> None:
    if getattr(args, "self_test", False):
        report = build_report()
        if not report["ok"]:
            raise AssertionError(report)
        print("depone doctor --self-test: pass")
        return

    report = build_report()
    emit_result(
        args,
        report,
        human=[
            f"Depone doctor: {'ok' if report['ok'] else 'failed'}",
            *[
                f"- {'ok' if item['ok'] else 'fail'}: {item['name']} ({item['detail']})"
                for item in report["checks"]  # type: ignore[index]
            ],
            *[f"- warning: {warning}" for warning in report["warnings"]],  # type: ignore[index]
        ],
    )
    if not report["ok"]:
        sys.exit(EXIT_FAILED)
