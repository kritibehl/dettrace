# Case Study: Duplicate Dequeue Race Condition

## Scenario

Two workers attempt to dequeue tasks simultaneously.

## Expected Behavior

Worker A → Task 1  
Worker B → Task 2  

## Actual Behavior

Worker A → Task 1  
Worker B → Task 1  

Task 2 skipped.

---

## DetTrace Output

Event 5:

Expected:
TASK_DEQUEUED task=1

Actual:
TASK_DEQUEUED task=2

---

## Root Cause

Missing synchronization around queue access.

---

## Impact

- Duplicate processing
- Lost tasks
- State inconsistency

---

## Fix

Introduce atomic dequeue or locking mechanism.

---

## Insight

The visible failure occurred later.

The real issue started at event index 5.

