# retry_storm_chain

Symptom:
- retries rise
- latency balloons
- dependency collapses

Invisible root cause:
- early timeout triggered amplified retry traffic

First divergence:
- retry/timeout pattern appeared before downstream saturation

What normal logs missed:
- the beginning of causal amplification

DetTrace output:
- timeout-chain detection
- retry-storm fingerprint
- propagation prediction
