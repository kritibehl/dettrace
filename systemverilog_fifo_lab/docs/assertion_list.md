# FIFO Assertion List

## Reset assertion

Verify reset clears FIFO pointers and count.

## Full flag assertion

Verify full flag asserts only when FIFO capacity is reached.

## Empty flag assertion

Verify empty flag asserts only when FIFO contains no data.

## Overflow assertion

Verify writes are rejected while full flag is active.

## Underflow assertion

Verify reads are rejected while empty flag is active.

## Ordering assertion

Verify dequeue ordering matches enqueue ordering.

## Pointer stability assertion

Verify pointers do not advance incorrectly during blocked operations.
