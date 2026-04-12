from __future__ import annotations

import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("autoops.db")


def _conn(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def _score_decision(
    severity: str,
    confidence: float,
    recurrence: int,
    release_blocking: bool,
    nearby_change_count: int,
    family: str,
) -> tuple[str, str]:
    sev = (severity or "").lower()
    family = (family or "").lower()

    if release_blocking and confidence >= 0.84 and nearby_change_count > 0:
        return "rollback", "release-blocking incident with strong confidence and correlated nearby change"
    if sev in {"high", "critical"} and recurrence >= 2:
        return "escalate", "high-severity recurring incident suggests broader operational impact"
    if family in {"dns", "dependency_failure", "service_unreachable", "tls_handshake"} and confidence >= 0.84:
        return "escalate", "externally visible dependency or connectivity issue should be routed quickly"
    if sev in {"low"} and confidence < 0.70 and recurrence <= 1 and not release_blocking:
        return "ignore", "low-confidence isolated signal with low operational risk"
    return "escalate", "needs operator review with owner and mitigation guidance"


def blast_radius_estimate(incident_id: int, db_path: str | Path = DB_PATH, window_minutes: int = 60) -> dict[str, Any]:
    conn = _conn(db_path)
    incident = conn.execute("SELECT * FROM analyses WHERE id = ?", (incident_id,)).fetchone()
    if not incident:
        conn.close()
        return {"error": "incident not found"}

    ts = _parse_dt(incident["created_at"])
    if ts is None:
        conn.close()
        return {"error": "incident timestamp invalid"}

    start = (ts - timedelta(minutes=window_minutes)).isoformat()
    end = (ts + timedelta(minutes=window_minutes)).isoformat()

    nearby = conn.execute(
        """
        SELECT id, created_at, filename, failure_family, probable_owner, severity, release_blocking, signature, confidence
        FROM analyses
        WHERE created_at BETWEEN ? AND ?
        ORDER BY created_at ASC
        """,
        (start, end),
    ).fetchall()

    owner_counts = Counter((r["probable_owner"] or "unknown") for r in nearby)
    source_counts = Counter((r["filename"] or "unknown-source") for r in nearby)
    family_counts = Counter((r["failure_family"] or "unknown-family") for r in nearby)
    blocker_count = sum(int(r["release_blocking"]) for r in nearby)

    impacted_owners = list(owner_counts.keys())
    impacted_sources = list(source_counts.keys())

    if blocker_count >= 3 or len(impacted_owners) >= 2 or len(nearby) >= 5:
        label = "broad"
    elif blocker_count >= 1 or len(nearby) >= 3:
        label = "moderate"
    else:
        label = "localized"

    conn.close()
    return {
        "incident_id": incident_id,
        "blast_radius": label,
        "who_will_be_affected": {
            "owners": impacted_owners,
            "sources": impacted_sources,
        },
        "nearby_incident_count": len(nearby),
        "release_blocking_count": blocker_count,
        "owner_counts": dict(owner_counts),
        "source_counts": dict(source_counts),
        "family_counts": dict(family_counts),
        "window_minutes": window_minutes,
    }


def automated_decision(incident_id: int, db_path: str | Path = DB_PATH) -> dict[str, Any]:
    conn = _conn(db_path)
    incident = conn.execute("SELECT * FROM analyses WHERE id = ?", (incident_id,)).fetchone()
    if not incident:
        conn.close()
        return {"error": "incident not found"}

    incident_dict = dict(incident)
    recurrence = 1
    signature = incident_dict.get("signature")
    if signature:
        row = conn.execute("SELECT COUNT(*) AS c FROM analyses WHERE signature = ?", (signature,)).fetchone()
        recurrence = int(row["c"]) if row else 1

    ts = _parse_dt(incident_dict.get("created_at"))
    nearby_change_count = 0
    if ts:
        start = (ts - timedelta(minutes=60)).isoformat()
        end = (ts + timedelta(minutes=60)).isoformat()
        audit_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'"
        ).fetchone()
        if audit_exists:
            cols = {r["name"] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall()}
            ts_col = "timestamp" if "timestamp" in cols else ("created_at" if "created_at" in cols else None)
            if ts_col:
                rows = conn.execute(
                    f"SELECT * FROM audit_log WHERE {ts_col} BETWEEN ? AND ?",
                    (start, end),
                ).fetchall()
                nearby_change_count = sum(
                    1 for r in rows if any(tok in str(dict(r)).lower() for tok in ["deploy", "release", "rollout", "rule_update"])
                )

    confidence = float(incident_dict.get("confidence") or 0.0)
    severity = incident_dict.get("severity") or "low"
    family = incident_dict.get("failure_family") or incident_dict.get("predicted_issue") or "unknown"
    release_blocking = bool(incident_dict.get("release_blocking"))

    decision, reason = _score_decision(
        severity=severity,
        confidence=confidence,
        recurrence=recurrence,
        release_blocking=release_blocking,
        nearby_change_count=nearby_change_count,
        family=family,
    )

    radius = blast_radius_estimate(incident_id, db_path=db_path)

    owner = incident_dict.get("probable_owner") or "service-owner"
    remediation = incident_dict.get("first_remediation_step") or "inspect the failing dependency and compare nearby changes"

    conn.close()
    return {
        "incident_id": incident_id,
        "decision": decision,
        "reason": reason,
        "ownership": owner,
        "remediation": remediation,
        "recurrence": recurrence,
        "confidence": confidence,
        "severity": severity,
        "release_blocking": release_blocking,
        "nearby_change_count": nearby_change_count,
        "blast_radius": radius,
    }
