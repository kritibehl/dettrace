#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import random
import time
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from file_span_exporter import JsonFileSpanExporter


def sleep_ms(value: float):
    time.sleep(value / 1000.0)


def configure_tracing(output: str):
    resource = Resource.create(
        {
            "service.name": "checkout-demo",
            "deployment.environment": "dettrace-demo",
        }
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        SimpleSpanProcessor(JsonFileSpanExporter(output))
    )

    trace.set_tracer_provider(provider)
    return trace.get_tracer("dettrace.checkout.demo")


def run_request(tracer, mode: str, request_number: int):
    with tracer.start_as_current_span(
        "checkout.request",
        attributes={
            "service.name": "checkout",
            "request.number": request_number,
        },
    ):
        with tracer.start_as_current_span(
            "auth.validate",
            attributes={"service.name": "auth"},
        ):
            sleep_ms(4 + random.uniform(0, 2))

        with tracer.start_as_current_span(
            "inventory.reserve",
            attributes={"service.name": "inventory"},
        ):
            with tracer.start_as_current_span(
                "inventory.database",
                attributes={
                    "service.name": "inventory-db",
                    "db.system": "postgresql",
                },
            ):
                sleep_ms(10 + random.uniform(0, 4))

            if mode == "candidate":
                with tracer.start_as_current_span(
                    "redis.lookup",
                    attributes={
                        "service.name": "redis",
                        "db.system": "redis",
                    },
                ):
                    sleep_ms(35 + random.uniform(0, 6))

                sleep_ms(55 + random.uniform(0, 10))
            else:
                sleep_ms(4 + random.uniform(0, 3))

        with tracer.start_as_current_span(
            "payment.authorize",
            attributes={"service.name": "payment"},
        ):
            sleep_ms(8 + random.uniform(0, 3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["baseline", "candidate"],
        required=True,
    )
    parser.add_argument(
        "--output",
        required=True,
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=30,
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists():
        output.unlink()

    random.seed(42)

    tracer = configure_tracing(str(output))

    for request_number in range(args.requests):
        run_request(tracer, args.mode, request_number)

    provider = trace.get_tracer_provider()

    if hasattr(provider, "force_flush"):
        provider.force_flush()

    if hasattr(provider, "shutdown"):
        provider.shutdown()

    print(
        f"captured mode={args.mode} "
        f"requests={args.requests} "
        f"output={output}"
    )


if __name__ == "__main__":
    main()
