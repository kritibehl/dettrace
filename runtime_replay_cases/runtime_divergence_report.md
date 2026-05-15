# Runtime Divergence Replay Report

This report documents small replayable runtime-debugging traces for interpreter-style execution behavior.

These are diagnostic replay artifacts, not a JIT compiler, VM implementation, compiler backend, runtime optimizer, or JavaScript engine.

## Case 1: Cache fallback trace

### Expected path

    load_object_shape(shape_A)
    -> inline_cache_hit
    -> property_load
    -> return_value

### Observed path

    load_object_shape(shape_B)
    -> inline_cache_miss
    -> generic_property_lookup
    -> return_value

### First divergence

    index: 0
    expected_event: load_object_shape:shape_A
    actual_event: load_object_shape:shape_B

### Interpretation

The cached shape assumption was invalidated before the property load. The replay shows fallback from a cached property-load path to a generic lookup path.

## Case 2: Invalid branch target trace

### Expected path

    decode_branch(target_validated)
    -> jump_to_target(pc_24)
    -> execute_block
    -> return_value

### Observed path

    decode_branch(target_unchecked)
    -> jump_to_target(pc_999)
    -> invalid_branch_target
    -> trap

### First divergence

    index: 0
    expected_event: decode_branch:target_validated
    actual_event: decode_branch:target_unchecked

### Interpretation

The runtime trace shows a branch target that was not validated before updating the program counter. The replay isolates the missing validation step before the invalid branch trap.

## Safe claim

DetTrace demonstrates replay debugging of runtime-style failures by comparing expected versus observed execution traces and isolating the first divergence.
