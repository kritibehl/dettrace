# Scenario Notes

- fault injection: mark service healthy before downstream recovery stabilizes
- notes: Healthy run recovers downstream first; degraded run flips health early and masks ongoing dependency failure.
