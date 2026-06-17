# V47 Real Dogfood Corpus Spec

Status: implemented first real dogfood corpus recorder in
`scripts/dwm_dogfood_corpus.py`.

## Research and Prior Art

The benchmark path is now protected by review and promotion gates, but useful
upward evidence still needs real tasks. V47 defines a local dogfood corpus from
actual DWM maintenance work and records comparison slots without pretending that
the comparisons have already run.

## Product Position and Non-Goals

V47 is a corpus recorder. It creates local dogfood task definitions, comparison
mode placeholders, evidence requirements, and a V46 queue handoff.

Non-goals:

- do not execute direct Codex or DWM-controlled attempts,
- do not claim external benchmark authority,
- do not publish README graphs,
- do not include unsafe, networked, secret, deployment, or destructive tasks,
- do not turn `not-run` comparison slots into success claims.

## Workflow Architecture

`scripts/dwm_dogfood_corpus.py` writes:

- `dogfood-corpus.json`,
- `status.json`,
- `queue-packets.json`,
- `README.md`,
- a linked V46 `queue.json`,
- `summary.json` for manifest suites.

Each dogfood task records repo paths, evidence requirements, verification
commands, risk codes, and comparison slots for `direct-codex` and
`dwm-controlled`. Comparison slots start as `not-run`.

## Execution Model

```bash
python scripts/dwm_dogfood_corpus.py record --out out/dogfood-corpus/<corpus_id>
python scripts/dwm_dogfood_corpus.py --manifest fixtures/v47/manifest.json --out out/dogfood-corpus/v47-final
```

Every output directory is guarded by a dogfood-corpus ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_DOGFOOD_CORPUS_REQUIRED_TASK_MISSING` when the required local dogfood
  task set is incomplete,
- `ERR_DOGFOOD_CORPUS_UNSAFE_TASK` when risk codes include write, delete,
  network, deploy, secret, dependency, database, history rewrite, or external
  message,
- `ERR_DOGFOOD_CORPUS_PUBLIC_CLAIM` when a task attempts to make a public
  benchmark claim,
- `ERR_DOGFOOD_CORPUS_EVIDENCE_MISSING` when a task lacks evidence
  requirements,
- `ERR_DOGFOOD_CORPUS_TASK_INVALID` when task shape is malformed.

## Evaluation Fixtures

`fixtures/v47/manifest.json` covers:

- positive: corpus records local dogfood tasks and queue packets,
- negative: missing required task is blocked,
- negative: unsafe task is blocked,
- negative: public claim is blocked,
- negative: missing evidence requirements are blocked.

## Release Plan

V47 records the local corpus and queues it for later work. V48 can turn this
into a daily operator loop, and later slices can run attempts while preserving
the `not-run` versus measured-result boundary.
