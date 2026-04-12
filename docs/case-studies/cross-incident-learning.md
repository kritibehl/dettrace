# Cross-Incident Learning

DetTrace now goes beyond first-divergence detection.

## What it does

For each run, it can now:

- generate an incident fingerprint
- predict likely propagation paths
- compare the current incident to prior failures
- persist incident history for future matching

## Example outputs

- incident_fingerprint.json
- propagation_prediction.json
- similar_incidents.json

## Why it matters

This moves DetTrace from replay-only debugging toward incident intelligence:

- "this failure resembles a previous outage"
- "this divergence is likely to amplify into retry pressure"
- "this pattern tends to cause downstream latency and duplicate work"

