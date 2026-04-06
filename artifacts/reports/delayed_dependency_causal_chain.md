# Causal Chain

- **Scenario:** delayed_dependency
- **What changed first:** event 1 -> {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready}
- **What downstream behaviors changed:** operator-visible symptom became `deadline miss after dependency delay`
- **Which subsystem was affected first:** orchestrator
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
