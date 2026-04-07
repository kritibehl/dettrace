# Causal Chain

- **Scenario:** misordered_recovery
- **What changed first:** event 1 -> {seq=1, component=checkout-a, action=healthy, state=degraded, detail=marked_healthy_early, ts_ms=12}
- **What downstream behaviors changed:** operator-visible symptom became `recovery appears healthy before correctness is restored`
- **Which subsystem was affected first:** checkout-a
- **Did recovery restore correctness or mask behavior:** recovery masked ongoing incorrect behavior
