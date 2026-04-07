# Propagation View

```text
healthy path
  lb -> ... -> lb

degraded path
  divergence@1 -> recovery misordering -> recovery appears healthy before correctness is restored

step-by-step propagation
  checkout-a:healthy -> marked_healthy_early
  payment:error -> dependency_unavailable
  lb:route -> masked_recovery_path
```
