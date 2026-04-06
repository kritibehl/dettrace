# Causal Chain

- **Scenario:** timeout_chain
- **What changed first:** event 4 -> {seq=4, component=profile, action=timeout, state=degraded, detail=db_wait_exceeded}
- **What downstream behaviors changed:** operator-visible symptom became `gateway timeout visible to operator`
- **Which subsystem was affected first:** api
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
