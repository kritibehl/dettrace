# Incident Report

- **Scenario:** timeout_chain
- **Suspected cause:** timeout_chain
- **Confidence:** 0.82
- **First divergence event:** 4
- **Affected components:** api, profile
- **Likely user symptom:** gateway timeout visible to operator
- **Alternative hypotheses:** ordering instability after retry; missing dependency-ready trace granularity

## Key Evidence
- {seq=4, component=profile, action=timeout, state=degraded, detail=db_wait_exceeded}
