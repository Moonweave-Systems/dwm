# V57 Dogfood Pair Spec

Status: implemented first gated dogfood comparison pair in
`scripts/dwm_dogfood_pair.py`.

## Research and Prior Art

V56 produced the first DWM-controlled measured local sample. The missing half
of a comparison is a direct Codex receipt, but running a live Codex task is a
risk gate. V57 therefore records a pair only from a human-gated direct receipt.

## Product Position and Non-Goals

V57 is a pair builder. It does not execute Codex. It validates that a direct
Codex receipt has human approval, matching task id, evidence, metrics, and no
public superiority claim.

Non-goals:

- do not run live Codex,
- do not infer direct measurements from DWM measurements,
- do not publish README benchmark graphs,
- do not claim direct-agent superiority,
- do not accept missing or ungated direct Codex receipts.

## Workflow Architecture

The command is:

```bash
python scripts/dwm_dogfood_pair.py pair --dwm-measure out/dogfood-measurements/<measurement_id> --direct-receipt direct-receipt.json --out out/dogfood-pairs/<pair_id>
```

It reads:

- V56 `measurement.json`,
- a direct Codex receipt with `human_gate.approved: true`,
- direct Codex evidence file.

It writes:

- `comparison-pair.json`,
- `comparison-pair.md`,
- `pair-status.json`.

## Safety and Verification Gates

The gate blocks:

- `ERR_DOGFOOD_PAIR_GATE_MISSING` when direct Codex approval is absent,
- `ERR_DOGFOOD_PAIR_TASK_MISMATCH` when task ids differ,
- `ERR_DOGFOOD_PAIR_EVIDENCE_MISSING` when direct evidence is absent,
- `ERR_DOGFOOD_PAIR_OVERCLAIM` when the receipt includes superiority or public
  benchmark claims,
- `ERR_DOGFOOD_PAIR_MEASURE_INVALID` when the DWM measurement is not a recorded
  DWM-controlled sample.

## Evaluation Fixtures

`fixtures/v57/manifest.json` covers:

- positive: one comparison pair is recorded,
- negative: missing human gate is blocked,
- negative: task mismatch is blocked,
- negative: missing evidence is blocked,
- negative: overclaim text is blocked.

## Release Plan

V57 creates a first local pair artifact, not a public trend. A later slice can
collect multiple pairs and only then evaluate whether a graph candidate is
statistically and operationally meaningful.
