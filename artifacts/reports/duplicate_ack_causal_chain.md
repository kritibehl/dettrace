# Causal Chain

- **Scenario:** duplicate_ack
- **What changed first:** event 3 -> {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack}
- **What downstream behaviors changed:** operator-visible symptom became `duplicate completion or user-visible duplicate side effect`
- **Which subsystem was affected first:** coordinator
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
