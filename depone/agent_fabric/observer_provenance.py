"""Trusted observer provenance records for report-level assurance.

Capture manifests are content-addressed evidence, but a manifest in a generic
evidence directory is still runner-controlled input. Report-level A1/A2
therefore requires a separate trusted record created by the observer/operator
after verifying an observer-held seal.
"""

from __future__ import annotations

from typing import Any

from depone.agent_fabric.claim_gate import canonical_hash
from depone.agent_fabric.seal import ALG, verify_capture_seal

PROVENANCE_KIND = "trusted-observer-provenance"
PROVENANCE_SCHEMA_VERSION = "1.0"
ERR_TRUSTED_PROVENANCE_MISSING = "trusted observer provenance missing"
ERR_TRUSTED_PROVENANCE_MISMATCH = "trusted observer provenance mismatch"


def build_trusted_observer_provenance(
    manifest: dict[str, Any],
    *,
    evidence_path: str,
    seal: dict[str, Any],
    key: bytes,
) -> dict[str, Any]:
    """Build a trusted side-channel record for an exact capture manifest."""

    observer_capture = manifest.get("observer_capture")
    verified = verify_capture_seal(
        observer_capture if isinstance(observer_capture, dict) else {},
        seal,
        key,
    )
    return {
        "kind": PROVENANCE_KIND,
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "evidence_path": evidence_path,
        "manifest_hash": canonical_hash(manifest),
        "observer_capture_hash": manifest.get("observer_capture_hash"),
        "scheme": seal.get("alg"),
        "key_id": seal.get("key_id"),
        "seal": dict(seal),
        "verified": verified,
    }


def validate_trusted_observer_provenance(
    manifest: dict[str, Any],
    *,
    evidence_path: str,
    provenance: Any,
    key: bytes | None,
) -> list[str]:
    """Return errors unless trusted provenance matches this manifest exactly."""

    records = _records(provenance)
    if not records:
        return [ERR_TRUSTED_PROVENANCE_MISSING]

    saw_candidate = False
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("evidence_path") != evidence_path:
            continue
        saw_candidate = True
        errors = _record_errors(
            manifest,
            evidence_path=evidence_path,
            record=record,
            key=key,
        )
        if not errors:
            return []

    if saw_candidate:
        return [ERR_TRUSTED_PROVENANCE_MISMATCH]
    return [ERR_TRUSTED_PROVENANCE_MISSING]


def _records(provenance: Any) -> list[Any]:
    if isinstance(provenance, list):
        return provenance
    if isinstance(provenance, dict):
        nested = provenance.get("trusted_observer_provenance")
        if isinstance(nested, list):
            return nested
        return [provenance]
    return []


def _record_errors(
    manifest: dict[str, Any],
    *,
    evidence_path: str,
    record: dict[str, Any],
    key: bytes | None,
) -> list[str]:
    errors: list[str] = []
    if record.get("kind") != PROVENANCE_KIND:
        errors.append("trusted observer provenance kind mismatch")
    if record.get("schema_version") != PROVENANCE_SCHEMA_VERSION:
        errors.append("trusted observer provenance schema_version mismatch")
    if record.get("evidence_path") != evidence_path:
        errors.append("trusted observer provenance evidence_path mismatch")
    if record.get("manifest_hash") != canonical_hash(manifest):
        errors.append("trusted observer provenance manifest_hash mismatch")
    if record.get("observer_capture_hash") != manifest.get("observer_capture_hash"):
        errors.append("trusted observer provenance observer_capture_hash mismatch")
    if record.get("scheme") != ALG:
        errors.append("trusted observer provenance scheme mismatch")
    if record.get("verified") is not True:
        errors.append("trusted observer provenance not verified")
    seal = record.get("seal")
    if not isinstance(seal, dict):
        errors.append("trusted observer provenance seal missing")
    if not isinstance(key, bytes) or not key:
        errors.append("trusted observer provenance key missing")
    elif isinstance(seal, dict):
        observer_capture = manifest.get("observer_capture")
        if not isinstance(observer_capture, dict) or not verify_capture_seal(
            observer_capture,
            seal,
            key,
        ):
            errors.append("trusted observer provenance seal verification failed")
    return errors
