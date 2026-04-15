# Event Replay Schema

Minimal required fields:
- service
- timestamp
- trace_id
- event_type

Optional but useful:
- status
- latency_ms
- upstream
- message
- metadata

Purpose:
- deterministic replay
- first-divergence isolation
- service timeline reconstruction
