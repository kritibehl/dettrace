# DetTrace × OpenTelemetry Astronomy Shop

External validation of DetTrace against the official OpenTelemetry Demo / Astronomy Shop.

## Purpose

DetTrace tests whether baseline and candidate distributed executions are semantically different even when functional behavior still succeeds.

The integration exercises the standard path:

Application instrumentation
→ OTLP/gRPC
→ OpenTelemetry Collector
→ OTLP JSONL
→ DetTrace
→ canonical execution graph
→ regression decision

## Upstream

The validation environment is pinned in `UPSTREAM` to a specific OpenTelemetry Demo commit for reproducibility.

## Verified external ingestion

A broad Astronomy Shop capture has been successfully processed with:

- 454 valid OTLP JSONL batches
- 1,452 spans
- 456 distributed traces
- 16 services
- 1 orphan-parent trace in the captured dataset

Observed services include frontend, frontend-proxy, checkout, cart, product-catalog, recommendation, payment, shipping, currency, email, ad, flagd, image-provider, telemetry-docs, quote, and load-generator.

## Canonical execution representation

The post-v1 analyzer converts raw spans into semantic execution identities using stable properties such as:

- service identity
- HTTP route / method
- RPC service / method
- protocol
- stable downstream target
- parent-child relationships
- edge multiplicity

Volatile cross-run identity such as trace IDs, span IDs, container IDs, service instance IDs, ephemeral IPs, timestamps, and serialization order is excluded from semantic equality.

Parallel sibling ordering is treated as execution-equivalent while repeated semantic edges remain observable.

## Statistical quality

Comparisons can return:

- PASS
- FAIL
- INCONCLUSIVE

The quality gate checks minimum sample counts, severe sample imbalance, and invalid-trace fractions rather than treating insufficient evidence as a PASS.

## Automated validation

The trace-regression suite currently contains 26 passing tests, including tests for:

- volatile trace/span ID invariance
- parallel-child ordering invariance
- semantic edge multiplicity
- OpenTelemetry RPC semantic-convention normalization
- ephemeral-IP exclusion
- HTTP route normalization
- insufficient-sample INCONCLUSIVE behavior
- balanced-sample readiness

## Deterministic workload

The external harness runs a fixed request sequence against Astronomy Shop:

- home
- product
- recommendations
- cart
- checkout

A verified smoke capture completed three iterations with all 15 application requests successful and produced 68 valid Collector-generated OTLP batches.

## Remaining release validation

Before the next DetTrace release, the external matrix will complete exactly three regression classes:

1. latency regression
2. retry/topology regression
3. request-specific error regression

No additional DetTrace subsystem is planned.

The next release will be cut only after those scenarios pass against the pinned external application.
