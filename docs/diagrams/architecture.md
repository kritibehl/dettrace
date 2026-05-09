# DetTrace Architecture

```text
OpenTelemetry Spans / JSONL Traces / Incident Packs
                    |
                    v
              Event Ingestion
                    |
                    v
          Replayable Event Timeline
                    |
                    v
        First-Divergence / Pattern Analysis
                    |
      ---------------------------------
      |               |               |
      v               v               v
Retry Storms   Timeout Chains   Firmware-Style Faults
      |               |               |
      ---------------------------------
                    |
                    v
     Fingerprints / Failure Tags / Reports / Search

