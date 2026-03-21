# DetTrace

**Deterministic replay and distributed incident forensics for reconstructing cross-service failure timelines.**

[![Tests](https://github.com/kritibehl/dettrace/actions/workflows/test.yml/badge.svg)](https://github.com/kritibehl/dettrace/actions)
![GitHub Repo stars](https://img.shields.io/github/stars/kritibehl/dettrace?style=social)

**DetTrace tells you which service failed first and how the failure spread.**

It reconstructs distributed failures into replayable timelines — finding the first failing hop, explaining propagation across services, and producing semantic incident diffs that show *how* failures changed between runs.

---

## 30-Second Summary

- A request fails at the edge. Retries amplify load. Downstream becomes unhealthy.
- Standard logs show *what* happened. DetTrace shows *where it started* and *how it propagated*.
- It replays the incident deterministically, infers blast radius, and produces a semantic diff against any baseline run.
- Output: first failing service, failure reason, retry amplification delta, blast radius, operator runbook.

Originally built for deterministic concurrency replay, DetTrace now extends that model to distributed incident forensics: request/span causality reconstruction, timeout-chain analysis, retry amplification detection, blast-radius inference, and semantic incident diffing.

---

## The Problem

Distributed incidents are hard to debug because:

- Symptoms appear far from the original failure
- Retries distort the timeline and inflate blast radius
- Multiple services emit partial, conflicting signals
- Logs show *what* happened, but not *where the divergence truly began*

> A request fails at the edge. Retries amplify load. A downstream dependency becomes unavailable.

**DetTrace shows:** which service failed first, how failure propagated, and whether the candidate incident differs semantically from baseline.

---

## What DetTrace Answers

- Which downstream hop failed first?
- Was this a timeout cascade or a retry storm?
- Did failure propagate through request/span lineage?
- Did failover reduce blast radius or create misordered recovery?
- Was this more consistent with DNS, transport, dependency, or latency inflation symptoms?

---

## Core Workflow

```
trace / span ingestion
    ↓
event normalization
    ↓
timeline reconstruction
    ↓
first-divergence detection
    ↓
blast-radius + failure-pattern analysis
    ↓
semantic incident diff
```

---

## Key Capabilities

**Deterministic Replay** — Replays event sequences to isolate ordering-sensitive failures and make divergence reproducible across runs.

**Distributed Incident Reconstruction** — Builds cross-service timelines from trace-like or JSONL event inputs, including an OTEL-compatible ingest path.

**First-Divergence Analysis** — Detects the exact event and service where expected and actual behavior begin to meaningfully differ.

**Blast-Radius Inference** — Identifies the root service, directly impacted downstream services, and upstream services affected by propagation.

**Semantic Incident Diff** — Compares baseline vs. candidate incidents at the failure-pattern level, not just raw line mismatch.

---

## Example Incident Topology

```
Client / Edge Proxy
        │
        ▼
   auth-service   ← first failing service
        │
        ▼
     token-db     ← downstream impact

Observed signals:
  dns_failure → retry → transport_reset → retry_burst → timeout_chain

Propagation:
  edge-proxy → auth-service → token-db
                │             ^
                +-- retries --+
                       │
                       +-- eventual timeout
```

---

## Example Outputs

### Incident Report

```json
{
  "incident_family": "retry_storm",
  "timeout_events": 1,
  "retry_events": 2,
  "network_error_events": 2,
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

### Semantic Incident Diff

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

---

## OTEL-Style Ingestion

DetTrace includes a JSONL ingest path that converts span-like records into replayable distributed events:

| Span Field | Maps To |
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
| Annotated traces | `artifacts/baseline_annotated.jsonl`, `artifacts/candidate_annotated.jsonl` |
| Incident report | `reports/distributed_incident_report.json` |
| Semantic diff | `reports/distributed_semantic_diff.json` |

---

## Running Tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

End-to-end coverage: original flaky replay validation · distributed incident replay · OTEL ingestion · annotation checks · timeline correlation · blast-radius inference · semantic diff generation.

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

## Operator Runbook Output

DetTrace emits runbook-oriented guidance alongside replay artifacts:

1. Confirm request and span lineage; identify the first failing downstream hop
2. Correlate the incident with recent deploy, health-change, or failover windows
3. Inspect DNS, TCP connect, transport reset, and latency symptoms
4. Evaluate retry backoff and retry amplification
5. Review blast radius before rollback or traffic shift

---

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
viewer/            Developer-facing diagnostics UI
dettrace-swift/    Swift companion analyzer
packs/             Replayable distributed incident packs
reports/           Divergence and incident reports
samples/           Sample OTEL-style JSONL span input
artifacts/         Generated trace files
```

---

## Why This Project Stands Out

DetTrace goes beyond log diffing toward failure reconstruction. It demonstrates deterministic replay thinking applied to distributed systems, cross-service incident analysis with blast-radius inference, semantic comparison of failure patterns across runs, and multi-language systems work (C++ core + Swift companion) — making it especially relevant for infrastructure, runtime, and reliability-oriented teams.

---

## Related Projects

- [Faultline](https://github.com/kritibehl/faultline) — correctness under failure
- [KubePulse](https://github.com/kritibehl/KubePulse) — resilience validation
- [AutoOps-Insight](https://github.com/kritibehl/autoops-insight) — operator triage
- [FairEval-Suite](https://github.com/kritibehl/FairEval-Suite) — evaluation and release gating

## License

MIT
