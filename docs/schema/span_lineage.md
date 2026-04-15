# Span Lineage Schema

Minimal required fields:
- service
- timestamp
- trace_id
- event_type

Recommended lineage fields:
- upstream
- metadata.parent_span_id
- metadata.span_id
- metadata.operation

Purpose:
- OTEL-style ingestion
- cross-service propagation analysis
- causal graph reconstruction
