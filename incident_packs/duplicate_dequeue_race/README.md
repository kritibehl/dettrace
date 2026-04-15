# duplicate_dequeue_race

Symptom:
- duplicate processing
- queue inconsistency

Invisible root cause:
- dequeue visibility and ownership handoff became inconsistent

First divergence:
- dequeue order shifted before the visible failure surfaced

What normal logs missed:
- the earliest semantic mismatch

DetTrace output:
- first-divergence isolation
- semantic diff
- incident fingerprinting
