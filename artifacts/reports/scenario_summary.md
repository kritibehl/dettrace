# Scenario Summary

## timeout_chain
- first divergence: 4
- suspected cause: timeout_chain
- confidence: 0.82
- symptom: gateway timeout visible to operator
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

## retry_storm
- first divergence: 2
- suspected cause: retry_amplification
- confidence: 0.82
- symptom: burst of auth failures and elevated latency
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

## stale_state
- first divergence: 1
- suspected cause: stale-state transition
- confidence: 0.9
- symptom: control drift or stale state actuation
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

## delayed_dependency
- first divergence: 1
- suspected cause: timing divergence
- confidence: 0.84
- symptom: deadline miss after dependency delay
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

## duplicate_ack
- first divergence: 3
- suspected cause: duplicate event
- confidence: 0.9
- symptom: duplicate completion or user-visible duplicate side effect
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

## misordered_recovery
- first divergence: 1
- suspected cause: recovery misordering
- confidence: 0.9
- symptom: recovery appears healthy before correctness is restored
- recommendation: inspect first divergence and invariant evidence before reacting to terminal symptom

