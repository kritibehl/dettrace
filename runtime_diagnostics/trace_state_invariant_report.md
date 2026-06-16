# Trace State Invariant Report

## Invariants

| Invariant | Expected | Observed | Status |
|---|---|---|---|
| ready state requires successful ACK | ACK before completion | timeout before retry | FAIL |
| retry count must be bounded | bounded retry | bounded retry | PASS |
| final state must match transaction outcome | transaction_complete | transaction_complete | PASS |

## Interpretation

A final successful state does not erase earlier divergence. DetTrace keeps both the final recovery and the first reliability failure visible.
