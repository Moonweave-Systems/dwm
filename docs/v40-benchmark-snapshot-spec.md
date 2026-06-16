# V40 Benchmark Snapshot Spec

Status: implemented first release benchmark snapshot recorder in
`scripts/dwm_benchmark_snapshot.py`.

## Research and Prior Art

Meaningful benchmark trends need stable observations, not hand-picked report
folders. V38 can build a history ledger and V39 can decide whether a history is
promotable. V40 adds the missing release-grade observation: a benchmark snapshot
that binds a V35 report to a release id, git commit, score metrics, and report
hash.

## Product Position and Non-Goals

V40 records release benchmark snapshots for DWM's own evidence pipeline. A
snapshot can feed V38 history as `source_kind: release`.

Non-goals:

- do not execute benchmark attempts,
- do not invent release ids,
- do not accept stale report hashes,
- do not promote README trend graphs,
- do not claim external benchmark authority.

## Workflow Architecture

`scripts/dwm_benchmark_snapshot.py` reads one V35 report directory and writes:

- `snapshot.json`,
- `status.json`,
- `summary.json` for manifest suites.

`snapshot.json` records `release_id`, `git_commit`, `source_kind: release`,
`graph_metrics`, `score_bps`, and the source report hash.

V38 history can consume snapshots with:

```bash
python scripts/dwm_benchmark_history.py build --snapshot out/benchmark-snapshots/<snapshot_id> --out out/benchmark-history/<history_id>
```

## Execution Model

```bash
python scripts/dwm_benchmark_snapshot.py record --report out/live-reports/<report_id> --release-id <release_id> --out out/benchmark-snapshots/<snapshot_id>
python scripts/dwm_benchmark_snapshot.py --manifest fixtures/v40/manifest.json --out out/benchmark-snapshots/v40-final
```

Every output directory is guarded by a benchmark-snapshot ownership sentinel.

## Safety and Verification Gates

The gate blocks:

- `ERR_BENCHMARK_SNAPSHOT_ARTIFACT_MISSING` when report artifacts are missing,
- `ERR_BENCHMARK_SNAPSHOT_RELEASE_ID_MISSING` when release id is empty,
- `ERR_BENCHMARK_SNAPSHOT_STALE_REPORT` when report/status artifacts drift or an
  expected report hash does not match,
- `ERR_BENCHMARK_SNAPSHOT_METRICS_INVALID` when graph metrics are incomplete or
  internally inconsistent.

## Evaluation Fixtures

`fixtures/v40/manifest.json` covers:

- positive: report becomes a release snapshot,
- negative: missing release id is blocked,
- negative: stale report hash is blocked,
- negative: invalid metrics are blocked,
- negative: missing report artifact is blocked.

## Release Plan

V40 makes future README trend lines grounded in release snapshots. A later
workflow can gather three or more real release snapshots, build a V38 history,
pass V39 promotion, and only then publish a public trend graph.
