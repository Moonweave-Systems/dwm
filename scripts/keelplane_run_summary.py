#!/usr/bin/env python3
"""Write a Keelplane run status summary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Surface whichever status fields exist; loop runs use terminal_state/
# verified_phase_count, older status records use decision/valid.
SUMMARY_STATUS_KEYS = ("terminal_state", "verified_phase_count", "decision", "valid")


def write_summary(run_dir: Path, out_path: Path) -> dict[str, Any]:
    status = read_json(run_dir / "status.json")
    summary: dict[str, Any] = {
        "artifact_count": sum(1 for path in run_dir.iterdir() if path.is_file()),
        "source_hash": hash_file(run_dir / "source.txt"),
    }
    for key in SUMMARY_STATUS_KEYS:
        if key in status:
            summary[key] = status[key]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "run"
        run_dir.mkdir()
        (run_dir / "status.json").write_text(
            json.dumps(
                {"terminal_state": "verified-complete", "verified_phase_count": 2}
            ),
            encoding="utf-8",
        )
        (run_dir / "source.txt").write_text("data", encoding="utf-8")
        out_path = Path(tmp) / "summary.json"
        summary = write_summary(run_dir, out_path)
        assert summary["terminal_state"] == "verified-complete"
        assert summary["verified_phase_count"] == 2
        assert "decision" not in summary  # absent keys are not surfaced as null
        assert summary["artifact_count"] == 2
        assert summary["source_hash"] is not None
        assert json.loads(out_path.read_text())["terminal_state"] == "verified-complete"
    print("keelplane_run_summary self-test: pass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--run",
        type=Path,
        help="Keelplane run directory containing status.json",
    )
    parser.add_argument("--out", type=Path, help="Path to write summary JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.run is None or args.out is None:
        raise SystemExit("--run and --out are required unless --self-test is used")
    write_summary(args.run, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
