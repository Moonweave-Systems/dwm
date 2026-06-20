#!/usr/bin/env python3
"""Deterministic render-observe assertions for parseable SVG chart artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


LABEL_ATTRS = (
    "data-keelplane-label",
    "data-observed-label",
    "data-task-id",
    "data-label",
    "data-series-label",
)
VALUE_ATTRS = (
    "data-keelplane-value",
    "data-observed-value",
    "data-delta-seconds",
    "data-value",
    "data-series-value",
)
NUMBER_RE = re.compile(r"^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:s)?$")


def load_expected_rows(input_path: Path) -> list[tuple[str, float]]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    rows = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        raise AssertionError(f"{input_path} must contain a non-empty rows list")

    expected: list[tuple[str, float]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AssertionError(f"row {index} must be an object")
        label = row.get("task_id", row.get("label"))
        value = row.get("delta_seconds", row.get("value"))
        if not isinstance(label, str) or not label:
            raise AssertionError(f"row {index} must declare task_id or label")
        if not isinstance(value, int | float):
            raise AssertionError(f"row {index} must declare a numeric delta_seconds or value")
        expected.append((label, float(value)))
    return expected


def parse_svg(artifact_path: Path) -> ET.Element:
    if not artifact_path.is_file():
        raise AssertionError(f"artifact is missing: {artifact_path}")
    text = artifact_path.read_text(encoding="utf-8")
    if not text.strip():
        raise AssertionError(f"artifact is empty: {artifact_path}")
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        raise AssertionError(f"artifact is not parseable SVG/XML: {artifact_path}: {exc}") from exc


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def attr_value(element: ET.Element, candidates: tuple[str, ...]) -> str | None:
    for key in candidates:
        value = element.attrib.get(key)
        if value is not None:
            return value
    return None


def observed_from_data_attrs(root: ET.Element) -> list[tuple[str, float]]:
    observed: list[tuple[str, float]] = []
    for element in root.iter():
        label = attr_value(element, LABEL_ATTRS)
        raw_value = attr_value(element, VALUE_ATTRS)
        if label is None or raw_value is None:
            continue
        observed.append((label, parse_number(raw_value)))
    return observed


def parse_number(value: str) -> float:
    normalized = value.strip()
    if normalized.endswith("s"):
        normalized = normalized[:-1]
    try:
        return float(normalized)
    except ValueError as exc:
        raise AssertionError(f"observed value is not numeric: {value!r}") from exc


def text_nodes(root: ET.Element) -> list[str]:
    values: list[str] = []
    for element in root.iter():
        if local_name(element.tag) != "text":
            continue
        if element.text is None:
            continue
        text = element.text.strip()
        if text:
            values.append(text)
    return values


def observed_from_text_labels(root: ET.Element, expected: list[tuple[str, float]]) -> list[tuple[str, float]]:
    texts = text_nodes(root)
    expected_labels = [label for label, _value in expected]
    labels = [text for text in texts if text in expected_labels]
    values = [parse_number(text) for text in texts if NUMBER_RE.match(text)]
    if len(labels) != len(expected) or len(values) != len(expected):
        return []
    return list(zip(labels, values, strict=True))


def assert_observed_rows(expected: list[tuple[str, float]], observed: list[tuple[str, float]]) -> None:
    if not observed:
        raise AssertionError("artifact has no observable embedded chart values")
    if [label for label, _value in observed] != [label for label, _value in expected]:
        raise AssertionError(f"observed labels {observed!r} do not match expected {expected!r}")
    mismatches: list[str] = []
    for (label, expected_value), (_observed_label, observed_value) in zip(expected, observed, strict=True):
        if abs(observed_value - expected_value) > 0.000001:
            mismatches.append(f"{label}: expected {expected_value}, observed {observed_value}")
    if mismatches:
        raise AssertionError("observed chart values do not match declared input: " + "; ".join(mismatches))


def assert_svg_observes_input(*, artifact_path: Path, input_path: Path) -> None:
    expected = load_expected_rows(input_path)
    root = parse_svg(artifact_path)
    observed = observed_from_data_attrs(root)
    if not observed:
        observed = observed_from_text_labels(root, expected)
    assert_observed_rows(expected, observed)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assert an SVG chart observes declared input data")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--input", required=True)
    args = parser.parse_args(argv)
    try:
        assert_svg_observes_input(artifact_path=Path(args.artifact), input_path=Path(args.input))
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
