# Scenario Notes

- fault injection: inject dependency failures causing repeated retries
- notes: Healthy run performs one auth lookup; degraded run amplifies retries and surfaces an error burst.
