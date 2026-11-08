# Heap Data Structures Implementation Analysis and Applications

Ravi Teja Ponnekanti  
Algorithms and Data Structures - MSCS532  
Assignment 4 - November 8, 2026

Repository: https://github.com/ravitejaponnekanti/MSCS532_Assignment4

## Overview

This report evaluates an array-based Heapsort implementation and an indexed
binary-heap priority queue. It connects correctness and complexity analysis
with measured sorting times and a reproducible scheduling simulation.
Heapsort provides an O(n log n) time upper bound with O(1) auxiliary space.
In the measured 8,000-element distinct-key cases, Merge Sort was fastest,
while randomized Quicksort benefited most from repeated values. In the
scheduling example, priority dispatch reduced total tardiness from 6 to 3
time units without reducing the number of missed deadlines.

## 1 Heapsort design and correctness

`heapsort.py` stores a complete binary tree directly in the input list. For
zero-based index i, the parent is floor((i - 1)/2), the left child is 2i + 1,
and the right child is 2i + 2. A max-heap requires every parent to be at least
as large as its children; consequently its root is a maximum element.
Array indexing avoids explicit node objects and parent/child pointers.

`build_max_heap` processes internal nodes from n//2 - 1 back to zero. Each
call to iterative `sift_down` assumes the child subtrees are heaps, swaps the
root with its larger child when necessary, and continues down that path.
The only possible violation moves down with the swapped value. Induction
from the leaves establishes the full heap property after construction.

During sorting, the maximum swaps with the last element in the active heap.
The active boundary decreases, and sifting repairs the root. At each iteration,
the prefix is a max-heap and the suffix is sorted, with every suffix value
at least as large as every remaining heap value. This invariant proves ascending
order at termination. Empty, singleton, negative, sorted, reversed, and duplicate
inputs are supported. The implementation does not call heapq or a built-in sort.

## 2 Rigorous complexity analysis

A sift traverses at most the height of a complete binary tree, floor(log2 n),
and performs constant work per visited level, so its worst cost is O(log n).
Building a heap by n independent insertions would cost O(n log n), but the
submitted bottom-up method is linear. There are O(n/2^h) nodes of height h,
and each costs O(h). Hence its total cost is bounded by

```text
sum(h >= 1) O(n*h/2^h) = O(n) * sum(h >= 1) h/2^h = O(n).
```

The finite geometric derivative sum is bounded by 2. Visiting the internal
nodes also costs Omega(n), so heap construction is Theta(n), including when
the input is already a heap (Demaine et al., 2020). Logarithms in this report
are base two unless otherwise stated; changing the base changes only a
constant factor in these asymptotic bounds.

Sorting then performs n - 1 extractions. Each costs O(log k) with k active
elements. Therefore, for every input,

```text
T(n) <= O(n) + sum(k = 2 to n) O(log k)
     = O(n) + O(log(n!)) = O(n log n).
```

This proves the requested O(n log n) upper bound in the best, average, and
worst cases; it does not assert that every extraction actually traverses the
full height. For distinct keys, standard binary Heapsort has tight
Theta(n log n) best, average, and worst bounds. The best-case lower bound is
specific to Heapsort, not a consequence of the generic comparison-sorting
lower bound, which only supplies worst-case and uniform-random-permutation
average lower bounds. Sedgewick and Wayne's sorting summary explicitly notes
the distinct-key qualification (n.d.).

If duplicates are allowed, a tight best-case claim needs care. In this code,
all-equal input stops every sift after a constant number of comparisons.
Building and the n - 1 extraction iterations then take Theta(n), still within
O(n log n). Already sorted input is not that same special case. Average-case
Theta(n log n) here refers to uniformly random permutations of distinct keys;
a different input distribution, such as all-equal arrays, has a different average.

### Heapsort time bounds for this implementation

| Case and input assumption | Tight running time | O(n log n) upper bound |
|---|---|---|
| Best case with arbitrary duplicate keys allowed | Theta(n), attained by all-equal input | Holds |
| Best case restricted to distinct keys | Theta(n log n) | Holds |
| Average over uniform random permutations of distinct keys | Theta(n log n) | Holds |
| Worst case | Theta(n log n) | Holds |

The linear duplicate-key best case therefore agrees with the assignment's
O(n log n) requirement: a linear function is also O(n log n). It would be
incorrect to replace that upper bound with a tight Theta(n log n) claim for
every possible duplicate-key input.

Heapsort changes the original list using a fixed number of indices and a
temporary swap, with iterative sifting. Auxiliary space is O(1); the input
itself occupies O(n). There is no recursion stack or second array. It is not
stable because distant swaps can change the relative order of equal records.
Python comparison and indexing overhead affects constants. These time bounds
assume constant-cost element comparisons; arbitrary expensive comparison
methods would add their own cost.

## 3 Empirical sorting comparison

`comparison_sorts.py` supplies independent educational implementations of
randomized three-way Quicksort and stable top-down Merge Sort. Quicksort chooses
a uniform pivot inside each active subarray and groups equal keys together;
its expected time is O(n log n) and worst time O(n^2). Processing smaller
partitions first limits pending stack space to O(log n). Merge Sort divides
ranges in half and merges with one reusable buffer: time Theta(n log n) for
this unoptimized implementation and auxiliary space O(n), plus O(log n)
recursion depth. No code imports another assignment directory.

The experiment uses sizes 500, 2,000, and 8,000 and four distributions:
unique random integers, ascending unique integers, descending unique integers,
and integers drawn from eight repeated values. Five trials vary random data
and Quicksort seeds. Every algorithm receives the same input values per trial,
and the execution order rotates. Wall times use `perf_counter_ns`; input
copying, generation, and output validation are excluded. Algorithm allocations
and Quicksort random-generator construction are included. Every output is
checked against Python's sorted result. The CSV retains median, minimum,
and maximum times for all 36 algorithm/dataset/size cases.

These are local Python 3.12.14 measurements on Windows 11. Exact platform
metadata is saved in `environment.json`. No memory profiler affects the timed
runs; the space discussion is analytical, not a claim of measured total RAM.

### Table 1 Median running times in milliseconds

| Size | Input | Heapsort ms | Quicksort ms | Merge Sort ms |
|---:|---|---:|---:|---:|
| 500 | random | 0.9138 | 1.0327 | 0.8665 |
| 500 | sorted | 1.0700 | 1.1601 | 0.7545 |
| 500 | reverse | 1.0789 | 1.1285 | 0.7635 |
| 500 | repeated | 0.8964 | 0.1939 | 0.9852 |
| 2,000 | random | 4.9568 | 4.9626 | 4.1188 |
| 2,000 | sorted | 5.2864 | 5.4297 | 3.8409 |
| 2,000 | reverse | 4.5149 | 4.5452 | 3.7453 |
| 2,000 | repeated | 4.0666 | 0.7694 | 4.2367 |
| 8,000 | random | 22.4519 | 22.2535 | 19.8465 |
| 8,000 | sorted | 22.4158 | 20.5158 | 17.2423 |
| 8,000 | reverse | 22.6710 | 22.2396 | 17.9303 |
| 8,000 | repeated | 19.1343 | 2.3677 | 19.1283 |

At 8,000 distinct random items, Heapsort took 22.4519 ms, randomized Quicksort
22.2535 ms, and Merge Sort 19.8465 ms. Merge Sort was fastest on the three
distinct-key distributions at that size. Heapsort remained near 22 ms across
random, sorted, and reversed data, consistent with its robust bound and lack
of a bad-pivot pattern. Its constant-space behavior can still be valuable even
when it is not the fastest Python implementation.

Increasing random input size fourfold from 2,000 to 8,000 raised Heapsort time
about 4.53 times, Quicksort about 4.48 times, and Merge Sort about 4.82 times.
The n log2 n model predicts about 4.73 times, broadly compatible with these
measurements. This finite experiment illustrates growth rather than proving
an asymptotic bound.

On eight-value repeated data at 8,000 items, Quicksort took 2.3677 ms versus
19.1343 ms for Heapsort and 19.1283 ms for Merge Sort. Grouping equal values
removes large groups in one partition, explaining the Quicksort advantage.
This distribution is not all-equal, so it does not demonstrate Heapsort's
linear all-equal special case. Its lower time than unique inputs is consistent
with some early sift exits.

Interpreter overhead, allocation, function calls, cache behavior, scheduling,
and sampled partition shapes affect observed constants. Five trials, small
educational implementations, and one computer do not establish a universal
ranking or confidence intervals. These results are not a comparison against
optimized production library sorts.

## 4 Indexed max-priority queue

`Task` is an immutable dataclass containing task ID, integer priority, arrival
time, positive duration, and an optional deadline. Immutable values prevent a
caller from silently invalidating heap order. Task IDs are unique while queued.
Invalid fields and duplicate inserts are rejected, and an absent ID raises
KeyError on update. Extracting from an empty queue raises IndexError.

A list represents a binary max-heap. Higher numeric priority runs first;
equal priorities use earlier arrival, then original insertion sequence.
The queue stores task/sequence pairs and an ID-to-index dictionary. Every
swap updates both dictionary entries, preserving the position invariant.
Without that dictionary, finding a task to change its priority would require
O(n) scanning, obscuring the benefit of logarithmic heap repair.

Insert appends a leaf and sifts upward. Extract-max removes the root, moves
the last leaf to index zero, and sifts downward. Increasing a priority can
only violate order above the task; decreasing can only violate order below
it. Both directional methods delegate to `change_priority`, which replaces
the immutable task and repairs in the necessary direction. Equal updates
require no heap movement. `is_empty` checks list length; `peek_max` reads
the root without removing it.

### Table 2 Operation complexity

| Operation | Heap work | Reason |
|---|---|---|
| insert(task) | O(log n) worst-case sift | At most one leaf-to-root path |
| extract_max() | O(log n) worst-case sift | At most one root-to-leaf path |
| increase_key(id, priority) | O(log n) worst-case sift | Index lookup, then sift upward |
| decrease_key(id, priority) | O(log n) worst-case sift | Index lookup, then sift downward |
| change_priority(id, priority) | O(log n) worst-case sift | Chooses one direction |
| peek_max(), is_empty(), len() | O(1) | Root or length access |

These are heap-structure bounds under O(1) index-map operations. In actual
Python, list append/pop and dictionary storage have amortized/expected
qualifications: an occasional allocation or rehash can cost O(n), and
dictionary worst-case lookup is not guaranteed constant. Thus the concrete
implementation's updates are expected amortized O(log n), while the sift
itself has O(log n) worst-case levels. Lists and the index map use O(n)
space; iterative repair uses O(1) temporary space. This distinction avoids
claiming hard real-time bounds for a Python container implementation.

## 5 Scheduler simulation and applications

The simulator models one CPU, integer time, known task arrivals, fixed
priorities, and nonpreemptive execution. Only tasks with arrival <= current
time enter the ready queue. Once dispatched, a task runs to completion.
If the ready queue is empty, time jumps to the next arrival, representing
idle time. Deadlines are recorded for evaluation; they do not determine
priority and are not enforced. Context-switch costs, I/O blocking, and
priority-update events during a running task are outside this model; key
updates are separately implemented and tested by the queue API.

An FCFS baseline uses the same tasks and durations. Arrival, duration,
deadline, waiting, turnaround, and tardiness are expressed in abstract
simulation time units, not the milliseconds used in the sorting benchmark.
Priorities are dimensionless integer ranks. The task set is:

| Task | Priority | Arrival | Duration | Deadline |
|---|---:|---:|---:|---:|
| A | 2 | 0 | 4 | 5 |
| B | 9 | 1 | 1 | 3 |
| C | 3 | 1 | 3 | 10 |
| D | 8 | 2 | 2 | 6 |
| E | 1 | 12 | 1 | 14 |

Priority execution is A [0,4), B [4,5), D [5,7), C [7,10), idle [10,12),
E [12,13). FCFS is A [0,4), B [4,5), C [5,8), D [8,10), then the same idle
interval and E. In both policies B waits for low-priority A because execution
is nonpreemptive. D overtakes C only in the priority policy.

Waiting = start - arrival. Turnaround = finish - arrival. Tardiness is
max(0, finish - deadline); finishing exactly at a deadline is on time.
Utilization is busy time divided by elapsed time from first arrival to last
completion, including internal idle periods but excluding time before the
first arrival. Empty input has zero metrics.

### Table 3 Simulated scheduling results

| Metric | Priority | FCFS |
|---|---:|---:|
| Mean waiting | 2.4 | 2.6 |
| Mean turnaround | 4.6 | 4.8 |
| Deadline misses | 2 | 2 |
| Total tardiness | 3 | 6 |
| Busy time | 11 | 11 |
| Elapsed time | 13 | 13 |
| Utilization | 84.62% | 84.62% |

Waiting, turnaround, tardiness, busy time, and elapsed time use simulation
time units; deadline misses are counts and utilization is a percentage.

On this task set, priority scheduling halves total tardiness but does not
reduce the number of missed deadlines. B finishes at 5 after deadline 3 in
both policies. D finishes at 7 rather than 10, reducing its tardiness from
4 to 1. The modest waiting-time improvement is specific to this workload,
not a general optimality guarantee. Reordering cannot remove the two idle
time units before E, so utilization is unchanged.

A sustained stream of high-priority arrivals can starve low-priority tasks.
Aging could periodically increase waiting tasks' priorities through the
provided API; that strategy is discussed, not simulated here. Deadline-aware
or preemptive policies would address different objectives, but even they
need feasibility analysis before guaranteeing deadlines. A heap organizes
ready tasks efficiently; it does not by itself make a scheduling policy fair
or optimal. Potential applications include bounded worker queues and
discrete-event dispatch, with policy chosen for the application's objective.

Sorting arrivals costs O(t log t) for t tasks. Each task is inserted and
extracted once, costing O(t log t) heap work overall with O(t) storage.
The event-driven clock jumps rather than iterating every time unit, so runtime
does not scale with the numeric magnitude of arrival times or durations.

## 6 Verification and conclusion

Seven tests cover sorting edge cases, 100 generated arrays, the max-heap
property after construction, and 1,000 randomized queue operations checked
against a reference model. Queue tests verify the index map and heap order
after every operation, both priority-change directions, stable ties,
immutability, duplicate IDs, and empty errors. Scheduler tests check exact
dispatch order, intervals, metrics, idle periods, empty input, and invalid
policies. Every timed sort is also validated independently.

Heapsort offers an O(n log n) upper bound on all inputs with constant auxiliary
space. The indexed binary heap supports efficient ready-queue updates and
selection. The empirical results show that constant factors and duplicates
affect sorting performance, while the scheduler shows that efficient data
structures and good scheduling outcomes are separate concerns.

## References

Demaine, E., Ku, J., & Solomon, J. (2020). *Lecture 8: Binary heaps* [Course notes].
MIT OpenCourseWare.
https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/40d4851e550507ca14dc778b9b2266cc_MIT6_006S20_lec8.pdf

Sedgewick, R., & Wayne, K. (n.d.). *Algorithms and data structures cheatsheet*.
Princeton University. https://algs4.cs.princeton.edu/cheatsheet/
