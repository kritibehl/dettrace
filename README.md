# DetTrace

**OpenTelemetry trace regression analysis for CI.**

Compares baseline and candidate OpenTelemetry executions to catch structural, latency, and critical-path regressions before a change reaches production — with per-request-shape isolation, so one endpoint's regression doesn't get diluted by traffic from unrelated ones.

`Python` · `OpenTelemetry` · `C++17` · `Swift`

---

## Proof, first

A deliberately regressed checkout flow, analyzed cohort-by-cohort instead of as one blended distribution:

```
POST /checkout   (30 baseline / 30 candidate traces)  →  decision: FAIL
GET  /health     (10 baseline / 10 candidate traces)  →  decision: INCONCLUSIVE (raw verdict PASS; below the 30-sample minimum)
```

For `POST /checkout`:
```
p95 latency:   43.04 ms → 141.30 ms   (+228.3%)
error rate:    0.0% → 20.0%           (checkout.request AND inventory.reserve)
new dependency introduced:  inventory.reserve → redis.lookup
primary critical-path contributor:  inventory.reserve  (+59.22ms p95 contribution)
```

`GET /health` has only 10 samples per side against a 30-sample minimum, so DetTrace reports it `INCONCLUSIVE` (its raw verdict is `PASS`) instead of passing or failing it on thin data. That's the actual point: DetTrace evaluates matched request cohorts independently, and declines to over-claim on undersampled ones, instead of averaging all traffic into one number that would hide the checkout-specific failure.

---

## How it works

```
Baseline traces → semantic normalization → span graph → latency/structure
comparison → interval-derived critical-path analysis → per-cohort CI PASS/FAIL
```

Traces are grouped by request-shape fingerprint (root service, root span operation, HTTP method/route) before comparison, so unrelated endpoints never get blended together. Error-rate changes are reported in percentage points (0% → 20% = "+20pp"), not as an undefined relative increase.

```bash
python3 -m trace_regression.cli \
  --baseline artifacts/otlp/baseline.otlp.jsonl \
  --candidate artifacts/otlp/candidate.otlp.jsonl \
  --regression-threshold-pct 50 \
  --error-threshold-pp 5
```

**Honest about its limits:** the critical-path algorithm uses parent/child span intervals — built for tree-structured timing, and it does not yet claim causal correctness for arbitrary asynchronous distributed DAGs. Per-span p95 deltas are not an additive decomposition of the end-to-end p95 delta, because percentiles aren't additive.

---

## Runs as a CI gate

Reusable composite GitHub Action — point it at baseline/candidate OTLP artifacts and it fails the PR on regression (or report-only, if preferred):

```yaml
- uses: kritibehl/dettrace@v1
  with:
    baseline: artifacts/baseline.otlp.jsonl
    candidate: artifacts/candidate.otlp.jsonl
    regression-threshold-pct: "50"
    error-threshold-pp: "5"
```

Also verified against the **OpenTelemetry Collector pipeline directly** (not just the repo's local JSON exporter): app → OTLP/gRPC → Collector → OTLP JSON → DetTrace. The committed Collector output in `artifacts/otlp/` has 40 traces per side; running the CLI on it reproduces `/checkout` FAIL (p95 43.04 ms → 141.30 ms, errors 0% → 20%) and `/health` INCONCLUSIVE.

Also independently validated against the **OpenTelemetry Astronomy Shop** demo app using standard Collector-produced OTLP — detecting a deliberately injected latency regression on `shipping / POST /ship-order` (p95: 24.00ms → 1015.23ms) and a topology regression (`GetCart` edge multiplicity 1→2). See `docs/ASTRONOMY_SHOP_VALIDATION.md`.

---

## Architecture

**Technical deep dive:** [Architecture, regression methodology, validation, and limits](docs/ARCHITECTURE_AND_VALIDATION.md).

```
instrumented application
        │  OTLP/gRPC
        ▼
OpenTelemetry Collector
        │  OTLP JSON
        ▼
DetTrace ingestion adapter
        │
        ▼
request-shape matching
        │
        ├── latency regression
        ├── error-rate regression
        ├── structural regression
        └── critical-path contribution analysis
        │
        ▼
per-cohort CI PASS / FAIL
```

---

## Optional conservative latency gate

The existing p95 threshold gate remains the **default**, preserving released
Action behavior. For a stricter CI decision on latency, enable per-trace
bootstrap confirmation:

```bash
python3 -m trace_regression.cli \
  --baseline artifacts/otlp/baseline.otlp.jsonl \
  --candidate artifacts/otlp/candidate.otlp.jsonl \
  --latency-evidence bootstrap \
  --bootstrap-iterations 1000 \
  --bootstrap-confidence 0.95
```

This opt-in gate samples whole traces independently per side, calculates
Bonferroni-adjusted one-sided percentile-bootstrap lower bounds for the p95
percentage change, and confirms a point-estimate regression only if the lower
bound exceeds the configured threshold. Unresolved crossings, insufficient
span coverage, unmatched request cohorts, and under-sampled cohorts become
`INCONCLUSIVE` unless a separate conclusive regression exists. Exit codes are
0 `PASS`, 1 `FAIL`, 2 `INCONCLUSIVE`.

This is **not** a statistical proof of no regression or immunity to tail
sampling bias; see [Uncertainty protocol](docs/STATISTICAL_EVIDENCE.md).

## Also included

DetTrace grew out of an earlier deterministic-replay research project, and that core capability is still in the repo and still real:

- **First-divergence isolation** — replays a concurrent/distributed execution against an expected trace and finds the exact event index where behavior first diverged (not the last symptom). Documented case: a duplicate-dequeue race isolated to divergence index 5, where queue ownership wasn't serialized with dequeue visibility.
- **Control-loop replay** — closed-loop debugging for sensor/actuator/timing faults (2D waypoint tracking), with real divergence results: `delayed_sensor` diverges at step 38, `actuator_saturation` at step 53, `timing_jitter` produces 5 missed deadlines.
- **Swift companion analyzer** (`dettrace-swift/`) — reads trace artifacts concurrently using async/await and actor isolation, for inspection outside the C++ core.
- **DetTrace++** — an ingestion API / distributed-incident-forensics extension with a `/timeline`, `/search`, and OTel-span ingestion, for multi-service incident replay.



---

## Repository Structure

```
dettrace/
├── demo_checkout/         Instrumented OpenTelemetry workload (baseline/candidate)
├── trace_regression/       Core analyzer — normalize, graph, compare, critical_path, cohorts, cli
├── otel/                    Collector config for the verified OTLP pipeline
├── analysis/ · trace/ · replay/   Deterministic-replay core (first-divergence engine)
├── dettrace-swift/            Swift companion analyzer
├── dettrace_platform/           DetTrace++ ingestion API
├── docs/ASTRONOMY_SHOP_VALIDATION.md
├── tests/
└── reports/                      Generated regression + divergence reports
```

## Tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

## License

MIT
