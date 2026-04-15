# Race Condition

## Symptom
- duplicate dequeue
- duplicate processing
- queue inconsistency

## Invisible root cause
Baseline and candidate traces diverged before the visible failure.

## DetTrace value
- first-divergence isolation
- semantic diff
- race-condition fingerprinting
