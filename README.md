<div align="center">

# KubePulse

**Resilience validation that catches when Kubernetes says healthy but the system is unsafe to operate**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Scenarios-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/Terraform-AWS%20EKS-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://terraform.io)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)

</div>

---

> **Kubernetes tells you whether a pod is alive.**
> **KubePulse tells you whether the system is safe to operate.**

---

## The Problem Standard Probes Don't Solve

A service passes readiness checks. The dashboard is green. Traffic continues.

Meanwhile: a downstream DNS lookup is failing. A dependency cascade has tripled p95 latency. A topology reroute put the service on a degraded path. **Readiness probes stayed green through all of it.**

This is not an edge case. It is a structural gap between container-level health and user-visible health — and most deployment pipelines only measure one.

KubePulse measures both.

---

## Probe False Positive: Demonstrated

### Topology Failover Scenario

A link failure triggers a reroute. Reachability recovers. Kubernetes reports healthy. But the system is now running on a degraded alternate path.

```json
{
  "readiness_false_positive": true,
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "recommendation_action": "reroute",
  "what_probes_missed": "degraded alternate path — higher latency, weaker margins"
}
```

### Multi-Service Cascade Scenario

PostgreSQL latency spike → auth service retry amplification → API layer p99 inflation. Readiness probes stayed green throughout.

```
Dependency chain modeled: edge → api → auth → postgres
```

| Metric | Baseline | Degraded | Delta |
|---|---|---|---|
| p50 latency | 4.9 ms | 240 ms | +4,800% |
| p95 latency | 10.1 ms | 780 ms | **+333%** |
| p99 latency | — | 1,200 ms | **+275%** |
| Error rate | 0% | 8% | +8pp |
| Resilience score | 100 | **46** | −54 |
| Network health | 100 | **75** | −25 |
| Availability gap | 0% | 9% | +9pp |
| Path extra latency | 0 ms | 410 ms | +410 ms |

```json
{
  "readiness_false_positive": true,
  "probes_say_healthy": true,
  "safe_to_operate": false,
  "recommendation_action": "block",
  "slo_violation": true,
  "error_budget_remaining": "0.0%"
}
```

---

## Network Lab Results

Container-based network lab for repeatable degradation experiments.

### DNS Failure

| | Baseline | Degraded |
|---|---|---|
| Request success | 25 / 25 | **0 / 25** |

The dependency path broke entirely. Readiness probes were not informed.

### API Path Latency Injection

| | Baseline | Degraded |
|---|---|---|
| Requests succeeded | 25 / 25 | 23 / 25 |
| p50 latency | 4.888 ms | **1,462 ms** |
| p95 latency | 10.120 ms | **2,306 ms** |

The service appeared "up." The latency made it operationally unsafe.

---

## What KubePulse Validates

| Signal | What it tells you |
|---|---|
| Recovery time | Did the system return to acceptable state, or just stop crashing? |
| p50 / p95 / p99 latency drift | Did latency return to baseline or stay elevated? |
| Probe integrity | Did readiness signals match real availability? |
| DNS / dependency reachability | Were downstream services actually reachable? |
| Error-rate delta | Did degraded-path behavior increase failure rates? |
| SLO pass/fail | Did behavior cross user-facing thresholds? |
| Error budget remaining | How much runway remains before SLO breach? |
| Rollout risk | Should traffic continue, reroute, or stop? |

---

## System States

| State | Recovery | Latency drift | Probes | Interpretation |
|---|---|---|---|---|
| Healthy | 0–5s | Minimal | Aligned | Safe to operate |
| Degraded | Elevated | Significant | **False positive possible** | Looks healthy, unsafe |
| Recovered | Baseline | Normalizing | Realigned | Safe to resume |

---

## Scenarios

| Scenario | Failure type | Key signal |
|---|---|---|
| Readiness false positive | Topology failover + path reroute | `probes_say_healthy=true`, `safe_to_operate=false` |
| Multi-service cascade | DB latency → retry amplification | 333% p95 drift, `recommendation: block` |
| CPU stress | Pod CPU throttling | 8s recovery, resilience score 86/100 |
| DNS failure | Resolver failure | 0/25 success vs 25/25 baseline |
| API latency injection | Degraded hop | p50 4.9ms → 1,462ms |
| AI service timeout | Model inference spike | Fallback success rate, degraded-serving mode |
| Vector DB degradation | Retrieval latency | p99 drift, availability gap |

---

## AI Service Reliability

KubePulse includes scenario packs for Kubernetes-hosted AI services:

- Model inference timeout spikes
- Vector DB degraded latency
- Embedding service unavailable
- Tool-router dependency failure
- Partial fallback behavior under load

For AI scenarios, scorecards surface: availability, p99 latency, fallback success rate, degraded-but-serving vs full outage. The condition "latency SLO passed but error budget exhausted" is expressible and detectable.

---

## Canonical Decision Artifact

```
┌─────────────────────────────────────────────────────────┐
│  Scenario: multi_service_cascade                        │
│                                                         │
│  Probes healthy?      YES  (misleading)                 │
│  SLO met?             NO                                │
│  Safe to operate?     NO                                │
│  Error budget left?   0.0%                              │
│                                                         │
│  What probes missed:  8% error rate, 333% p95 drift,   │
│                       9% availability gap               │
│                                                         │
│  Recommendation:      BLOCK rollout                     │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture

```
YAML scenario definition
        ↓
KubePulse scenario runner
        ↓
Baseline capture (p50 / p95 / p99 / error rate)
        ↓
Failure injection (CPU stress / pod kill / network partition / latency / DNS)
        ↓
Degraded measurement + SLO evaluation
        ↓
Probe integrity check
        ↓
Resilience score (composite)
        ↓
Decision artifact: continue / reroute / block
        ↓
CI gate (GitHub Actions) — blocks deployment if safe_to_operate=false
```

---

## Infrastructure (Terraform)

```bash
cd terraform/
terraform init
terraform apply
```

Provisions: VPC · public and private subnets · NAT gateway · EKS cluster · managed node group

---

## CI Integration

Every PR runs the full resilience suite. Deployments fail if resilience score drops below threshold or `safe_to_operate=false`.

```yaml
- name: Run KubePulse resilience gate
  run: python kubepulse/run_scenarios.py --gate
```

---

## Extending with a New Scenario

1. Add a failure script in `lab/network-lab/scripts/failures/`
2. Add the scenario branch in `run_experiment.sh`
3. Capture: request success/failure, p50/p95 latency, DNS/TCP behavior, recovery timing
4. Document healthy vs degraded vs recovered outcomes
5. Add operator interpretation: safe to operate, still degraded, rollout risk, recommendation

---

## Artifacts

```
docs/scorecards/          Resilience validation scorecards
docs/reports/             Example run reports and what_probes_missed
docs/network-lab/         Network lab result summaries
docs/showcase/            Scenario matrix, false-green gallery, decision artifacts
docs/compare/             Baseline vs degraded vs recovered comparisons
```

---

## Quickstart (Network Lab)

```bash
# Prerequisite: Docker Desktop running
docker compose -f lab/network-lab/docker-compose.yml up -d --build

# Run baseline
bash lab/network-lab/scripts/run_experiment.sh baseline

# Run DNS failure scenario
bash lab/network-lab/scripts/run_experiment.sh dns_failure

# Run latency injection
bash lab/network-lab/scripts/run_experiment.sh latency_injection
```

---

## Interview Framing

KubePulse started as a resilience validation tool. I pushed it toward a release-safety system after noticing that readiness probes stay green during dependency failures and topology reroutes — exactly the conditions where rollout should stop. The core insight is that container health and user-visible health are different measurements, and most deployment pipelines only check one of them.

---

## Stack

Python · FastAPI · Kubernetes · Prometheus · Docker · Terraform (AWS EKS) · GitHub Actions

---

## Related

- [Faultline](https://github.com/kritibehl/faultline) — exactly-once execution correctness under distributed failure
- [Postmortem Atlas](https://github.com/kritibehl/postmortem-atlas) — real production outages, structured by failure class
- [AutoOps-Insight](https://github.com/kritibehl/AutoOps-Insight) — CI failure intelligence and operator triage
- [DetTrace](https://github.com/kritibehl/dettrace) — deterministic replay for concurrency failures
