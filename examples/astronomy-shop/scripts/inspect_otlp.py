import argparse
import json
from collections import Counter
from pathlib import Path


def decode_any(value):
    if not isinstance(value, dict):
        return value

    scalar_keys = (
        "stringValue",
        "boolValue",
        "intValue",
        "doubleValue",
        "bytesValue",
    )

    for key in scalar_keys:
        if key in value:
            return value[key]

    if "arrayValue" in value:
        values = value[
            "arrayValue"
        ].get(
            "values",
            [],
        )

        return [
            decode_any(item)
            for item in values
        ]

    return value


def attributes(items):
    result = {}

    for item in items or []:
        key = item.get("key")

        if not key:
            continue

        result[key] = decode_any(
            item.get(
                "value",
                {},
            )
        )

    return result


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
    )

    args = parser.parse_args()

    path = Path(args.path)

    services = Counter()
    operations = Counter()
    roots = Counter()
    routes = Counter()
    traces = set()

    batches = 0
    spans = 0

    for line in path.read_text().splitlines():
        if not line.strip():
            continue

        payload = json.loads(line)

        batches += 1

        for rs in payload.get(
            "resourceSpans",
            [],
        ):
            resource = attributes(
                rs.get(
                    "resource",
                    {},
                ).get(
                    "attributes",
                    [],
                )
            )

            service = resource.get(
                "service.name",
                "unknown",
            )

            scopes = rs.get(
                "scopeSpans",
                rs.get(
                    "instrumentationLibrarySpans",
                    [],
                ),
            )

            for scope in scopes:
                for span in scope.get(
                    "spans",
                    [],
                ):
                    spans += 1

                    trace_id = span.get(
                        "traceId",
                        "",
                    )

                    if trace_id:
                        traces.add(
                            trace_id
                        )

                    name = span.get(
                        "name",
                        "unknown",
                    )

                    services[
                        service
                    ] += 1

                    operations[
                        (
                            service,
                            name,
                        )
                    ] += 1

                    attrs = attributes(
                        span.get(
                            "attributes",
                            [],
                        )
                    )

                    route = attrs.get(
                        "http.route"
                    )

                    if route:
                        method = (
                            attrs.get(
                                "http.request.method"
                            )
                            or attrs.get(
                                "http.method"
                            )
                            or ""
                        )

                        routes[
                            (
                                method,
                                route,
                            )
                        ] += 1

                    parent = span.get(
                        "parentSpanId",
                        "",
                    )

                    if not parent:
                        roots[
                            (
                                service,
                                name,
                            )
                        ] += 1

    print(
        "OTLP batches:",
        batches,
    )

    print(
        "spans:",
        spans,
    )

    print(
        "unique trace IDs:",
        len(traces),
    )

    print()
    print(
        "===== SERVICES ====="
    )

    for value, count in services.most_common(
        40
    ):
        print(
            f"{count:7d}",
            value,
        )

    print()
    print(
        "===== OPERATIONS ====="
    )

    for value, count in operations.most_common(
        70
    ):
        print(
            f"{count:7d}",
            value,
        )

    print()
    print(
        "===== ROOTS ====="
    )

    for value, count in roots.most_common(
        50
    ):
        print(
            f"{count:7d}",
            value,
        )

    print()
    print(
        "===== HTTP ROUTES ====="
    )

    for value, count in routes.most_common(
        50
    ):
        print(
            f"{count:7d}",
            value,
        )


if __name__ == "__main__":
    main()
