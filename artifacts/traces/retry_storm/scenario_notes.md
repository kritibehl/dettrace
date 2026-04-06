# Scenario Notes

- fault injection: inject auth dependency failures causing repeated retries
- notes: Healthy run performs a single auth lookup; degraded run amplifies retries and exposes error burst.
