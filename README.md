# DetTrace

> First-failure isolation through deterministic replay and incident forensics.

DetTrace is a deterministic replay and divergence analysis tool for isolating the first point of failure in concurrent or distributed execution traces.

It helps turn flaky, ambiguous failures into reproducible evidence. DetTrace records expected execution, compares it against observed behavior, isolates the first point where the traces split, and preserves artifacts that make debugging and incident reconstruction easier.

---

## Why DetTrace

Distributed and concurrent failures are often easy to observe but hard to explain.

A request fails at the edge. Retries amplify load. A downstream dependency becomes unavailable. Logs show fragments. Later symptoms look noisy and important, but they may not be where the failure actually began.

DetTrace reconstructs those fragments into replayable timelines so you can identify the first failing hop, understand how the failure propagated, and compare regressions semantically across runs.

**Questions DetTrace answers:**

- Where did execution first stop matching expectation?
- Which downstream hop failed first?
- Was this a timeout cascade or a retry storm?
- Did failure propagate through request/span lineage?
- Did failover reduce blast radius or create misordered recovery?
- Was this more consistent with DNS, transport, dependency, or latency inflation symptoms?

---

## What It Proves

DetTrace should communicate one thing clearly:

**It turns flaky or ambiguous failures into reproducible debugging evidence.**

It does that by combining:

- deterministic replay
- first-failure isolation
- divergence analysis
- replayable incident packs
- semantic diffing for distributed failures

---

## Proof Statement

**Deterministic replay and divergence analysis tool for isolating the first point of failure in concurrent or distributed execution traces.**

---

## Current Scope

- deterministic replay for concurrent execution traces
- first-divergence detection with structured reports
- replay artifact generation for expected, actual, and replayed traces
- 4 replayable distributed incident packs
- 10+ network, transport, and recovery annotations
- OTEL-style span ingestion into a deterministic replay model
- semantic incident diffing across baseline and candidate runs
- blast-radius inference across upstream and downstream services
- operator-style incident reports and runbook guidance
- 2 end-to-end test paths covering original replay and distributed incident analysis

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

## Debugging Story

A concurrent execution path was failing nondeterministically, but logs alone did not explain why. The system looked healthy at a high level, yet repeated runs produced inconsistent outcomes.

DetTrace recorded the expected execution trace, replayed the run under guard, and isolated the first divergence at event index `5`.

**What failed**
- a different task was dequeued than the expected schedule required

**What was confusing**
- the failure appeared intermittent
- later symptoms looked more important than the actual root split
- raw logs did not show where execution first stopped matching expectation

**What DetTrace revealed first**
- the execution diverged the moment `TASK_DEQUEUED task=2` appeared where `TASK_DEQUEUED task=1` was expected

This is the core value of the project: not just showing that something failed, but showing **where the failure actually began**.

---

## Original Replay Example

The original replay path includes a concrete flaky-case walkthrough in `examples/flaky_case_1/`.

Observed first divergence at event index `5`:

- Expected: `TASK_DEQUEUED task=1 worker=0 queue=0`
- Actual: `TASK_DEQUEUED task=2 worker=0 queue=0`

DetTrace catches the exact split point deterministically and preserves the divergent trace artifacts for inspection.

---

## What “event index 5 isolated” means

In plain English: DetTrace found the exact step where execution first stopped matching the expected behavior.

Instead of saying only that the run failed, it showed that the split happened at the 6th recorded event, when the system dequeued the wrong task. Everything after that point may be a downstream consequence rather than the root cause.

That is what makes the tool useful for debugging hard failures: it isolates the earliest meaningful mismatch.

---

## Evidence Produced

DetTrace generates debugging artifacts that make failures easier to inspect and compare:

- expected trace
- actual trace
- replayed trace
- guarded replay trace
- first-divergence report
- distributed incident replay packs
- semantic incident diff
- operator-style incident report

---

## First-Divergence Example

**Expected**
```json
{"seq":5,"type":"TASK_DEQUEUED","task":1,"worker":0,"queue":0}
Actual

{"seq":5,"type":"TASK_DEQUEUED","task":2,"worker":0,"queue":0}

What changed

the trace diverged at event index 5
task 2 was dequeued where task 1 was expected
later failures were downstream effects of this earlier split
Without DetTrace vs With DetTrace
Without the tool	With DetTrace
failure appears flaky and inconsistent	failure becomes replayable
logs show many symptoms but not the first split	first divergence is isolated deterministically
later timeouts and retries obscure root cause	earliest causal mismatch is preserved as evidence
distributed failures look ambiguous	incident packs, annotations, and semantic diff make propagation explainable
Failure Modes Modeled
Category	Failure Mode
Timeout	cascading timeouts, timeout chains
Retry	retry storms, retry amplification
Transport	TCP connect timeout, transport reset, cancellation propagation
Network	DNS failure, latency inflation between hops
Dependency	downstream unavailable, dependency failover edge cases
Recovery	misordered failure recovery

These are modeled as replayable trace and event streams.

Distributed Incident Pack Example

DetTrace also models distributed failure scenarios as replayable incident packs, including:

cascading timeouts
retry storms
misordered recovery
dependency failover edge cases

Example progression:

dns_failure -> retry -> transport_reset -> retry_burst -> downstream_unavailable -> timeout_chain

This makes it possible to replay and compare failure propagation patterns rather than only inspect isolated events.

Example Incident Topology
Client / Edge Proxy
        |
        v
   auth-service   <- first failing service
        |
        v
     token-db     <- downstream impact

Observed signals:
  dns_failure -> retry -> transport_reset -> retry_burst -> timeout_chain

Propagation:
  edge-proxy -> auth-service -> token-db
                |             ^
                +-- retries --+
                       |
                       +-- eventual timeout
Example Incident Report
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
Semantic Incident Diff

DetTrace compares baseline and candidate incidents at the service and failure-pattern level, not just raw event mismatch.

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

DetTrace surfaces:

first failing service changes
failure-reason shifts
retry amplification deltas
timeout and network-error changes
latency characteristic changes between runs

This helps distinguish root-cause shifts from downstream symptom changes across runs.

OTEL-Style Ingestion

DetTrace includes a JSONL ingest path that converts span-like records into replayable distributed events.

Span field	Maps to
trace_id	request_id
span_id	span_id
parent_span_id	parent_span_id
peer_service	downstream_service
start_ms	ts_ms

This lets DetTrace analyze span-shaped telemetry using the same replay and incident-forensics model.

Quick Start
Original deterministic replay demo
./scripts/run_demo.sh

This demo:

builds the project
generates an expected trace
runs a divergent execution
isolates the first divergence
writes a structured divergence report
Distributed incident replay demo
./scripts/run_distributed_demo.sh

This demo:

generates replayable incident packs
ingests OTEL-style sample spans
annotates network and transport symptoms
writes an incident report
generates a semantic diff between baseline and candidate runs
Distributed Demo Outputs
Output	Path
Replay packs	packs/cascading_timeouts.jsonl, packs/retry_storm.jsonl, packs/misordered_recovery.jsonl, packs/failover_edge.jsonl
Sample ingest	samples/otel_spans.jsonl
Annotated traces	artifacts/baseline_annotated.jsonl, artifacts/candidate_annotated.jsonl, artifacts/otel_ingested_annotated.jsonl, artifacts/replayed_distributed.jsonl
Incident report	reports/distributed_incident_report.json
Semantic diff	reports/distributed_semantic_diff.json
Running Tests
cmake -B build && cmake --build build
cd build && ctest --output-on-failure

End-to-end coverage includes:

original flaky replay validation
distributed incident replay
OTEL ingestion
annotation checks
timeline correlation
blast-radius inference
semantic diff generation
Swift Companion Analyzer

dettrace-swift/ is a functional Swift CLI companion for inspecting trace artifacts outside the core C++ runtime.

It:

reads generated trace files concurrently
compares traces and identifies divergence
produces structured JSON and Markdown reports
supports repeated artifact inspection workflows during debugging
cd dettrace-swift
swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
Diagnostics Viewer

A lightweight developer-facing UI in viewer/ for inspecting execution differences.

It provides:

side-by-side diff for passing vs failing executions
first-divergence highlighting
rule-based root-cause hints
invariant status exploration
reproducible scenarios and benchmark page
./scripts/serve_viewer.sh
# -> http://localhost:8000/viewer/index.html
# -> http://localhost:8000/viewer/benchmarks.html
Repo Structure
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
Operator Runbook Output

DetTrace emits runbook-oriented guidance alongside replay artifacts:

Confirm request and span lineage; identify the first failing downstream hop
Correlate the incident with recent deploy, health-change, or failover windows
Inspect DNS, TCP connect, transport reset, and latency symptoms
Evaluate retry backoff and retry amplification
Review blast radius before rollback or traffic shift
Positioning

DetTrace is a specialist debugging and incident-forensics tool for making hard failures reproducible, inspectable, and explainable.

It is not a packet sniffer, not a router-control framework, and not a full observability platform. Its value is in making distributed failure sequences replayable, comparable, and explainable.

For broad recruiter scanning, this is best positioned as a specialist amplifier rather than your first general-purpose project.

Resume Angle

Built deterministic replay and divergence-analysis tooling that isolates the first point of failure in concurrent and distributed execution traces, turning flaky or ambiguous failures into reproducible debugging evidence.

Extended deterministic replay into incident-forensics tooling that reconstructs cross-service failure timelines, isolates first failing hops, and preserves replay artifacts for diagnosing retry, timeout, and transport-level divergence.

License

MIT
