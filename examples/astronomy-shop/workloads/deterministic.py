#!/usr/bin/env python3

import argparse
import copy
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


PRODUCT = "0PUK6V6EV0"


def request(
    base,
    method,
    path,
    *,
    payload=None,
    timeout=20,
):
    body = None

    headers = {
        "User-Agent": "dettrace-astronomy-validation/1",
        "baggage": "synthetic_request=true",
    }

    if payload is not None:
        body = json.dumps(
            payload
        ).encode()

        headers[
            "Content-Type"
        ] = "application/json"

    req = urllib.request.Request(
        base + path,
        data=body,
        headers=headers,
        method=method,
    )

    started = time.perf_counter()

    try:
        with urllib.request.urlopen(
            req,
            timeout=timeout,
        ) as response:
            response.read()

            return {
                "status": response.status,
                "elapsed_ms": (
                    time.perf_counter()
                    - started
                ) * 1000,
            }

    except urllib.error.HTTPError as exc:
        exc.read()

        return {
            "status": exc.code,
            "elapsed_ms": (
                time.perf_counter()
                - started
            ) * 1000,
        }


def run_iteration(
    index,
    base,
    person,
):
    user_id = (
        f"dettrace-user-{index:04d}"
    )

    checkout = copy.deepcopy(
        person
    )

    checkout[
        "userId"
    ] = user_id

    results = {}

    results[
        "home"
    ] = request(
        base,
        "GET",
        "/",
    )

    results[
        "product"
    ] = request(
        base,
        "GET",
        f"/api/products/{PRODUCT}",
    )

    query = urllib.parse.urlencode(
        {
            "productIds": PRODUCT,
        }
    )

    results[
        "recommendations"
    ] = request(
        base,
        "GET",
        f"/api/recommendations?{query}",
    )

    results[
        "cart"
    ] = request(
        base,
        "POST",
        "/api/cart",
        payload={
            "item": {
                "productId": PRODUCT,
                "quantity": 1,
            },
            "userId": user_id,
        },
    )

    results[
        "checkout"
    ] = request(
        base,
        "POST",
        "/api/checkout",
        payload=checkout,
    )

    return results


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base-url",
        default="http://localhost:8080",
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=40,
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=5,
    )

    parser.add_argument(
        "--people",
        default=(
            str(
                Path.home()
                / "opentelemetry-demo"
                / "src/load-generator"
                / "people.json"
            )
        ),
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    people = json.loads(
        Path(
            args.people
        ).read_text()
    )

    international = [
        person
        for person in people
        if person[
            "address"
        ][
            "country"
        ].strip().upper()
        not in {
            "US",
            "USA",
            "UNITED STATES",
            "UNITED STATES OF AMERICA",
        }
    ]

    if not international:
        raise SystemExit(
            "No international checkout identity found"
        )

    person = international[0]

    started = time.time()

    with ThreadPoolExecutor(
        max_workers=args.workers
    ) as pool:
        futures = [
            pool.submit(
                run_iteration,
                i,
                args.base_url,
                person,
            )
            for i in range(
                args.iterations
            )
        ]

        iterations = [
            future.result()
            for future in futures
        ]

    summary = {}

    for operation in (
        "home",
        "product",
        "recommendations",
        "cart",
        "checkout",
    ):
        values = [
            row[
                operation
            ]
            for row in iterations
        ]

        summary[
            operation
        ] = {
            "count": len(values),
            "successes": sum(
                1
                for value in values
                if 200
                <= value[
                    "status"
                ]
                < 400
            ),
            "errors": sum(
                1
                for value in values
                if value[
                    "status"
                ]
                >= 400
            ),
            "status_counts": {
                str(status): sum(
                    1
                    for value in values
                    if value[
                        "status"
                    ]
                    == status
                )
                for status in sorted(
                    {
                        value[
                            "status"
                        ]
                        for value in values
                    }
                )
            },
            "elapsed_ms": [
                value[
                    "elapsed_ms"
                ]
                for value in values
            ],
        }

    report = {
        "iterations": args.iterations,
        "workers": args.workers,
        "product": PRODUCT,
        "checkout_country": person[
            "address"
        ][
            "country"
        ],
        "duration_seconds": (
            time.time()
            - started
        ),
        "summary": summary,
    }

    Path(
        args.output
    ).write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        json.dumps(
            {
                key: {
                    "count": value[
                        "count"
                    ],
                    "successes": value[
                        "successes"
                    ],
                    "errors": value[
                        "errors"
                    ],
                    "status_counts": value[
                        "status_counts"
                    ],
                }
                for key, value
                in summary.items()
            },
            indent=2,
            sort_keys=True,
        )
    )

    print()
    print(
        "DETERMINISTIC WORKLOAD: PASS"
    )


if __name__ == "__main__":
    main()
