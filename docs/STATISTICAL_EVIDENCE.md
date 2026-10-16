# DetTrace — conservative statistical latency evidence

## Scope and backward compatibility

DetTrace's default `--latency-evidence point-estimate` retains existing
threshold and action semantics. The **opt-in** `--latency-evidence bootstrap`
mode conservatively rechecks existing per-semantic-key p95 threshold
crossings; it does not alter span topology or error-rate rules.

## Method

1. Match traces by request-shape cohort (unchanged from DetTrace).
2. Identify shared semantic span keys and candidate p95 threshold crossings
   using the existing comparator. The current p95 is span-occurrence-weighted.
3. For each crossing, resample **whole traces with replacement** within each
   group (baseline/candidate independently), retaining every occurrence of a
   semantic key in each sampled trace. This approximates the same estimator
   while keeping within-trace correlated spans together.
4. Calculate the candidate-vs-baseline percentage difference in bootstrapped
   p95. Take the one-sided lower percentile bound with alpha adjusted as
   `(1-confidence)/number_of_comparable_semantic_keys` (Bonferroni).
5. Confirm a crossing only when the lower bound is strictly larger than the
   configured percentage threshold. If the observed point estimate crosses
   but its lower bound does not, classify the cohort `INCONCLUSIVE` unless a
   structural or error-rate regression independently yields `FAIL`.

Requires at least 30 traces containing each examined span per side by default
(`--bootstrap-min-span-traces`). A nonpositive baseline p95, invalid duration,
or unusable resample is `INCONCLUSIVE` (no divide-by-zero/Infinity masquerading
as a high-confidence failure).

## Statistical interpretation and limitations

- Deterministic PRNG seed ensures reproducible resamples, **not** statistical
  independence across repeated CI jobs.
- The percentile-bootstrap interval is exploratory and can be inaccurate for
  heavy-tailed, censored, nonstationary, highly correlated or sparsely sampled
  p95 data. It does not replace production SLO evaluations, A/B experiments,
  or a designed hypothesis test.
- Bonferroni correction addresses multiple compared semantic keys **within a
  cohort**, not across request-shape cohorts, CI runs, or different metrics.
- A `PASS` in bootstrap mode means no detected threshold crossing with
  supported evidence, **not** equivalence or proof the candidate is safe.
- Structural additions and error regressions still use their prior point
  estimates and existing cohort sample-quality gate; they are not bootstrapped.
- Missing request-shape cohorts, under-sampled cohorts, and unconfirmed p95
  crossings produce overall `INCONCLUSIVE` in opt-in mode if no confirmed
  regression exists. A concrete `FAIL` takes precedence.
- Do not conflate p95 span contributions with additive end-to-end latency.

## CI usage

```yaml
- uses: ./
  with:
    baseline: artifacts/otlp/baseline.otlp.jsonl
    candidate: artifacts/otlp/candidate.otlp.jsonl
    latency-evidence: bootstrap
    bootstrap-iterations: '1000'
    bootstrap-confidence: '0.95'
    bootstrap-seed: '2026'
```

Default action behavior and report structure are preserved, except for an
additional `latency_evidence_mode` top-level field. Opt-in cohort reports also
include `point_estimate_decision` and structured `latency_evidence` assessments.
All bootstrap analyses depend on representativeness of input traces and are
not claims of incident-free production reliability.
