# Scenario Notes

- fault injection: inject duplicate completion acknowledgment without retry
- notes: Healthy run has one completion ack; degraded run emits duplicate ack and breaks idempotent completion expectations.
