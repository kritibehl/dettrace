# misordered_recovery

Symptom:
- partial recovery appears successful, then service degrades again

Invisible root cause:
- recovery actions completed out of order

First divergence:
- service timeline deviated from the healthy recovery sequence

What normal logs missed:
- ordering drift before the visible regression

DetTrace output:
- semantic incident diff
- timeline-based causal analysis
- historical comparison
