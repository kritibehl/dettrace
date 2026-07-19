#!/usr/bin/env python3
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

REPORT_JSON = Path("performance_benchmarks/replay_benchmark_report.json")
REPORT_MD = Path("reports/replay_performance_report.md")

TRACE_SIZES = [10_000, 100_000, 1_000_000]


def make_event(index: int) -> str:
    return f"{index}:sensor_event:{index % 17}:{index % 101}"


def build_trace(size: int, divergence_index: int | None = None):
    trace = [make_event(i) for i in range(size)]
    if divergence_index is not None:
        trace[divergence_index] = f"{divergence_index}:corrupted_event"
    return trace


def sha256_trace(trace):
    hasher = hashlib.sha256()
    for event in trace:
        hasher.update(event.encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def linear_first_divergence(expected, observed):
    for i, (left, right) in enumerate(zip(expected, observed)):
        if left != right:
            return i
    if len(expected) != len(observed):
        return min(len(expected), len(observed))
    return None


def prefix_hashes(trace, block_size=1024):
    hashes = []
    hasher = hashlib.sha256()

    for i, event in enumerate(trace, start=1):
        hasher.update(event.encode("utf-8"))
        hasher.update(b"\n")

        if i % block_size == 0 or i == len(trace):
            hashes.append(hasher.hexdigest())

    return hashes


def indexed_first_divergence(expected, observed, block_size=1024):
    expected_hashes = prefix_hashes(expected, block_size)
    observed_hashes = prefix_hashes(observed, block_size)

    low = 0
    high = min(len(expected_hashes), len(observed_hashes)) - 1
    first_bad_block = None

    while low <= high:
        mid = (low + high) // 2
        if expected_hashes[mid] == observed_hashes[mid]:
            low = mid + 1
        else:
            first_bad_block = mid
            high = mid - 1

    if first_bad_block is None:
        if len(expected) != len(observed):
            return min(len(expected), len(observed))
        return None

    start = first_bad_block * block_size
    end = min(start + block_size, len(expected), len(observed))

    for i in range(start, end):
        if expected[i] != observed[i]:
            return i

    return min(len(expected), len(observed))


def current_rss_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss / (1024 * 1024) if usage.ru_maxrss > 10_000_000 else usage.ru_maxrss / 1024


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    return result, elapsed


def benchmark_size(size: int):
    divergence_index = size - max(10, size // 10)

    mem_before = current_rss_mb()

    build_start = time.perf_counter()
    expected = build_trace(size)
    observed = build_trace(size, divergence_index)
    build_seconds = time.perf_counter() - build_start

    mem_after_build = current_rss_mb()

    expected_hash, checksum_seconds = timed(sha256_trace, expected)
    observed_hash = sha256_trace(observed)

    linear_index, linear_seconds = timed(
        linear_first_divergence,
        expected,
        observed,
    )

    indexed_index, indexed_seconds = timed(
        indexed_first_divergence,
        expected,
        observed,
    )

    replay_start = time.perf_counter()
    replay_checksum = sha256_trace(observed)
    replay_seconds = time.perf_counter() - replay_start

    throughput = size / replay_seconds if replay_seconds else 0.0

    return {
        "trace_size": size,
        "expected_divergence_index": divergence_index,
        "linear_divergence_index": linear_index,
        "indexed_divergence_index": indexed_index,
        "build_seconds": round(build_seconds, 6),
        "checksum_seconds": round(checksum_seconds, 6),
        "linear_scan_seconds": round(linear_seconds, 6),
        "indexed_lookup_seconds": round(indexed_seconds, 6),
        "replay_seconds": round(replay_seconds, 6),
        "throughput_events_per_second": round(throughput, 2),
        "rss_before_mb": round(mem_before, 2),
        "rss_after_build_mb": round(mem_after_build, 2),
        "estimated_trace_memory_delta_mb": round(max(0.0, mem_after_build - mem_before), 2),
        "expected_checksum": expected_hash,
        "observed_checksum": observed_hash,
        "replay_checksum": replay_checksum,
        "checksum_reproducible": observed_hash == replay_checksum,
        "divergence_results_match": (
            linear_index == divergence_index
            and indexed_index == divergence_index
        ),
    }


def write_markdown(report):
    lines = [
        "# Deterministic Replay Performance Report",
        "",
        "## Safe scope",
        "",
        "Synthetic trace replay benchmark for deterministic debugging workflows.",
        "This is not a production profiler, runtime, kernel tracer, or hardware benchmark.",
        "",
        "## Method",
        "",
        "- benchmark sizes: 10K, 100K, and 1M events",
        "- deterministic SHA-256 checksum validation",
        "- linear first-divergence scan",
        "- prefix-hash indexed divergence lookup",
        "- replay throughput in events per second",
        "- process RSS memory observation",
        "",
        "The indexed lookup is valid because monotonic prefix hashes identify the earliest mismatching block before a linear scan inside that block.",
        "",
        "## Results",
        "",
        "| Events | Linear ms | Indexed ms | Replay events/s | Memory delta MB | Checksum stable | Divergence correct |",
        "|---:|---:|---:|---:|---:|---|---|",
    ]

    for item in report["results"]:
        lines.append(
            f"| {item['trace_size']:,} "
            f"| {item['linear_scan_seconds'] * 1000:.3f} "
            f"| {item['indexed_lookup_seconds'] * 1000:.3f} "
            f"| {item['throughput_events_per_second']:,.2f} "
            f"| {item['estimated_trace_memory_delta_mb']:.2f} "
            f"| {item['checksum_reproducible']} "
            f"| {item['divergence_results_match']} |"
        )

    lines.extend([
        "",
        "## Complexity",
        "",
        "- linear divergence scan: `O(n)` time and `O(1)` auxiliary space",
        "- prefix-hash index construction: `O(n)` time and `O(n / block_size)` stored hashes",
        "- indexed lookup after index creation: `O(log blocks + block_size)`",
        "- deterministic checksum generation: `O(n)`",
        "",
        "## Interpretation",
        "",
        "Replay remains deterministic across all benchmark sizes when the same observed trace produces the same checksum and both lookup methods isolate the same first-divergence index.",
        "",
    ])

    REPORT_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sizes",
        default=",".join(str(x) for x in TRACE_SIZES),
        help="Comma-separated trace sizes",
    )
    args = parser.parse_args()

    sizes = [int(value.strip()) for value in args.sizes.split(",") if value.strip()]
    results = [benchmark_size(size) for size in sizes]

    report = {
        "workflow": "deterministic-replay-performance-benchmark",
        "safe_claim": "synthetic deterministic replay performance benchmark; not production runtime profiling",
        "results": results,
        "all_checksums_reproducible": all(
            item["checksum_reproducible"] for item in results
        ),
        "all_divergence_results_match": all(
            item["divergence_results_match"] for item in results
        ),
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    write_markdown(report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
