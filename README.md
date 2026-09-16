# DetTrace

**OpenTelemetry trace regression analysis for CI.**

Compares baseline and candidate OpenTelemetry executions to catch structural, latency, and critical-path regressions before a change reaches production — with per-request-shape isolation, so one endpoint's regression doesn't get diluted by traffic from unrelated ones.

`Python` · `OpenTelemetry` · `C++17` · `Swift`

---

## Proof, first

A deliberately regressed checkout flow, analyzed cohort-by-cohort instead of as one blended distribution:

```
POST /checkout   (30 baseline / 30 candidate traces)  →  decision: FAIL
GET  /health     (10 baseline / 10 candidate traces)  →  decision: PASS
```

For `POST /checkout`:
```
p95 latency:   61.12 ms → 172.06 ms   (+181.5%)
error rate:    0.0% → 20.0%           (checkout.request AND inventory.reserve)
new dependency introduced:  inventory.reserve → redis.lookup
primary critical-path contributor:  inventory.reserve  (+65.56ms p95 contribution)
new critical-path contributor:      redis.lookup        (+44.41ms)
```

`GET /health` — untouched by the regression — correctly stays `PASS`. That's the actual point: DetTrace evaluates matched request cohorts independently instead of averaging all traffic into one number that would hide the checkout-specific failure.

---

## How it works

```
Baseline traces → semantic normalization → span graph → latency/structure
comparison → interval-derived critical-path analysis → per-cohort CI PASS/FAIL
```

Traces are grouped by request-shape fingerprint (root service, root span operation, HTTP method/route) before comparison, so unrelated endpoints never get blended together. Error-rate changes are reported in percentage points (0% → 20% = "+20pp"), not as an undefined relative increase.

```bash
python3 -m trace_regression.cli \
  --baseline artifacts/traces/baseline/checkout.json \
  --candidate artifacts/traces/candidate/checkout.json \
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

Also verified against the **OpenTelemetry Collector pipeline directly** (not just the repo's local JSON exporter): app → OTLP/gRPC → Collector → OTLP JSON → DetTrace. Verified run: 170 baseline / 200 candidate spans across 40 traces each, same `/checkout` FAIL / `/health` PASS split, independently reproducing the p95 and error-rate regression through the standard OTel pipeline rather than a repo-specific format.

Also independently validated against the **OpenTelemetry Astronomy Shop** demo app using standard Collector-produced OTLP — catching a real latency regression on `shipping / POST /ship-order` (p95: 24.00ms → 1015.23ms) and a topology regression (`GetCart` edge multiplicity 1→2). See `docs/ASTRONOMY_SHOP_VALIDATION.md`.

---

## Architecture

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

## Also included

DetTrace grew out of an earlier deterministic-replay research project, and that core capability is still in the repo and still real:

- **First-divergence isolation** — replays a concurrent/distributed execution against an expected trace and finds the exact event index where behavior first diverged (not the last symptom). Documented case: a duplicate-dequeue race isolated to divergence index 5, where queue ownership wasn't serialized with dequeue visibility.
- **Control-loop replay** — closed-loop debugging for sensor/actuator/timing faults (2D waypoint tracking), with real divergence results: `delayed_sensor` diverges at step 38, `actuator_saturation` at step 53, `timing_jitter` produces 5 missed deadlines.
- **Swift companion analyzer** (`dettrace-swift/`) — reads trace artifacts concurrently using async/await and actor isolation, for inspection outside the C++ core.
- **DetTrace++** — an ingestion API / distributed-incident-forensics extension with a `/timeline`, `/search`, and OTel-span ingestion, for multi-service incident replay.

The repo also carries a large volume of smaller simulated diagnostics packs (firmware/UART traces, protocol-state replay, hardware-adjacent I/O scenarios, sensor-stream validation, and similar) that are explicitly labeled in-repo as simulations, not production or hardware ownership claims. They're real code, but they're not load-bearing for this project's story — the OpenTelemetry CI-gate capability above is. If you want to walk through any of the secondary modules in an interview, know it well first; don't let the README's breadth substitute for depth you can defend out loud.

**Recommended before this goes live:** the actual repo README is far larger than this file, includes several sections repeated verbatim, and buries the strong CI-gate story under a long tail of smaller demos. This version leads with what's strongest and cuts the rest to a summary — replacing the live README with something close to this, rather than adding to it, is the move that will actually help here.

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
