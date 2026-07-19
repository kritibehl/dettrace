# Deterministic Replay Performance Report

## Safe scope

Synthetic trace replay benchmark for deterministic debugging workflows.
This is not a production profiler, runtime, kernel tracer, or hardware benchmark.

## Method

- benchmark sizes: 10K, 100K, and 1M events
- deterministic SHA-256 checksum validation
- linear first-divergence scan
- prefix-hash indexed divergence lookup
- replay throughput in events per second
- process RSS memory observation

The indexed lookup is valid because monotonic prefix hashes identify the earliest mismatching block before a linear scan inside that block.

## Results

| Events | Linear ms | Indexed ms | Replay events/s | Memory delta MB | Checksum stable | Divergence correct |
|---:|---:|---:|---:|---:|---|---|
| 10,000 | 0.492 | 3.165 | 8,985,396.02 | 1.23 | True | True |
| 100,000 | 4.554 | 32.199 | 9,372,949.66 | 13.52 | True | True |
| 1,000,000 | 36.495 | 343.486 | 9,121,285.79 | 120.91 | True | True |

## Complexity

- linear divergence scan: `O(n)` time and `O(1)` auxiliary space
- prefix-hash index construction: `O(n)` time and `O(n / block_size)` stored hashes
- indexed lookup after index creation: `O(log blocks + block_size)`
- deterministic checksum generation: `O(n)`

## Interpretation

Replay remains deterministic across all benchmark sizes when the same observed trace produces the same checksum and both lookup methods isolate the same first-divergence index.
