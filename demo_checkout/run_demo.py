#!/usr/bin/env python3

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
)
from opentelemetry.trace import (
    Status,
    StatusCode,
)

from file_span_exporter import (
    JsonFileSpanExporter,
)


def sleep_ms(
    value: float,
):
    time.sleep(
        value / 1000.0
    )


def configure_tracing(
    mode: str,
    exporter: str,
    output: str | None,
    otlp_endpoint: str,
):
    resource = Resource.create(
        {
            "service.name":
                "checkout-demo",
            "deployment.environment":
                "dettrace-demo",
            "dettrace.mode":
                mode,
        }
    )

    provider = TracerProvider(
        resource=resource
    )

    if exporter == "file":
        if not output:
            raise ValueError(
                "--output is required "
                "when --exporter=file"
            )

        provider.add_span_processor(
            SimpleSpanProcessor(
                JsonFileSpanExporter(
                    output
                )
            )
        )

    elif exporter == "otlp":
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=(
                        otlp_endpoint
                    ),
                    insecure=True,
                )
            )
        )

    else:
        raise ValueError(
            "unsupported exporter: "
            f"{exporter}"
        )

    trace.set_tracer_provider(
        provider
    )

    return (
        trace.get_tracer(
            "dettrace.checkout.demo"
        ),
        provider,
    )


def run_checkout_request(
    tracer,
    mode: str,
    request_number: int,
):
    core_rng = random.Random(
        42 + request_number
    )

    candidate_rng = random.Random(
        10000 + request_number
    )

    candidate_error = (
        mode == "candidate"
        and request_number % 5 == 0
    )

    with tracer.start_as_current_span(
        "checkout.request",
        attributes={
            "service.name":
                "checkout",
            "request.number":
                request_number,
            "http.request.method":
                "POST",
            "http.route":
                "/checkout",
            "dettrace.request_shape":
                "checkout",
        },
    ) as checkout_span:

        with tracer.start_as_current_span(
            "auth.validate",
            attributes={
                "service.name":
                    "auth",
            },
        ):
            sleep_ms(
                4
                + core_rng.uniform(
                    0,
                    2,
                )
            )

        with tracer.start_as_current_span(
            "inventory.reserve",
            attributes={
                "service.name":
                    "inventory",
            },
        ) as inventory_span:

            with tracer.start_as_current_span(
                "inventory.database",
                attributes={
                    "service.name":
                        "inventory-db",
                    "db.system":
                        "postgresql",
                },
            ):
                sleep_ms(
                    10
                    + core_rng.uniform(
                        0,
                        4,
                    )
                )

            if mode == "candidate":
                with tracer.start_as_current_span(
                    "redis.lookup",
                    attributes={
                        "service.name":
                            "redis",
                        "db.system":
                            "redis",
                    },
                ):
                    sleep_ms(
                        35
                        + candidate_rng.uniform(
                            0,
                            6,
                        )
                    )

                sleep_ms(
                    55
                    + candidate_rng.uniform(
                        0,
                        10,
                    )
                )

            else:
                sleep_ms(
                    4
                    + core_rng.uniform(
                        0,
                        3,
                    )
                )

            if candidate_error:
                inventory_span.set_attribute(
                    "error.type",
                    "synthetic_inventory_failure",
                )

                inventory_span.set_status(
                    Status(
                        status_code=(
                            StatusCode.ERROR
                        ),
                        description=(
                            "synthetic candidate "
                            "inventory regression"
                        ),
                    )
                )

        with tracer.start_as_current_span(
            "payment.authorize",
            attributes={
                "service.name":
                    "payment",
            },
        ):
            sleep_ms(
                8
                + core_rng.uniform(
                    0,
                    3,
                )
            )

        if candidate_error:
            checkout_span.set_attribute(
                "error.type",
                "synthetic_checkout_failure",
            )

            checkout_span.set_status(
                Status(
                    status_code=(
                        StatusCode.ERROR
                    ),
                    description=(
                        "synthetic candidate "
                        "checkout regression"
                    ),
                )
            )


def run_health_request(
    tracer,
    request_number: int,
):
    rng = random.Random(
        20000 + request_number
    )

    with tracer.start_as_current_span(
        "health.request",
        attributes={
            "service.name":
                "checkout",
            "request.number":
                request_number,
            "http.request.method":
                "GET",
            "http.route":
                "/health",
            "dettrace.request_shape":
                "health",
        },
    ):
        with tracer.start_as_current_span(
            "health.check",
            attributes={
                "service.name":
                    "checkout",
            },
        ):
            sleep_ms(
                1
                + rng.uniform(
                    0,
                    1,
                )
            )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=[
            "baseline",
            "candidate",
        ],
        required=True,
    )

    parser.add_argument(
        "--exporter",
        choices=[
            "file",
            "otlp",
        ],
        default="file",
    )

    parser.add_argument(
        "--output",
    )

    parser.add_argument(
        "--otlp-endpoint",
        default="localhost:4317",
    )

    parser.add_argument(
        "--requests",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--health-requests",
        type=int,
        default=10,
    )

    args = parser.parse_args()

    if (
        args.exporter == "file"
        and not args.output
    ):
        parser.error(
            "--output is required "
            "for --exporter=file"
        )

    if args.output:
        output = Path(
            args.output
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if (
            args.exporter == "file"
            and output.exists()
        ):
            output.unlink()

    tracer, provider = (
        configure_tracing(
            mode=args.mode,
            exporter=args.exporter,
            output=args.output,
            otlp_endpoint=(
                args.otlp_endpoint
            ),
        )
    )

    for request_number in range(
        args.requests
    ):
        run_checkout_request(
            tracer,
            args.mode,
            request_number,
        )

    for request_number in range(
        args.health_requests
    ):
        run_health_request(
            tracer,
            request_number,
        )

    provider.force_flush()

    provider.shutdown()

    destination = (
        args.output
        if args.exporter == "file"
        else args.otlp_endpoint
    )

    print(
        f"captured mode="
        f"{args.mode} "
        f"exporter="
        f"{args.exporter} "
        f"checkout_requests="
        f"{args.requests} "
        f"health_requests="
        f"{args.health_requests} "
        f"destination="
        f"{destination}"
    )


if __name__ == "__main__":
    main()
