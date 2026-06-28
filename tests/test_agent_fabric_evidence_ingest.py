from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from depone.agent_fabric.evidence_substrate import ingest_external_evidence


class AgentFabricEvidenceIngestTests(unittest.TestCase):
    def _bundle(self) -> dict[str, object]:
        return json.loads(
            Path("out/v128-real-dogfood/evidence-substrate-bundle.json").read_text(
                encoding="utf-8"
            )
        )

    def _artifact_paths(self) -> dict[str, str]:
        return {
            "source_fixture": "depone/fixtures/agent_fabric/reference_adapter_shell.json",
            "depone-capture-manifest": "out/v128-real-dogfood/capture-manifest.json",
            "observer_capture": "out/v128-real-dogfood/observer-capture.json",
        }

    def test_pass_when_all_real_bundle_subjects_match_disk(self) -> None:
        bundle = self._bundle()

        verdict = ingest_external_evidence(
            bundle["dsse_envelope"],
            self._artifact_paths(),
            otel_spans=bundle["otel_spans"],
        )

        self.assertEqual(verdict["decision"], "pass")
        self.assertEqual(verdict["verified_subject_count"], 3)
        self.assertFalse(verdict["boundary"]["raises_assurance"])
        self.assertFalse(verdict["boundary"]["trusts_external_signature"])

    def test_inconclusive_when_subject_artifact_is_absent(self) -> None:
        bundle = self._bundle()

        verdict = ingest_external_evidence(
            bundle["dsse_envelope"],
            {"source_fixture": self._artifact_paths()["source_fixture"]},
        )

        self.assertEqual(verdict["decision"], "inconclusive")
        self.assertIn(
            "missing",
            {result["status"] for result in verdict["subject_results"]},
        )

    def test_blocked_when_present_artifact_hash_mismatches(self) -> None:
        bundle = self._bundle()
        artifact_paths = self._artifact_paths()

        with tempfile.TemporaryDirectory() as temp_dir:
            tampered_path = Path(temp_dir) / "reference_adapter_shell.json"
            tampered_path.write_text('{"tampered": true}\n', encoding="utf-8")
            artifact_paths["source_fixture"] = str(tampered_path)
            verdict = ingest_external_evidence(bundle["dsse_envelope"], artifact_paths)

        self.assertEqual(verdict["decision"], "blocked")
        self.assertIn(
            "mismatch",
            {result["status"] for result in verdict["subject_results"]},
        )

    def test_blocked_when_dsse_claims_unverifiable_signatures(self) -> None:
        bundle = self._bundle()
        envelope = dict(bundle["dsse_envelope"])
        envelope["signatures"] = [{"keyid": "unknown", "sig": "claimed"}]

        verdict = ingest_external_evidence(envelope, self._artifact_paths())

        self.assertEqual(verdict["decision"], "blocked")
        self.assertEqual(verdict["signing_status"], "unverifiable-signature")

    def test_blocked_when_dsse_is_malformed_without_raise(self) -> None:
        verdict = ingest_external_evidence(
            {
                "payloadType": "application/vnd.in-toto+json",
                "payload": "not base64",
                "signatures": [],
            },
            self._artifact_paths(),
        )

        self.assertEqual(verdict["decision"], "blocked")

    def test_otel_structural_errors_do_not_upgrade_to_pass(self) -> None:
        bundle = self._bundle()

        verdict = ingest_external_evidence(
            bundle["dsse_envelope"],
            self._artifact_paths(),
            otel_spans=[{"trace_id": "trace"}],
        )

        self.assertEqual(verdict["decision"], "blocked")
        self.assertTrue(verdict["otel_errors"])


if __name__ == "__main__":
    unittest.main()
