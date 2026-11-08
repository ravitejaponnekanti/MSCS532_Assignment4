"""Single-CPU nonpreemptive fixed-priority scheduling simulation."""
import csv
import json
from collections import deque
from pathlib import Path
from priority_queue import Task, MaxPriorityQueue


def simulate(tasks, policy='priority'):
    """Dispatch only arrived tasks. Deadlines are measured, not enforced.

    Equal priority uses earlier arrival, then original input order.
    policy='fcfs' is a comparison baseline. No context-switch overhead.
    """
    if policy not in ('priority', 'fcfs'):
        raise ValueError('policy must be priority or fcfs')
    tasks = list(tasks)
    if len({t.task_id for t in tasks}) != len(tasks):
        raise ValueError('task IDs must be unique')
    arrivals = sorted(enumerate(tasks), key=lambda pair: (pair[1].arrival_time, pair[0]))
    queue, fifo = MaxPriorityQueue(), deque()
    index = now = 0
    records = []
    while index < len(arrivals) or not queue.is_empty() or fifo:
        if queue.is_empty() and not fifo and index < len(arrivals):
            now = max(now, arrivals[index][1].arrival_time)
        while index < len(arrivals) and arrivals[index][1].arrival_time <= now:
            task = arrivals[index][1]
            if policy == 'priority': queue.insert(task)
            else: fifo.append(task)
            index += 1
        task = queue.extract_max() if policy == 'priority' else fifo.popleft()
        finish = now + task.duration
        records.append(dict(task_id=task.task_id, priority=task.priority,
                            arrival=task.arrival_time, duration=task.duration,
                            deadline=task.deadline, start=now, finish=finish,
                            waiting=now-task.arrival_time,
                            turnaround=finish-task.arrival_time,
                            tardiness=max(0, finish-task.deadline) if task.deadline is not None else 0,
                            missed_deadline=task.deadline is not None and finish > task.deadline))
        now = finish
    count = len(records)
    busy = sum(t.duration for t in tasks)
    span = now - min((t.arrival_time for t in tasks), default=0)
    summary = dict(policy=policy, tasks=count,
                   mean_waiting=sum(r['waiting'] for r in records)/count if count else 0,
                   mean_turnaround=sum(r['turnaround'] for r in records)/count if count else 0,
                   missed_deadlines=sum(r['missed_deadline'] for r in records),
                   total_tardiness=sum(r['tardiness'] for r in records),
                   busy_time=busy, elapsed_time=span,
                   utilization=busy/span if span else 0)
    return records, summary


def example_tasks():
    return [Task('A', 2, 0, 4, 5), Task('B', 9, 1, 1, 3),
            Task('C', 3, 1, 3, 10), Task('D', 8, 2, 2, 6),
            Task('E', 1, 12, 1, 14)]


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    summaries = []
    for policy in ('priority', 'fcfs'):
        records, summary = simulate(example_tasks(), policy)
        summaries.append(summary)
        print(policy, records, summary, sep='\n')
        with (root/('schedule_' + policy + '.csv')).open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)
    (root/'scheduler_summary.json').write_text(json.dumps(summaries, indent=2), encoding='utf-8')
