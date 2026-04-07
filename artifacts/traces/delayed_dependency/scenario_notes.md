# Scenario Notes

- fault injection: inject delayed dependency-ready event
- notes: Healthy run waits for dependency-ready before action; degraded run dispatches too early and misses deadline.
