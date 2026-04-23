from __future__ import annotations

import hashlib
import json
import math
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "incidents"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="DetTrace++ Distributed Incident Forensics Platform", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class ServiceEvent(BaseModel):
    service: str
    timestamp: str
    trace_id: str
    event_type: str
    message: str = ""
    latency_ms: Optional[float] = None
    status: Optional[str] = None
    upstream: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentIngestRequest(BaseModel):
    incident_name: str
    source: str = "manual"
    events: List[ServiceEvent]


class MultiServiceReplayRequest(BaseModel):
    incident_id: str


class ExplanationRequest(BaseModel):
    incident_id: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def incident_path(incident_id: str) -> Path:
    return DATA_DIR / f"{incident_id}.json"


def stable_hash(parts: List[str]) -> str:
    h = hashlib.sha256()
    h.update("|".join(parts).encode("utf-8"))
    return h.hexdigest()[:16]


def load_incident(incident_id: str) -> Dict[str, Any]:
    path = incident_path(incident_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"incident {incident_id} not found")
    return json.loads(path.read_text())


def save_incident(doc: Dict[str, Any]) -> None:
    incident_path(doc["incident_id"]).write_text(json.dumps(doc, indent=2))


def sort_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(events, key=lambda e: (e.get("timestamp", ""), e.get("service", ""), e.get("event_type", "")))


def first_divergence(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    by_trace: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in sort_events(events):
        by_trace[e["trace_id"]].append(e)

    candidate_groups = [g for g in by_trace.values() if len(g) >= 2]
    if not candidate_groups:
        return None

    baseline = candidate_groups[0]
    for group in candidate_groups[1:]:
        limit = min(len(baseline), len(group))
        for idx in range(limit):
            a = baseline[idx]
            b = group[idx]
            if (a["service"], a["event_type"], a.get("status")) != (b["service"], b["event_type"], b.get("status")):
                return {
                    "first_divergence_index": idx,
                    "baseline_trace_id": baseline[0]["trace_id"],
                    "candidate_trace_id": group[0]["trace_id"],
                    "baseline_event": a,
                    "candidate_event": b,
                    "divergence_type": "cross_service_event_mismatch",
                }
    return None


def detect_retry_storm(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    key_counts = Counter()
    for e in events:
        if e["event_type"].lower() in {"retry", "request_retry", "dependency_retry"}:
            key = (e["service"], e.get("upstream") or "unknown")
            key_counts[key] += 1

    if not key_counts:
        return None

    (service, upstream), count = key_counts.most_common(1)[0]
    if count < 3:
        return None

    return {
        "pattern": "retry_storm",
        "service": service,
        "upstream": upstream,
        "retry_count": count,
        "severity": "high" if count >= 5 else "medium",
    }


def detect_timeout_chain(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    timed_out = [e for e in events if str(e.get("status", "")).lower() in {"timeout", "timed_out"}]
    if len(timed_out) < 2:
        return None

    services = [e["service"] for e in timed_out]
    return {
        "pattern": "timeout_chain",
        "service_path": services,
        "count": len(timed_out),
        "severity": "high" if len(timed_out) >= 3 else "medium",
    }


def build_fingerprint(events: List[Dict[str, Any]], divergence: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    features: List[str] = []
    if divergence:
        features.append("cross_service_divergence")

    retry = detect_retry_storm(events)
    if retry:
        features.append("retry_storm")

    timeout = detect_timeout_chain(events)
    if timeout:
        features.append("timeout_chain")

    if any(e["event_type"].lower() == "dequeue" for e in events):
        features.append("race_condition_duplicate_dequeue")

    if any("db" in (e["service"] + " " + e.get("message", "")).lower() for e in events):
        features.append("database_path")

    fingerprint = "_".join(sorted(set(features))) if features else "unknown"
    return {"incident_fingerprint": fingerprint, "features": sorted(set(features))}


def root_cause_explanation(events: List[Dict[str, Any]], divergence: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    retry = detect_retry_storm(events)
    timeout = detect_timeout_chain(events)

    if retry:
        return {
            "likely_root_cause": f"{retry['service']} entered a retry storm against {retry['upstream']}",
            "reasoning": [
                f"Observed {retry['retry_count']} retry events",
                "Repeated retries amplify load and delay downstream recovery",
            ],
            "operator_summary": "Start with the upstream dependency and rate-limit retries before scaling consumers.",
        }

    if timeout:
        return {
            "likely_root_cause": "Timeout chain across multiple services",
            "reasoning": [
                f"Timeouts observed across {len(timeout['service_path'])} linked service events",
                "Downstream services likely inherited degraded latency from an upstream bottleneck",
            ],
            "operator_summary": "Inspect the earliest timeout in the chain and compare latency inflation service by service.",
        }

    if divergence:
        base = divergence["baseline_event"]
        cand = divergence["candidate_event"]
        return {
            "likely_root_cause": "Cross-service event ordering diverged from baseline execution",
            "reasoning": [
                f"First divergence at index {divergence['first_divergence_index']}",
                f"Baseline event was {base['service']}:{base['event_type']}",
                f"Candidate event was {cand['service']}:{cand['event_type']}",
            ],
            "operator_summary": "Investigate why service ordering changed before the visible failure appeared.",
        }

    return {
        "likely_root_cause": "No dominant failure pattern detected",
        "reasoning": ["Incident needs more traces or logs for explanation"],
        "operator_summary": "Collect broader trace coverage and rerun analysis.",
    }


def cluster_incidents() -> Dict[str, Any]:
    docs = [json.loads(p.read_text()) for p in sorted(DATA_DIR.glob("*.json"))]
    clusters: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for doc in docs:
        fp = doc.get("analysis", {}).get("fingerprint", {}).get("incident_fingerprint", "unknown")
        clusters[fp].append({
            "incident_id": doc["incident_id"],
            "incident_name": doc["incident_name"],
            "created_at": doc["created_at"],
        })

    return {
        "cluster_count": len(clusters),
        "clusters": [{"fingerprint": k, "incidents": v, "size": len(v)} for k, v in sorted(clusters.items())],
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "dettrace-plus-plus", "timestamp": now_iso()}


@app.post("/ingest")
def ingest(payload: IncidentIngestRequest) -> Dict[str, Any]:
    incident_id = f"inc_{uuid.uuid4().hex[:10]}"
    events = [e.model_dump() for e in payload.events]
    events = sort_events(events)

    divergence = first_divergence(events)
    fingerprint = build_fingerprint(events, divergence)
    explanation = root_cause_explanation(events, divergence)
    retry = detect_retry_storm(events)
    timeout = detect_timeout_chain(events)

    doc = {
        "incident_id": incident_id,
        "incident_name": payload.incident_name,
        "source": payload.source,
        "created_at": now_iso(),
        "event_count": len(events),
        "events": events,
        "analysis": {
            "divergence": divergence,
            "fingerprint": fingerprint,
            "retry_storm_detection": retry,
            "timeout_chain_detection": timeout,
            "root_cause_explanation": explanation,
            "memory_key": stable_hash([payload.incident_name, fingerprint["incident_fingerprint"]]),
        },
    }
    save_incident(doc)

    return {
        "incident_id": incident_id,
        "event_count": len(events),
        "analysis": doc["analysis"],
    }


@app.post("/replay/multi-service")
def replay_multi_service(payload: MultiServiceReplayRequest) -> Dict[str, Any]:
    doc = load_incident(payload.incident_id)
    events = sort_events(doc["events"])
    divergence = first_divergence(events)
    return {
        "incident_id": payload.incident_id,
        "service_count": len(sorted({e["service"] for e in events})),
        "trace_count": len(sorted({e["trace_id"] for e in events})),
        "timeline": events,
        "first_divergence": divergence,
    }


@app.post("/explain/root-cause")
def explain_root_cause(payload: ExplanationRequest) -> Dict[str, Any]:
    doc = load_incident(payload.incident_id)
    return {
        "incident_id": payload.incident_id,
        "explanation": doc["analysis"]["root_cause_explanation"],
    }


@app.get("/incidents")
def list_incidents() -> Dict[str, Any]:
    docs = [json.loads(p.read_text()) for p in sorted(DATA_DIR.glob("*.json"))]
    items = []
    for d in docs:
        items.append({
            "incident_id": d["incident_id"],
            "incident_name": d["incident_name"],
            "created_at": d["created_at"],
            "event_count": d["event_count"],
            "fingerprint": d.get("analysis", {}).get("fingerprint", {}).get("incident_fingerprint", "unknown"),
        })
    return {"items": items, "total": len(items)}


@app.get("/clusters")
def clusters() -> Dict[str, Any]:
    return cluster_incidents()


@app.get("/before-after-diff/{incident_id}")
def before_after_diff(incident_id: str) -> Dict[str, Any]:
    doc = load_incident(incident_id)
    events = sort_events(doc["events"])
    divergence = doc.get("analysis", {}).get("divergence")
    if not divergence:
        return {
            "incident_id": incident_id,
            "before": events[:3],
            "after": events[-3:],
            "divergence": None,
        }

    idx = divergence["first_divergence_index"]
    start = max(0, idx - 2)
    end = min(len(events), idx + 3)
    return {
        "incident_id": incident_id,
        "before": events[start:idx],
        "divergence_point": divergence,
        "after": events[idx:end],
    }



@app.get("/graph/{incident_id}")
def graph_view(incident_id: str) -> Dict[str, Any]:
    doc = load_incident(incident_id)
    events = sort_events(doc["events"])
    nodes = []
    edges = []
    for idx, e in enumerate(events):
        nodes.append({
            "id": idx,
            "service": e["service"],
            "event_type": e["event_type"],
            "timestamp": e["timestamp"],
            "trace_id": e["trace_id"],
        })
        if idx > 0:
            prev = events[idx - 1]
            edges.append({
                "from": idx - 1,
                "to": idx,
                "kind": "timeline",
                "same_trace": prev["trace_id"] == e["trace_id"],
            })
    return {
        "incident_id": incident_id,
        "graph": {"nodes": nodes, "edges": edges},
        "divergence": doc.get("analysis", {}).get("divergence"),
    }


@app.get("/viewer/{incident_id}", response_class=HTMLResponse)
def divergence_viewer_page(incident_id: str) -> str:
    doc = load_incident(incident_id)
    divergence = doc.get("analysis", {}).get("divergence")
    events = sort_events(doc["events"])

    by_trace: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in events:
        by_trace[e["trace_id"]].append(e)

    traces = list(by_trace.keys())
    expected = [e["event_type"] for e in by_trace[traces[0]]] if len(traces) >= 1 else []
    actual = [e["event_type"] for e in by_trace[traces[1]]] if len(traces) >= 2 else []
    likely_reason = "event ordering mismatch"
    if doc.get("analysis", {}).get("uart_irq_analysis"):
        likely_reason = doc["analysis"]["uart_irq_analysis"]["likely_reason"]
    if doc.get("analysis", {}).get("firmware_trace_analysis"):
        likely_reason = doc["analysis"]["firmware_trace_analysis"]["likely_reason"]

    expected_text = " → ".join(expected) if expected else "n/a"
    actual_text = " → ".join(actual) if actual else "n/a"
    first_idx = divergence["first_divergence_index"] if divergence else "none"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Divergence Viewer</title>
  <link rel="stylesheet" href="/static/timeline.css" />
</head>
<body>
  <div class="wrap">
    <h1>Divergence Viewer</h1>
    <div class="card"><strong>Incident:</strong> {doc["incident_name"]}</div>
    <div class="card">
      <div><strong>Expected</strong></div>
      <div>{expected_text}</div>
    </div>
    <div class="card">
      <div><strong>Actual</strong></div>
      <div>{actual_text}</div>
    </div>
    <div class="card">
      <div><strong>First divergence:</strong> index {first_idx}</div>
      <div><strong>Likely reason:</strong> {likely_reason}</div>
    </div>
  </div>
</body>
</html>"""

@app.get("/timeline/{incident_id}", response_class=HTMLResponse)
def timeline_page(incident_id: str) -> str:
    doc = load_incident(incident_id)
    title = doc["incident_name"]
    incident_json = json.dumps(doc)
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <link rel="stylesheet" href="/static/timeline.css" />
</head>
<body>
  <div class="wrap">
    <h1>{title}</h1>
    <p>Distributed Incident Timeline</p>
    <div id="summary"></div>
    <div id="timeline"></div>
  </div>
  <script>
    const incident = {incident_json};
    const timeline = document.getElementById("timeline");
    const summary = document.getElementById("summary");

    const divergence = incident.analysis.divergence;
    summary.innerHTML = `
      <div class="card">
        <strong>Fingerprint:</strong> ${{incident.analysis.fingerprint.incident_fingerprint}}<br/>
        <strong>Event count:</strong> ${{incident.event_count}}<br/>
        <strong>Root cause:</strong> ${{incident.analysis.root_cause_explanation.likely_root_cause}}<br/>
        <strong>First divergence:</strong> ${{divergence ? divergence.first_divergence_index : "none"}}
      </div>
    `;

    incident.events.forEach((e, idx) => {{
      const isDiv =
        divergence &&
        divergence.first_divergence_index === idx;
      const el = document.createElement("div");
      el.className = "event" + (isDiv ? " divergence" : "");
      el.innerHTML = `
        <div class="left">
          <span class="svc">${{e.service}}</span>
          <span class="ts">${{e.timestamp}}</span>
        </div>
        <div class="right">
          <div><strong>${{e.event_type}}</strong> · trace=${{e.trace_id}}</div>
          <div class="msg">${{e.message || ""}}</div>
          <div class="meta">status=${{e.status || "n/a"}} latency_ms=${{e.latency_ms ?? "n/a"}} upstream=${{e.upstream || "n/a"}}</div>
        </div>
      `;
      timeline.appendChild(el);
    }});
  </script>
</body>
</html>"""




@app.get("/sequence-compare/{incident_id}")
def sequence_compare_view(incident_id: str) -> Dict[str, Any]:
    doc = load_incident(incident_id)
    divergence = doc.get("analysis", {}).get("divergence")
    events = sort_events(doc["events"])

    by_trace: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in events:
        by_trace[e["trace_id"]].append(e)

    traces = list(by_trace.keys())
    if len(traces) < 2:
        return {
            "incident_id": incident_id,
            "message": "need baseline and candidate traces"
        }

    baseline = by_trace[traces[0]]
    candidate = by_trace[traces[1]]

    return {
        "incident_id": incident_id,
        "baseline_trace_id": traces[0],
        "candidate_trace_id": traces[1],
        "expected_sequence": [e["event_type"] for e in baseline],
        "actual_sequence": [e["event_type"] for e in candidate],
        "first_divergence_index": divergence["first_divergence_index"] if divergence else None
    }

@app.get("/divergence/{incident_id}")
def first_divergence_view(incident_id: str) -> Dict[str, Any]:
    doc = load_incident(incident_id)
    divergence = doc.get("analysis", {}).get("divergence")

    if not divergence:
        return {
            "incident_id": incident_id,
            "message": "no divergence detected"
        }

    events = doc.get("events", [])
    uart_issue = detect_uart_irq_issue(events)

    return {
        "incident_id": incident_id,
        "first_divergence_index": divergence["first_divergence_index"],
        "expected": divergence["baseline_event"],
        "actual": divergence["candidate_event"],
        "divergence_type": divergence["divergence_type"],
        "likely_reason": (
            uart_issue["likely_reason"]
            if uart_issue else (
                detect_firmware_trace_issue(events)["likely_reason"]
                if detect_firmware_trace_issue(events) else "event ordering mismatch"
            )
        )
    }

@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "DetTrace++",
        "endpoints": [
            "/health",
            "/ingest",
            "/replay/multi-service",
            "/explain/root-cause",
            "/incidents",
            "/clusters",
            "/graph/{incident_id}",
            "/before-after-diff/{incident_id}",
            "/sequence-compare/{incident_id}",
            "/divergence/{incident_id}",
            "/viewer/{incident_id}",
            "/timeline/{incident_id}",
        ],
    }
