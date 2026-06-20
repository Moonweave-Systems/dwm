from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from keelplane_loop import run_manifest  # noqa: E402


def test_render_artifact_is_recorded_in_phase_evidence() -> None:
    out_dir = ROOT / "out" / "keelplane-loop" / "render-observe-artifact-evidence-test"

    summary = run_manifest(ROOT / "fixtures" / "keelplane-render" / "manifest.json", out_dir)

    assert summary["decision"] == "keep"
    journal = json.loads((out_dir / "correct" / "journal.json").read_text(encoding="utf-8"))
    phase = journal["phases"][0]
    artifacts = phase["target_artifacts"]
    chart = next(item for item in artifacts if item["path"] == "fixtures/keelplane-render/generated/chart.svg")
    assert chart["sha256"]
    assert chart["byte_count"] > 0
