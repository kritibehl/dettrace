# Causal Chain

- **Scenario:** stale_state
- **What changed first:** event 1 -> {seq=1, component=planner, action=state_update, state=ok, detail=est=v2}
- **What downstream behaviors changed:** operator-visible symptom became `control drift or stale state actuation`
- **Which subsystem was affected first:** controller
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
