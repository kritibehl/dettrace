# DetTrace++ API Contracts

## Health

GET /health

Response:
```json
{
  "status": "ok",
  "service": "dettrace-plus-plus",
  "timestamp": "2026-05-08T00:00:00Z"
}
OpenTelemetry Ingestion

POST /ingest/otel

Purpose:
Convert OpenTelemetry-style spans into replayable DetTrace timelines.

Response includes:

incident_id
event_count
fingerprint
retry storm detection
timeout chain detection
root cause explanation
Timeline Export

GET /timeline-export/{incident_id}

Returns:

timeline
bookmarks
divergence snapshots
failure tags
full analysis
Incident Report

GET /report/{incident_id}

Returns:

fingerprint
event count
first divergence index
likely root cause
operator summary
evidence
Search

GET /search?q=retry
GET /search?tag=retry_storm

Returns matching incidents by keyword or failure tag.

Sequence Compare

GET /sequence-compare/{incident_id}

Returns:

expected sequence
actual sequence
first divergence index
