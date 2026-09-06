from __future__ import annotations

import json
from pathlib import Path


def _any_value(value):
    if value is None:
        return None

    if "stringValue" in value:
        return value["stringValue"]

    if "boolValue" in value:
        return bool(value["boolValue"])

    if "intValue" in value:
        raw = value["intValue"]
        try:
            return int(raw)
        except (TypeError, ValueError):
            return raw

    if "doubleValue" in value:
        raw = value["doubleValue"]
        try:
            return float(raw)
        except (TypeError, ValueError):
            return raw

    if "bytesValue" in value:
        return value["bytesValue"]

    if "arrayValue" in value:
        return [
            _any_value(item)
            for item in value[
                "arrayValue"
            ].get(
                "values",
                [],
            )
        ]

    if "kvlistValue" in value:
        result = {}

        for item in value[
            "kvlistValue"
        ].get(
            "values",
            [],
        ):
            key = item.get("key")

            if key is not None:
                result[key] = _any_value(
                    item.get(
                        "value",
                        {},
                    )
                )

        return result

    return None


def _attributes(items):
    result = {}

    for item in items or []:
        key = item.get("key")

        if key is None:
            continue

        result[key] = _any_value(
            item.get(
                "value",
                {},
            )
        )

    return result


def _status_name(status):
    status = status or {}

    code = status.get(
        "code",
        0,
    )

    if isinstance(code, int):
        if code == 2:
            return "ERROR"

        if code == 1:
            return "OK"

        return "UNSET"

    normalized = str(
        code
    ).upper()

    if (
        normalized == "2"
        or normalized.endswith(
            "_ERROR"
        )
        or normalized == "ERROR"
    ):
        return "ERROR"

    if (
        normalized == "1"
        or normalized.endswith(
            "_OK"
        )
        or normalized == "OK"
    ):
        return "OK"

    return "UNSET"


def otlp_payload_to_spans(
    payload,
):
    spans = []

    for resource_spans in payload.get(
        "resourceSpans",
        [],
    ):
        resource = _attributes(
            resource_spans.get(
                "resource",
                {},
            ).get(
                "attributes",
                [],
            )
        )

        scope_groups = (
            resource_spans.get(
                "scopeSpans"
            )
            or resource_spans.get(
                "instrumentationLibrarySpans"
            )
            or []
        )

        for scope_group in scope_groups:
            scope = (
                scope_group.get(
                    "scope"
                )
                or scope_group.get(
                    "instrumentationLibrary"
                )
                or {}
            )

            scope_name = scope.get(
                "name"
            )

            scope_version = scope.get(
                "version"
            )

            for span in scope_group.get(
                "spans",
                [],
            ):
                start_ns = int(
                    span.get(
                        "startTimeUnixNano",
                        0,
                    )
                    or 0
                )

                end_ns = int(
                    span.get(
                        "endTimeUnixNano",
                        0,
                    )
                    or 0
                )

                status = span.get(
                    "status",
                    {},
                )

                spans.append(
                    {
                        "trace_id":
                            span.get(
                                "traceId",
                                "",
                            ),
                        "span_id":
                            span.get(
                                "spanId",
                                "",
                            ),
                        "parent_span_id":
                            span.get(
                                "parentSpanId"
                            )
                            or None,
                        "name":
                            span.get(
                                "name",
                                "",
                            ),
                        "start_time_unix_nano":
                            start_ns,
                        "end_time_unix_nano":
                            end_ns,
                        "duration_ms":
                            max(
                                0,
                                end_ns
                                - start_ns,
                            )
                            / 1_000_000.0,
                        "status":
                            _status_name(
                                status
                            ),
                        "status_description":
                            status.get(
                                "message",
                                "",
                            ),
                        "attributes":
                            _attributes(
                                span.get(
                                    "attributes",
                                    [],
                                )
                            ),
                        "resource":
                            dict(
                                resource
                            ),
                        "instrumentation_scope":
                            {
                                "name":
                                    scope_name,
                                "version":
                                    scope_version,
                            },
                    }
                )

    return spans


def _load_jsonl(
    text,
):
    payloads = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        stripped = line.strip()

        if not stripped:
            continue

        try:
            payloads.append(
                json.loads(
                    stripped
                )
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid JSONL at "
                f"line {line_number}: "
                f"{exc}"
            ) from exc

    return payloads


def load_span_file(
    path,
):
    path = Path(path)

    text = path.read_text()

    if not text.strip():
        raise ValueError(
            f"Trace input is empty: {path}"
        )

    try:
        document = json.loads(
            text
        )
    except json.JSONDecodeError:
        document = None

    if isinstance(
        document,
        list,
    ):
        return document

    if isinstance(
        document,
        dict,
    ):
        if "resourceSpans" in document:
            return otlp_payload_to_spans(
                document
            )

        raise ValueError(
            "Unsupported JSON trace object. "
            "Expected OTLP resourceSpans."
        )

    payloads = _load_jsonl(
        text
    )

    spans = []

    for payload in payloads:
        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "OTLP JSONL entries "
                "must be JSON objects."
            )

        if "resourceSpans" not in payload:
            continue

        spans.extend(
            otlp_payload_to_spans(
                payload
            )
        )

    if not spans:
        raise ValueError(
            "No OTLP resourceSpans "
            f"found in {path}"
        )

    return spans
