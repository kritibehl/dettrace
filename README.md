<div align="center">

# DetTrace

**First-failure isolation through deterministic replay and incident forensics**

[![C++17](https://img.shields.io/badge/C%2B%2B-17-00599C?style=flat-square&logo=cplusplus&logoColor=white)](https://isocpp.org)
[![Swift](https://img.shields.io/badge/Swift-Analyzer-F05138?style=flat-square&logo=swift&logoColor=white)](https://swift.org)
[![CMake](https://img.shields.io/badge/CMake-Build-064F8C?style=flat-square&logo=cmake&logoColor=white)](https://cmake.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

> Distributed and concurrent failures are easy to observe.
> **DetTrace makes them reproducible, comparable, and explainable.**

---

## The Problem

Concurrency and distributed failures fail in one consistent way: they refuse to reproduce.

Add a log statement and the bug disappears. Remove it and it comes back differently. Retries amplify noise. Later symptoms look more important than where the failure actually began. By the time you collect enough data to reason about it, the interleaving that caused it is gone.

**DetTrace fixes this by reconstructing the failure deterministically** — recording execution as an event sequence, replaying it identically, and isolating the exact point where behavior first diverged from expectation.

The first divergence is the root cause. Everything after it is consequence.

---

## What DetTrace Builds

| Capability | What it does |
|---|---|
| **Deterministic replay** | Records execution as an event sequence, replays identically |
| **First-divergence isolation** | Finds the exact event index where behavior first stopped matching expectation |
| **Distributed incident analysis** | Reconstructs cross-service timelines using span lineage |
| **Semantic incident diffing** | Compares failure patterns across runs — not just raw event mismatch |
| **Blast-radius inference** | Identifies upstream and downstream impact across service dependencies |
| **Incident fingerprinting** | Classifies failure into a named, stable pattern |
| **Propagation prediction** | Predicts downstream failure path from first divergence onward |
| **Cross-incident learning** | Matches current failure against historical incidents |
| **Control-loop debugging** | Replay-based closed-loop analysis under sensor, actuator, and timing faults |

---

## First-Divergence: A Real Example

A concurrent execution path was failing nondeterministically. Logs showed many symptoms but not the root cause. Later timeouts and retries obscured when the failure actually began.

DetTrace recorded the expected execution, replayed under guard, and isolated the split:

```
Divergence at event index 5

EXPECTED:  TASK_DEQUEUED task=1  worker=0  queue=0
ACTUAL:    TASK_DEQUEUED task=2  worker=0  queue=0
```

**What this means:** Two workers competed for the same task. The failure appeared downstream as duplicate processing — but the root cause was at index 5, before any visible output. Without deterministic replay, this was invisible.

```json
{
  "first_divergence_index": 5,
  "divergence_type": "event_mismatch",
  "expected": { "seq": 5, "type": "TASK_DEQUEUED", "task": 1 },
  "actual":   { "seq": 5, "type": "TASK_DEQUEUED", "task": 2 }
}
```

---

## Distributed Incident Analysis

DetTrace reconstructs cross-service failure sequences using OTEL-style span records.

### Example incident: retry storm

```
dns_failure → retry → transport_reset → retry_burst → downstream_unavailable → timeout_chain
```

```
Client / Edge Proxy
        │
        ▼
   auth-service   ← first failing service
        │
        ▼
     token-db     ← downstream impact

Propagation:
  edge-proxy → auth-service → token-db
                │              ↑
                └── retries ───┘
                       │
                       └── eventual timeout
```

### Incident report

```json
{
  "incident_family": "retry_storm",
  "annotations": ["dns_failure", "transport_reset", "retry_burst", "downstream_unavailable", "timeout_chain"],
  "blast_radius": {
    "root_service": "auth-service",
    "directly_impacted_services": ["token-db"],
    "upstream_services": ["edge-proxy"]
  },
  "timeline_correlation": {
    "deploy_correlated": true,
    "suspected_trigger": "recent_deploy",
    "max_latency_ms": 900,
    "error_burst_count": 3
  }
}
```

---

## Semantic Incident Diff

DetTrace compares baseline and candidate incidents at the service and pattern level — not raw event differences.

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

This distinguishes root-cause shifts from downstream symptom changes across runs.

---

## Incident Intelligence: Cross-Run Learning

DetTrace extends beyond single-run replay into pattern learning across incidents.

### Fingerprinting

```json
{ "incident_fingerprint": "event_mismatch_task_mismatch" }
```

### Propagation prediction

Given the divergence type, DetTrace predicts the downstream failure path before it fully unfolds:

```json
{
  "predicted_failure_propagation_path": ["work_distribution_skew", "missed_or_duplicate_processing"]
}
```

### Cross-incident similarity

```json
{ "confidence": 1.0, "top_match": "incident_20250301_task_mismatch" }
```

Confidence 1.0: this failure has been seen before. The exact divergence pattern and propagation path match a prior incident — converting debugging from "what is this?" to "we have seen this before."

---

## Control-Loop Replay

DetTrace includes a control-loop replay module for closed-loop debugging under sensor, actuator, and timing faults.

### Scenarios

| Scenario | Stable? | First divergence | Root cause class |
|---|---|---|---|
| healthy | yes | none | — |
| delayed_sensor | no | **step 38 / 3.9s** | delayed measurement, dropped sample |
| actuator_saturation | no | **step 53 / 5.4s** | actuator saturation |
| timing_jitter | no | timing-budget failure | 5 missed deadlines |

### Diagnostics summary

```json
{
  "first_divergence_step": 38,
  "first_divergence_timestamp": "3.9s",
  "root_cause_class": "delayed_measurement",
  "error_growth_after_divergence": 0.903344,
  "deadline_misses": 5,
  "instability_detected": true
}
```

Canonical visual artifact: `reports/control_loop_canonical_summary.svg`

---

## Failure Modes Modeled

| Category | Failure modes |
|---|---|
| Timeout | Cascading timeouts, timeout chains |
| Retry | Retry storms, retry amplification |
| Transport | TCP connect timeout, transport reset, cancellation propagation |
| Network | DNS failure, latency inflation between hops |
| Dependency | Downstream unavailable, dependency failover edge cases |
| Recovery | Misordered failure recovery, stale-state transitions |
| Control-loop | Delayed sensor, actuator saturation, timing jitter, missed deadlines |

---

## Replayable Incident Packs

| Pack | Failure pattern |
|---|---|
| `cascading_timeouts.jsonl` | Timeout chain across service hops |
| `retry_storm.jsonl` | Retry amplification under dependency failure |
| `misordered_recovery.jsonl` | Recovery events arrive out of causal order |
| `failover_edge.jsonl` | Dependency failover with incomplete blast-radius resolution |

---

## Artifact Output per Run

| Artifact | Contents |
|---|---|
| `expected.jsonl` | What execution should have produced |
| `actual.jsonl` | What it actually produced |
| `replayed.jsonl` | Deterministic replay output |
| `divergence_report.json` | First divergence index, type, context |
| `incident_fingerprint.json` | Named failure pattern |
| `propagation_prediction.json` | Predicted downstream failure path |
| `similar_incidents.json` | Cross-run similarity matches |
| `reports/distributed_incident_report.json` | Full cross-service incident report |
| `reports/distributed_semantic_diff.json` | Baseline vs candidate failure comparison |
| `reports/control_loop_diagnostics_summary.json` | Control-loop timing and divergence |
| `reports/incident_fingerprints.json` | Cross-incident fingerprint library |
| `reports/cross_incident_learning.md` | Pattern learning summary |

---

## Comparison with Existing Tools

| | DetTrace | Mozilla rr | Valgrind Helgrind |
|---|---|---|---|
| Language | C++17 + Swift | C/C++, x86 Linux | C/C++ |
| Approach | Event-level replay + divergence isolation | Full syscall-level record-and-replay | Lock order + happens-before analysis |
| Scope | Application-level concurrency + distributed incidents | Full program including kernel | Data races and lock misuse |
| Incident learning | **Yes** — fingerprint + propagation prediction | No | No |
| Cross-run history | **Yes** | No | No |
| Overhead | Low (application-level) | High (full system capture) | Very high (instrumentation) |
| Output | **Structured artifacts + causal chain + semantic diff** | Replay binary | Violation reports |
| Control-loop debugging | **Yes** | No | No |

DetTrace operates at the application event level — faster and more portable than full record-and-replay, with application-meaningful events and an incident intelligence layer that syscall-level tools cannot provide.

---

## Swift Analysis Layer

`dettrace-swift/` — Swift companion analyzer using `async/await` and actor-isolated `AnalysisStore` for safe concurrent artifact processing.

```swift
actor AnalysisStore {
    private var incidents: [Incident] = []

    func ingest(_ artifacts: ArtifactSet) async throws {
        let fingerprint = try await classify(artifacts.divergenceReport)
        let prediction  = try await predict(fingerprint)
        incidents.append(Incident(fingerprint: fingerprint, prediction: prediction))
    }
}
```

C++ for execution. Swift for safe analysis. Actor isolation prevents analysis-time race conditions in the layer that is itself analyzing race conditions.

```bash
cd dettrace-swift
swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
```

---

## Diagnostics Viewer

`viewer/` — lightweight developer UI for inspecting execution differences.

- Side-by-side diff for passing vs failing executions
- First-divergence highlighting
- Rule-based root-cause hints
- Invariant status exploration
- Reproducible scenarios and benchmark page

```bash
./scripts/serve_viewer.sh
# → http://localhost:8000/viewer/index.html
```

---

## Quick Start

```bash
# Build
cmake -B build && cmake --build build
cd build && ctest --output-on-failure

# Original deterministic replay demo
./scripts/run_demo.sh

# Distributed incident replay demo
./scripts/run_distributed_demo.sh

# Control-loop replay
./scripts/run_control_loop.sh

# Incident intelligence pipeline
./scripts/run_incident_intelligence.sh

# Swift analyzer
cd dettrace-swift && swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
```

---

## Operator Runbook Output

DetTrace emits runbook-oriented guidance alongside replay artifacts:

1. Confirm request and span lineage; identify the first failing downstream hop
2. Correlate the incident with recent deploy, health-change, or failover windows
3. Inspect DNS, TCP connect, transport reset, and latency inflation symptoms
4. Evaluate retry backoff and retry amplification extent
5. Review blast radius before rollback or traffic shift

---

## Case Studies

- [Duplicate Dequeue Race Condition](docs/case-studies/duplicate-dequeue.md) — how DetTrace isolated a task ordering race at event index 5

---

## Why This Matters

As AI-generated code enters production at scale, the verification problem grows. Code generation is becoming automated — correctness verification is not. Deterministic replay is the discipline that makes concurrent and distributed systems provably debuggable rather than just statistically monitored.

---

## Stack

C++17 · Swift · CMake · JSONL artifacts

---

## Related

- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution correctness under distributed failure
- [KubePulse](https://github.com/kritibehl/KubePulse) — resilience validation under degraded Kubernetes conditions
- [Postmortem Atlas](https://github.com/kritibehl/postmortem-atlas) — real production outages, structured and analyzed
