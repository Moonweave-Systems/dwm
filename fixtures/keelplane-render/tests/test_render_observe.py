from __future__ import annotations

import sys
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from keelplane_render_observe_assert import assert_svg_observes_input  # noqa: E402


def test_generated_chart_observes_declared_input_values() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "fixtures" / "keelplane-render" / "generated" / "chart_generator.py"),
            "--input",
            str(ROOT / "fixtures" / "keelplane-render" / "input-data.json"),
            "--out",
            str(ROOT / "fixtures" / "keelplane-render" / "generated" / "chart.svg"),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stderr
    assert_svg_observes_input(
        artifact_path=ROOT / "fixtures" / "keelplane-render" / "generated" / "chart.svg",
        input_path=ROOT / "fixtures" / "keelplane-render" / "input-data.json",
    )
