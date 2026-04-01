# DetTrace

<<<<<<< HEAD
> Deterministic replay and divergence analysis for isolating the first point of failure in concurrent and distributed execution traces.
=======
<<<<<<< HEAD
**Deterministic replay and distributed incident forensics for reconstructing cross-service failure timelines.**

![GitHub Repo stars](https://img.shields.io/github/stars/kritibehl/dettrace?style=social)

**DetTrace tells you which service failed first and how the failure spread.**

It reconstructs distributed failures into replayable timelines — finding the first failing hop, explaining propagation across services, and producing semantic incident diffs that show *how* failures changed between runs.
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

---

Distributed failures are easy to observe. They're hard to explain.

A request fails at the edge. Retries amplify load. Logs show fragments — timeouts, resets, cascading errors — but none of them point to where the failure *actually started*. DetTrace answers that question.

<<<<<<< HEAD
It records expected execution, replays observed behavior under guard, isolates the exact event where the traces diverge, and preserves artifacts that make debugging and incident reconstruction possible.

DetTrace is a specialist debugging and incident-forensics tool for turning flaky or ambiguous failures into reproducible evidence.

---

## What DetTrace Does
=======
Originally built for deterministic concurrency replay, DetTrace now extends that model to distributed incident forensics: request/span causality reconstruction, timeout-chain analysis, retry amplification detection, blast-radius inference, and semantic incident diffing.
=======
> Deterministic replay and divergence analysis for isolating the first point of failure in concurrent and distributed execution traces.

---

Distributed failures are easy to observe. They're hard to explain.
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)

A request fails at the edge. Retries amplify load. Logs show fragments — timeouts, resets, cascading errors — but none of them point to where the failure *actually started*. DetTrace answers that question.

<<<<<<< HEAD
## The Problem
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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
=======
It records expected execution, replays observed behavior under guard, isolates the exact event where the traces diverge, and preserves artifacts that make debugging and incident reconstruction possible.

DetTrace is a specialist debugging and incident-forensics tool for turning flaky or ambiguous failures into reproducible evidence.
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)

**First divergence isolated at event index `5`.**

Not just *that* the run failed — but *where* the execution first stopped matching expectation. Everything after that point is a downstream consequence, not the root cause.

---

## Without DetTrace vs With DetTrace

<<<<<<< HEAD
| Without | With DetTrace |
|---|---|
| Failure appears flaky and inconsistent | Failure becomes replayable |
| Logs show symptoms but not the first split | First divergence isolated deterministically |
| Later timeouts and retries obscure root cause | Earliest causal mismatch preserved as evidence |
| Distributed failures look ambiguous | Incident packs, annotations, and semantic diffs make propagation explainable |
=======
<<<<<<< HEAD
**Deterministic Replay** — Replays event sequences to isolate ordering-sensitive failures and make divergence reproducible across runs.

**Distributed Incident Reconstruction** — Builds cross-service timelines from trace-like or JSONL event inputs, including an OTEL-compatible ingest path.

**First-Divergence Analysis** — Detects the exact event and service where expected and actual behavior begin to meaningfully differ.

**Blast-Radius Inference** — Identifies the root service, directly impacted downstream services, and upstream services affected by propagation.

**Semantic Incident Diff** — Compares baseline vs. candidate incidents at the failure-pattern level, not just raw line mismatch.
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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
=======
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
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)

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
<<<<<<< HEAD
=======
<<<<<<< HEAD
  "timeout_events": 1,
  "retry_events": 2,
  "network_error_events": 2,
=======
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)
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

<<<<<<< HEAD
## Example Semantic Diff
=======
<<<<<<< HEAD
### Semantic Incident Diff
=======
## Example Semantic Diff
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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

<<<<<<< HEAD
This helps distinguish root-cause shifts from downstream symptom changes across runs.
=======
<<<<<<< HEAD
Surfaces: first-failing-service changes, failure-reason shifts, retry amplification deltas, and latency characteristic changes between runs.

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
=======
This helps distinguish root-cause shifts from downstream symptom changes across runs.
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

---

## OTEL-Style Ingestion

<<<<<<< HEAD
DetTrace includes a JSONL ingest path that maps span records into its replay model:
=======
<<<<<<< HEAD
DetTrace includes a JSONL ingest path that converts span-like records into replayable distributed events:
=======
DetTrace includes a JSONL ingest path that maps span records into its replay model:
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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
<<<<<<< HEAD
=======
<<<<<<< HEAD
| Replay packs | `packs/cascading_timeouts.jsonl`, `packs/retry_storm.jsonl`, `packs/misordered_recovery.jsonl`, `packs/failover_edge.jsonl` |
| Sample ingest | `samples/otel_spans.jsonl` |
| Annotated traces | `artifacts/baseline_annotated.jsonl`, `artifacts/candidate_annotated.jsonl` |
| Incident report | `reports/distributed_incident_report.json` |
| Semantic diff | `reports/distributed_semantic_diff.json` |
=======
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)
| `artifacts/expected.jsonl` | Expected execution trace |
| `artifacts/actual.jsonl` | Observed execution trace |
| `artifacts/replayed.jsonl` | Replayed trace |
| `reports/divergence_report.json` | First-divergence report |
| `packs/*.jsonl` | Replayable distributed incident packs |
| `reports/distributed_incident_report.json` | Operator-style incident report |
| `reports/distributed_semantic_diff.json` | Semantic diff across runs |
<<<<<<< HEAD
=======
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

---

## Running Tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

<<<<<<< HEAD
End-to-end coverage includes original flaky replay, distributed incident replay, OTEL ingestion, annotation checks, timeline correlation, blast-radius inference, and semantic diff generation.
=======
<<<<<<< HEAD
End-to-end coverage: original flaky replay validation · distributed incident replay · OTEL ingestion · annotation checks · timeline correlation · blast-radius inference · semantic diff generation.
=======
End-to-end coverage includes original flaky replay, distributed incident replay, OTEL ingestion, annotation checks, timeline correlation, blast-radius inference, and semantic diff generation.
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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
<<<<<<< HEAD
```

Features side-by-side diff for passing vs failing executions, first-divergence highlighting, rule-based root-cause hints, and invariant status exploration.
=======
```

Features side-by-side diff for passing vs failing executions, first-divergence highlighting, rule-based root-cause hints, and invariant status exploration.

---

<<<<<<< HEAD
## Operator Runbook Output
=======
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
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)

DetTrace emits runbook guidance alongside replay artifacts:

1. Confirm request and span lineage; identify the first failing downstream hop
2. Correlate the incident with recent deploy, health-change, or failover windows
3. Inspect DNS, TCP connect, transport reset, and latency symptoms
4. Evaluate retry backoff and retry amplification
5. Review blast radius before rollback or traffic shift

---

<<<<<<< HEAD
## Quick Start

```bash
# Original deterministic replay demo
./scripts/run_demo.sh

# Distributed incident replay demo
./scripts/run_distributed_demo.sh
```

The distributed demo builds the incident path, generates replay packs, writes annotated cross-service traces, ingests OTEL-style sample spans, and emits a structured incident report plus semantic diff.

---

## Architecture

```
input traces / spans
    ↓
normalization
    ↓
event model
    ↓
replay engine
    ↓
divergence detection
    ↓
distributed incident analysis
    ↓
reports / viewer / semantic diff
```
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)

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

<<<<<<< HEAD
=======
## Related Projects

- [Faultline](https://github.com/kritibehl/faultline) — correctness under failure
- [KubePulse](https://github.com/kritibehl/KubePulse) — resilience validation
- [AutoOps-Insight](https://github.com/kritibehl/autoops-insight) — operator triage
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — evaluation and release gating

=======
>>>>>>> f79cfd1 (Refocus README on first-failure isolation and incident forensics)
>>>>>>> da976ff (Add Swift XCTest harness for deterministic replay and schedule-violation scenarios)
## License

MIT
