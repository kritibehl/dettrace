# Causal Chain

- **Scenario:** stale_state
- **What changed first:** event 1 -> {seq=1, component=controller, action=consume_state, state=degraded, detail=est=v1_stale, ts_ms=10}
- **What downstream behaviors changed:** operator-visible symptom became `control drift or stale state actuation`
- **Which subsystem was affected first:** controller
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
