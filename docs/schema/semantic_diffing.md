# Semantic Diffing Schema

Minimal required fields:
- service
- timestamp
- trace_id
- event_type

Recommended comparison fields:
- status
- latency_ms
- upstream
- message

Purpose:
- baseline vs candidate incident comparison
- first semantic mismatch detection
- root-cause oriented diffing
