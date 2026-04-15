from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ingest_and_cluster():
    payload = {
        "incident_name": "unit-test-incident",
        "source": "test",
        "events": [
            {
                "service": "queue-service",
                "timestamp": "2026-04-12T12:00:00+00:00",
                "trace_id": "baseline-a",
                "event_type": "dequeue",
                "message": "worker A task 1",
                "status": "ok",
                "latency_ms": 3
            },
            {
                "service": "queue-service",
                "timestamp": "2026-04-12T12:00:01+00:00",
                "trace_id": "candidate-a",
                "event_type": "dequeue",
                "message": "worker A task 2",
                "status": "ok",
                "latency_ms": 4
            }
        ]
    }
    ingest = client.post("/ingest", json=payload)
    assert ingest.status_code == 200
    incident_id = ingest.json()["incident_id"]

    replay = client.post("/replay/multi-service", json={"incident_id": incident_id})
    assert replay.status_code == 200

    clusters = client.get("/clusters")
    assert clusters.status_code == 200


def test_graph_and_diff_views():
    payload = {
        "incident_name": "graph-test-incident",
        "source": "test",
        "events": [
            {
                "service": "svc-a",
                "timestamp": "2026-04-12T12:00:00+00:00",
                "trace_id": "baseline-z",
                "event_type": "dequeue",
                "message": "baseline event",
                "status": "ok",
                "latency_ms": 2
            },
            {
                "service": "svc-b",
                "timestamp": "2026-04-12T12:00:01+00:00",
                "trace_id": "candidate-z",
                "event_type": "retry",
                "message": "candidate event",
                "status": "timeout",
                "latency_ms": 200
            }
        ]
    }
    ingest = client.post("/ingest", json=payload)
    assert ingest.status_code == 200
    incident_id = ingest.json()["incident_id"]

    graph = client.get(f"/graph/{incident_id}")
    assert graph.status_code == 200
    assert "graph" in graph.json()

    diff = client.get(f"/before-after-diff/{incident_id}")
    assert diff.status_code == 200
