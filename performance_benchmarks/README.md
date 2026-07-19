# DetTrace Replay Performance Benchmarks

This benchmark measures deterministic replay behavior across synthetic traces containing:

- 10,000 events
- 100,000 events
- 1,000,000 events

## Measurements

- trace-generation overhead
- deterministic checksum time
- replay throughput in events per second
- process RSS memory change
- linear first-divergence latency
- indexed first-divergence latency
- deterministic result consistency

## Lookup methods

### Linear scan

Scans expected and observed traces from the beginning.

Complexity:

    O(n)

### Prefix-hash indexed lookup

Builds monotonic prefix checksums over fixed-size blocks, performs binary search for the earliest mismatching block, then performs a linear scan inside that block.

Index construction:

    O(n)

Lookup after index creation:

    O(log blocks + block_size)

This indexed approach is only valid because prefix hashes preserve the property that every block before the first divergence has an identical cumulative checksum.

## Safe scope

Synthetic deterministic replay benchmarking only.

This does not claim production runtime profiling, kernel tracing, hardware benchmarking, or profiler integration.
