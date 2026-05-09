import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_otel_ingestion_report_and_search():
    payload = json.loads(Path("case_studies/otel/retry_storm_spans.json").read_text())

    r = client.post("/ingest/otel", json={
        "incident_name": "ci-otel-retry-storm",
        "payload": payload
    })
    assert r.status_code == 200
    body = r.json()
    incident_id = body["incident_id"]

    assert body["event_count"] == 5
    assert body["analysis"]["retry_storm_detection"]["retry_count"] == 4
    assert body["analysis"]["timeout_chain_detection"]["count"] == 5

    report = client.get(f"/report/{incident_id}")
    assert report.status_code == 200
    assert report.json()["summary"]["fingerprint"] == "retry_storm_timeout_chain"

    search = client.get("/search?tag=retry_storm")
    assert search.status_code == 200
    assert search.json()["total"] >= 1


def test_firmware_sequence_divergence():
    for filename, expected_idx in [
        ("case_studies/timer_missed_tick.json", 1),
        ("case_studies/gpio_interrupt_race.json", 3),
        ("case_studies/uart_interrupt_stuck_irq.json", 4),
    ]:
        payload = json.loads(Path(filename).read_text())
        r = client.post("/ingest", json=payload)
        assert r.status_code == 200
        incident_id = r.json()["incident_id"]

        seq = client.get(f"/sequence-compare/{incident_id}")
        assert seq.status_code == 200
        assert seq.json()["first_divergence_index"] == expected_idx
