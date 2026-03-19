# DetTrace

> Deterministic replay + distributed incident forensics for reconstructing cross-service failure timelines.

---

DetTrace reconstructs distributed failure sequences into replayable, comparable, and explainable timelines. Originally built for deterministic concurrency replay and divergence analysis, it now extends that model to distributed incident forensics: request/span causality reconstruction, timeout-chain analysis, retry amplification detection, failover edge-case replay, blast-radius inference, and semantic incident diffing.

---

## Current Scope

- 4 replayable distributed incident packs
- 10+ network, transport, and recovery annotations
- OTEL-style span ingestion into a deterministic replay model
- semantic incident diffing across baseline and candidate runs
- blast-radius inference across upstream and downstream services
- 2 end-to-end test paths covering original replay and distributed incident analysis

---

## Why DetTrace

Distributed incidents are easy to observe but hard to explain.

A request fails at the edge. Retries amplify load. A downstream dependency becomes unavailable. Logs across services show only fragments.

DetTrace reconstructs those fragments into replayable failure timelines so you can identify the first failing hop, understand propagation across services, and compare incident regressions semantically across runs.

**Questions DetTrace answers:**

- Which downstream hop failed first?
- Was this a timeout cascade or a retry storm?
- Did failure propagate through request/span lineage?
- Did failover reduce blast radius or create misordered recovery?
- Was this more consistent with DNS, transport, dependency, or latency inflation symptoms?

---

## Quick Start

**Original deterministic replay demo:**
```bash
./scripts/run_demo.sh
```

**Distributed incident replay demo:**
```bash
./scripts/run_distributed_demo.sh
```

The distributed demo builds the incident path, generates replay packs, writes annotated cross-service traces, ingests OTEL-style sample spans, and emits a structured incident report plus semantic diff.

---

## What DetTrace Does

### Core replay and divergence analysis

- Generates an expected concurrent execution trace and validates invariants against it
- Validates execution against an expected ordering during guarded replay
- Detects the **first point of divergence** deterministically
- Saves divergent trace artifacts even when replay throws, preserving failure context
- Produces a structured divergence report identifying the mismatched events

### Distributed incident analysis

- Reconstructs cross-service timelines using request IDs, span IDs, and parent-span lineage
- Ingests OTEL-style span records into a replayable distributed event model
- Annotates traces with network and transport symptoms
- Replays baseline incident timelines deterministically
- Correlates incidents with deploy and error-burst timing windows
- Infers blast radius across upstream callers and downstream dependencies
- Produces semantic incident diffs and operator-oriented runbook guidance

---

## Original Replay Example

The original replay path includes a concrete flaky-case walkthrough in `examples/flaky_case_1/`.

Observed first divergence at event index `5`:

- Expected: `TASK_DEQUEUED task=1 worker=0 queue=0`
- Actual: `TASK_DEQUEUED task=2 worker=0 queue=0`

DetTrace catches the exact split point deterministically and preserves the divergent trace artifacts for inspection.

---

## Failure Modes Modeled

| Category | Failure Mode |
|---|---|
| Timeout | cascading timeouts, timeout chains |
| Retry | retry storms, retry amplification |
| Transport | TCP connect timeout, transport reset, cancellation propagation |
| Network | DNS failure, latency inflation between hops |
| Dependency | downstream unavailable, dependency failover edge cases |
| Recovery | misordered failure recovery |

These are modeled as replayable trace and event streams.

---

## Example Incident Topology

```
Client / Edge Proxy
        |
        v
   auth-service   ← first failing service
        |
        v
     token-db     ← downstream impact

Observed signals:
  dns_failure → retry → transport_reset → retry_burst → timeout_chain

Propagation:
  edge-proxy → auth-service → token-db
                |             ^
                +-- retries --+
                       |
                       +-- eventual timeout
```

---

## Example Incident Report

```json
{
  "incident_family": "retry_storm",
  "timeout_events": 1,
  "retry_events": 2,
  "network_error_events": 2,
  "failover_events": 0,
  "annotations": [
    "dns_failure",
    "transport_reset",
    "retry_burst",
    "downstream_unavailable",
    "latency_inflation_between_hops",
    "timeout_chain"
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

---

## Semantic Incident Diff

DetTrace compares baseline and candidate incidents at the service and failure-pattern level, not just raw event mismatch.

```json
{
  "baseline_first_failing_service": "profile-service",
  "candidate_first_failing_service": "auth-service",
  "baseline_first_failure_reason": "tcp_connect_timeout",
  "candidate_first_failure_reason": "dns_failure",
  "retry_delta": 2,
  "timeout_delta": -1,
  "network_error_delta": 2,
  "max_latency_delta_ms": -410
}
```

Surfaces: first failing service changes, failure-reason shifts, retry amplification deltas, timeout/network-error changes, and latency characteristic changes between runs.

---

## OTEL-Style Ingestion

DetTrace includes a JSONL ingest path that converts span-like records into replayable distributed events.

| Span field | Maps to |
|---|---|
| `trace_id` | `request_id` |
| `span_id` | `span_id` |
| `parent_span_id` | `parent_span_id` |
| `peer_service` | `downstream_service` |
| `start_ms` | `ts_ms` |

---

## Distributed Demo Outputs

| Output | Path |
|---|---|
| Replay packs | `packs/cascading_timeouts.jsonl`, `packs/retry_storm.jsonl`, `packs/misordered_recovery.jsonl`, `packs/failover_edge.jsonl` |
| Sample ingest | `samples/otel_spans.jsonl` |
| Annotated traces | `artifacts/baseline_annotated.jsonl`, `artifacts/candidate_annotated.jsonl`, `artifacts/otel_ingested_annotated.jsonl`, `artifacts/replayed_distributed.jsonl` |
| Incident report | `reports/distributed_incident_report.json` |
| Semantic diff | `reports/distributed_semantic_diff.json` |

---

## Running Tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

End-to-end coverage includes: original flaky replay validation, distributed incident replay, OTEL ingestion, annotation checks, timeline correlation, blast-radius inference, and semantic diff generation.

---

## Swift Companion Analyzer

`dettrace-swift/` is a Swift CLI companion that reads C++-generated trace artifacts concurrently using `async/await`, isolates analysis state with an `actor`, and generates structured JSON and Markdown divergence reports.

```bash
cd dettrace-swift
swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
```

---

## Diagnostics Viewer

A lightweight developer-facing UI in `viewer/` for inspecting execution differences.

- Side-by-side diff for passing vs. failing executions
- First-divergence highlighting
- Rule-based root-cause hints
- Invariant status exploration
- Reproducible scenarios and benchmark page

```bash
./scripts/serve_viewer.sh
# → http://localhost:8000/viewer/index.html
# → http://localhost:8000/viewer/benchmarks.html
```

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
  integration/     test_flaky_case_1 + distributed incident replay
  regression/
bench/             Overhead benchmarks
docs/
viewer/            Trace viewer
artifacts/         Generated trace files
packs/             Replayable distributed incident packs
reports/           Divergence and incident reports
samples/           Sample OTEL-style JSONL span input
dettrace-swift/    Swift companion analyzer
```

---

## Operator Runbook Output

DetTrace emits runbook-oriented guidance alongside replay artifacts:

1. Confirm request and span lineage; identify the first failing downstream hop
2. Correlate the incident with recent deploy, health-change, or failover windows
3. Inspect DNS, TCP connect, transport reset, and latency symptoms
4. Evaluate retry backoff and retry amplification
5. Review blast radius before rollback or traffic shift

---

## Positioning

DetTrace is **deterministic replay + distributed incident forensics**.

It is not a packet sniffer, not a router-control framework, and not a full observability platform. Its value is in making distributed failure sequences replayable, comparable, and explainable.

---

## Resume Angle

Built a C++ distributed incident-forensics framework that ingests OTEL-style spans, reconstructs cross-service failure timelines, detects retry amplification and transport-level divergence, infers blast radius, and semantically diffs timeout, retry, and failover regressions across baseline and candidate runs.

---

## License

MIT