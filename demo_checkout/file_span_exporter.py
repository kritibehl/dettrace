from __future__ import annotations

import json
from pathlib import Path

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult


class JsonFileSpanExporter(SpanExporter):
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def export(self, spans):
        records = []

        for span in spans:
            context = span.get_span_context()
            parent_span_id = None

            if span.parent is not None:
                parent_span_id = f"{span.parent.span_id:016x}"

            records.append(
                {
                    "trace_id": f"{context.trace_id:032x}",
                    "span_id": f"{context.span_id:016x}",
                    "parent_span_id": parent_span_id,
                    "name": span.name,
                    "start_time_unix_nano": span.start_time,
                    "end_time_unix_nano": span.end_time,
                    "duration_ms": (
                        (span.end_time - span.start_time) / 1_000_000
                        if span.start_time is not None and span.end_time is not None
                        else None
                    ),
                    "status": getattr(span.status.status_code, "name", str(span.status.status_code)),
                    "attributes": {
                        str(key): value
                        for key, value in dict(span.attributes or {}).items()
                    },
                    "resource": {
                        str(key): value
                        for key, value in dict(span.resource.attributes or {}).items()
                    },
                }
            )

        existing = []

        if self.output_path.exists():
            existing = json.loads(self.output_path.read_text())

        existing.extend(records)

        self.output_path.write_text(
            json.dumps(existing, indent=2, default=str)
        )

        return SpanExportResult.SUCCESS

    def shutdown(self):
        return None
