import json

import pytest

from trace_regression.ingest import (
    load_span_file,
    otlp_payload_to_spans,
)


def make_payload(
    trace_id="a" * 32,
    status="STATUS_CODE_OK",
):
    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {
                                "stringValue": "checkout-demo"
                            },
                        },
                        {
                            "key": "dettrace.mode",
                            "value": {
                                "stringValue": "baseline"
                            },
                        },
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "dettrace.test",
                        },
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": "1" * 16,
                                "parentSpanId": "",
                                "name": "checkout.request",
                                "startTimeUnixNano": "1000000",
                                "endTimeUnixNano": "11000000",
                                "attributes": [
                                    {
                                        "key": "service.name",
                                        "value": {
                                            "stringValue": "checkout"
                                        },
                                    },
                                    {
                                        "key": "http.request.method",
                                        "value": {
                                            "stringValue": "POST"
                                        },
                                    },
                                    {
                                        "key": "http.route",
                                        "value": {
                                            "stringValue": "/checkout"
                                        },
                                    },
                                ],
                                "status": {
                                    "code": status
                                },
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_converts_otlp_resource_spans():
    spans = otlp_payload_to_spans(
        make_payload()
    )

    assert len(spans) == 1

    span = spans[0]

    assert span["trace_id"] == "a" * 32
    assert span["name"] == "checkout.request"
    assert span["parent_span_id"] is None
    assert span["duration_ms"] == pytest.approx(10.0)
    assert span["status"] == "OK"

    assert (
        span["attributes"]["http.request.method"]
        == "POST"
    )

    assert (
        span["attributes"]["http.route"]
        == "/checkout"
    )

    assert (
        span["resource"]["dettrace.mode"]
        == "baseline"
    )


def test_maps_otlp_error_status():
    spans = otlp_payload_to_spans(
        make_payload(
            trace_id="b" * 32,
            status="STATUS_CODE_ERROR",
        )
    )

    assert spans[0]["status"] == "ERROR"


def test_reads_collector_otlp_jsonl(tmp_path):
    path = tmp_path / "collector.otlp.jsonl"

    path.write_text(
        json.dumps(
            make_payload("c" * 32)
        )
        + "\n"
        + json.dumps(
            make_payload("d" * 32)
        )
        + "\n"
    )

    spans = load_span_file(path)

    assert len(spans) == 2

    assert {
        span["trace_id"]
        for span in spans
    } == {
        "c" * 32,
        "d" * 32,
    }


def test_existing_internal_json_remains_supported(
    tmp_path,
):
    path = tmp_path / "internal.json"

    original = [
        {
            "trace_id": "trace-1",
            "span_id": "span-1",
            "name": "request",
        }
    ]

    path.write_text(
        json.dumps(original)
    )

    assert load_span_file(path) == original


def test_cli_loader_accepts_collector_otlp_jsonl(
    tmp_path,
):
    from trace_regression.cli import (
        load_raw_traces,
    )

    path = (
        tmp_path
        / "collector-cli.otlp.jsonl"
    )

    path.write_text(
        json.dumps(
            make_payload(
                "e" * 32
            )
        )
        + "\n"
    )

    traces = load_raw_traces(
        path
    )

    assert len(traces) == 1

    assert len(
        traces[0]
    ) == 1

    assert traces[0][0][
        "name"
    ] == "checkout.request"
