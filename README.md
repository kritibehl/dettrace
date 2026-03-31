# DetTrace

> Deterministic replay and divergence analysis for isolating the first point of failure in concurrent and distributed execution traces.

---

Distributed failures are easy to observe. They're hard to explain.

A request fails at the edge. Retries amplify load. Logs show fragments — timeouts, resets, cascading errors — but none of them point to where the failure *actually started*. DetTrace answers that question.

It records expected execution, replays observed behavior under guard, isolates the exact event where the traces diverge, and preserves artifacts that make debugging and incident reconstruction possible.

DetTrace is a specialist debugging and incident-forensics tool for turning flaky or ambiguous failures into reproducible evidence.

---

## What DetTrace Does

- Detects the **first point of divergence** deterministically across concurrent and distributed traces
- Reconstructs cross-service failure timelines from span lineage and request IDs
- Ingests OTEL-style span records into a replayable distributed event model
- Annotates traces with network, transport, and recovery symptoms
- Produces semantic incident diffs comparing baseline and candidate runs
- Infers blast radius across upstream callers and downstream dependencies
- Emits operator-style incident reports and runbook guidance

---

## The Core Value

```
Expected:  {"seq":5,"type":"TASK_DEQUEUED","task":1,"worker":0,"queue":0}
Actual:    {"seq":5,"type":"TASK_DEQUEUED","task":2,"worker":0,"queue":0}
```

**First divergence isolated at event index `5`.**

Not just *that* the run failed — but *where* the execution first stopped matching expectation. Everything after that point is a downstream consequence, not the root cause.

---

## Without DetTrace vs With DetTrace

| Without | With DetTrace |
|---|---|
| Failure appears flaky and inconsistent | Failure becomes replayable |
| Logs show symptoms but not the first split | First divergence isolated deterministically |
| Later timeouts and retries obscure root cause | Earliest causal mismatch preserved as evidence |
| Distributed failures look ambiguous | Incident packs, annotations, and semantic diffs make propagation explainable |

---

## Quick Start

### Deterministic replay demo

```bash
./scripts/run_demo.sh
```

Builds the project, generates an expected trace, runs a divergent execution, isolates the first divergence, and writes a structured divergence report.

### Distributed incident replay demo

```bash
./scripts/run_distributed_demo.sh
```

Generates replayable incident packs, ingests OTEL-style sample spans, annotates network and transport symptoms, writes an incident report, and generates a semantic diff between baseline and candidate runs.

---

## Failure Modes Modeled

| Category | Failure Mode |
|---|---|
| Timeout | Cascading timeouts, timeout chains |
| Retry | Retry storms, retry amplification |
| Transport | TCP connect timeout, transport reset, cancellation propagation |
| Network | DNS failure, latency inflation between hops |
| Dependency | Downstream unavailable, dependency failover edge cases |
| Recovery | Misordered failure recovery |

---

## Example Incident Report

```json
{
  "incident_family": "retry_storm",
  "annotations": [
    "dns_failure", "transport_reset", "retry_burst",
    "downstream_unavailable", "latency_inflation_between_hops", "timeout_chain"
  ],
  "timeline_correlation": {
    "deploy_correlated": true,
    "suspected_trigger": "recent_deploy",
    "max_latency_ms": 900,
    "error_burst_count": 3
  },
  "blast_radius": {
    "root_service": "auth-service",
    "directly_impacted_services": ["token-db"],
    "upstream_services": ["edge-proxy"]
  }
}
```

## Example Semantic Diff

```json
{
  "baseline_first_failing_service": "profile-service",
  "candidate_first_failing_service": "auth-service",
  "baseline_first_failure_reason": "tcp_connect_timeout",
  "candidate_first_failure_reason": "dns_failure",
  "retry_delta": 2,
  "timeout_delta": -1,
  "max_latency_delta_ms": -410
}
```

This helps distinguish root-cause shifts from downstream symptom changes across runs.

---

## OTEL-Style Ingestion

DetTrace includes a JSONL ingest path that maps span records into its replay model:

| Span field | Maps to |
|---|---|
| `trace_id` | `request_id` |
| `span_id` | `span_id` |
| `parent_span_id` | `parent_span_id` |
| `peer_service` | `downstream_service` |
| `start_ms` | `ts_ms` |

---

## Artifacts Generated

| Artifact | Description |
|---|---|
| `artifacts/expected.jsonl` | Expected execution trace |
| `artifacts/actual.jsonl` | Observed execution trace |
| `artifacts/replayed.jsonl` | Replayed trace |
| `reports/divergence_report.json` | First-divergence report |
| `packs/*.jsonl` | Replayable distributed incident packs |
| `reports/distributed_incident_report.json` | Operator-style incident report |
| `reports/distributed_semantic_diff.json` | Semantic diff across runs |

---

## Running Tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

End-to-end coverage includes original flaky replay, distributed incident replay, OTEL ingestion, annotation checks, timeline correlation, blast-radius inference, and semantic diff generation.

---

## Swift Companion Analyzer

`dettrace-swift/` is a Swift CLI companion for inspecting trace artifacts outside the core C++ runtime. It reads generated trace files concurrently, compares traces, identifies divergence, and produces structured JSON and Markdown reports.

```bash
cd dettrace-swift
swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
```

---

## Diagnostics Viewer

A lightweight developer UI in `viewer/` for inspecting execution differences.

```bash
./scripts/serve_viewer.sh
# http://localhost:8000/viewer/index.html
# http://localhost:8000/viewer/benchmarks.html
```

Features side-by-side diff for passing vs failing executions, first-divergence highlighting, rule-based root-cause hints, and invariant status exploration.

---

## Repo Structure

```
analysis/          Divergence detection and invariant checking
trace/             Trace recording and serialization
replay/            Replay engine
examples/
  flaky_case_1/    Concrete ordering-divergence walkthrough
include/dettrace/  Public headers, distributed trace model
src/               Core implementation and distributed incident mode
scripts/           Demo runners and report helpers
tests/
  unit/
  integration/
  regression/
bench/             Overhead benchmarks
viewer/            Trace viewer
artifacts/         Generated trace files
packs/             Replayable distributed incident packs
reports/           Divergence and incident reports
samples/           Sample OTEL-style JSONL span input
dettrace-swift/    Swift companion analyzer
```

---

## Operator Runbook

DetTrace emits runbook guidance alongside replay artifacts:

1. Confirm request and span lineage; identify the first failing downstream hop
2. Correlate the incident with recent deploy, health-change, or failover windows
3. Inspect DNS, TCP connect, transport reset, and latency symptoms
4. Evaluate retry backoff and retry amplification
5. Review blast radius before rollback or traffic shift

---

## License

MIT
