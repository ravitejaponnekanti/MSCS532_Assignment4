# MSCS532 Assignment 4

Heap Data Structures Implementation Analysis and Applications

Python implementations of in-place Heapsort, an indexed max-priority queue,
and a nonpreemptive task scheduler, with sorting benchmarks and analysis.

## Requirements

Python 3.8 or later. Standard library only; no additional packages required.

## Run

From this folder in a terminal:

```powershell
python heapsort.py
python scheduler.py
python -m unittest -v
python benchmark.py
```

Heapsort prompts for space-separated integers. Empty input is supported.
For the local environment, replace `python` with `.\.venv\Scripts\python.exe`.
Use **Run Python File in Terminal** in VS Code for keyboard input.

## Priority queue example

```python
from priority_queue import Task, MaxPriorityQueue

queue = MaxPriorityQueue()
queue.insert(Task("A", priority=2, duration=4))
queue.insert(Task("B", priority=5, duration=1))
queue.increase_key("A", 8)
assert queue.extract_max().task_id == "A"
queue.decrease_key("B", 1)
assert not queue.is_empty()
```

Higher numeric priority wins. Equal priorities use earlier arrival, then
insertion order. Task objects are immutable. Duplicate IDs and invalid fields
are rejected. Missing updates raise `KeyError`; empty extraction raises
`IndexError`. Update methods accept a task ID and an integer new priority.

## Results and report

See [REPORT.md](REPORT.md) for the detailed design, correctness arguments,
best/average/worst sorting analysis, queue-operation costs, measured comparison,
scheduling results, limitations, and references.

At 8,000 random elements, median times were 22.4519 ms for Heapsort,
22.2535 ms for randomized Quicksort, and 19.8465 ms for Merge Sort. These
measurements are specific to this machine and implementation. Heapsort has
constant auxiliary space and O(n log n) time in every case; its tight best
case is linear when all keys are equal and sifting stops early.

The sample priority schedule reduces total tardiness from 6 to 3 compared
with FCFS. Both miss two deadlines and have 84.62% utilization. This is
nonpreemptive fixed-priority scheduling, not a deadline-guaranteed policy.

## Files

- `heapsort.py`: max-heap construction and in-place sorting.
- `priority_queue.py`: Task and indexed binary max-heap.
- `scheduler.py`: priority/FCFS simulations and CSV/JSON outputs.
- `comparison_sorts.py`: randomized Quicksort and stable Merge Sort.
- `benchmark.py`: five timing trials on sizes 500, 2,000, and 8,000 across
  random, sorted, reversed, and repeated inputs.
- `test_algorithms.py`: seven automated correctness and invariant tests.
- `benchmark_results.csv`, `environment.json`: 36 aggregate timing cases
  and environment details.
- `schedule_priority.csv`, `schedule_fcfs.csv`, `scheduler_summary.json`:
  reproducible sample scheduling results.
- `REPORT.md`: written report for submission.

Rerunning the scripts replaces their result files. Update report tables if
benchmark measurements change.

## Repository and submission

https://github.com/ravitejaponnekanti/MSCS532_Assignment4

Commit and push the code, report, README, and result files before submitting
the repository link through the course portal.
