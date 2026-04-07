# Cross-Incident Learning Report

DetTrace incident intelligence fingerprints each incident, finds similar historical failures, and surfaces recurring failure patterns.

## timeout_chain
- similar to `duplicate_ack` | score=0.0611111 | basis=symptom_overlap, nearby_first_divergence_position

## retry_storm
- similar to `stale_state` | score=0.05 | basis=nearby_first_divergence_position
- similar to `delayed_dependency` | score=0.05 | basis=nearby_first_divergence_position
- similar to `duplicate_ack` | score=0.05 | basis=nearby_first_divergence_position

## stale_state
- similar to `retry_storm` | score=0.05 | basis=nearby_first_divergence_position
- similar to `delayed_dependency` | score=0.05 | basis=nearby_first_divergence_position
- similar to `misordered_recovery` | score=0.05 | basis=nearby_first_divergence_position

## delayed_dependency
- similar to `retry_storm` | score=0.05 | basis=nearby_first_divergence_position
- similar to `stale_state` | score=0.05 | basis=nearby_first_divergence_position
- similar to `misordered_recovery` | score=0.05 | basis=nearby_first_divergence_position

## duplicate_ack
- similar to `timeout_chain` | score=0.0611111 | basis=symptom_overlap, nearby_first_divergence_position
- similar to `retry_storm` | score=0.05 | basis=nearby_first_divergence_position

## misordered_recovery
- similar to `retry_storm` | score=0.05 | basis=nearby_first_divergence_position
- similar to `stale_state` | score=0.05 | basis=nearby_first_divergence_position
- similar to `delayed_dependency` | score=0.05 | basis=nearby_first_divergence_position

