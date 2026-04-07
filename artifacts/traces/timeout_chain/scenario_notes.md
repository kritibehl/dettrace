# Scenario Notes

- fault injection: inject profile->db timeout after downstream request
- notes: Healthy run returns successfully; degraded run accumulates cascading timeouts and cancellation.
