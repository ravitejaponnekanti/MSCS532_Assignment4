"""Indexed binary max-heap for immutable tasks with stable priority ties."""
from dataclasses import dataclass, replace
from typing import Optional


@dataclass(frozen=True)
class Task:
    task_id: str
    priority: int
    arrival_time: int = 0
    duration: int = 1
    deadline: Optional[int] = None

    def __post_init__(self):
        if not isinstance(self.task_id, str) or not self.task_id:
            raise ValueError('task_id must be a nonempty string')
        for name in ('priority', 'arrival_time', 'duration'):
            if type(getattr(self, name)) is not int:
                raise ValueError(name + ' must be an integer')
        if self.arrival_time < 0 or self.duration <= 0:
            raise ValueError('arrival_time must be nonnegative and duration positive')
        if self.deadline is not None and (type(self.deadline) is not int or self.deadline < self.arrival_time):
            raise ValueError('deadline must be an integer at or after arrival')


class MaxPriorityQueue:
    """Higher numeric priority first; ties use arrival, then insertion order.

    An ID-to-index dictionary avoids linear lookup during priority updates.
    Immutable Task objects prevent silent external priority changes.
    """
    def __init__(self):
        self._heap = []  # (Task, insertion sequence)
        self._position = {}
        self._sequence = 0

    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        return not self._heap

    def _rank(self, index):
        task, sequence = self._heap[index]
        return task.priority, -task.arrival_time, -sequence

    def _swap(self, i, j):
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._position[self._heap[i][0].task_id] = i
        self._position[self._heap[j][0].task_id] = j

    def _up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self._rank(parent) >= self._rank(index):
                break
            self._swap(index, parent)
            index = parent

    def _down(self, index):
        size = len(self._heap)
        while 2 * index + 1 < size:
            child = 2 * index + 1
            if child + 1 < size and self._rank(child + 1) > self._rank(child):
                child += 1
            if self._rank(index) >= self._rank(child):
                break
            self._swap(index, child)
            index = child

    def insert(self, task):
        if not isinstance(task, Task):
            raise TypeError('insert expects a Task')
        if task.task_id in self._position:
            raise ValueError('duplicate task ID: ' + task.task_id)
        self._position[task.task_id] = len(self._heap)
        self._heap.append((task, self._sequence))
        self._sequence += 1
        self._up(len(self._heap) - 1)

    def peek_max(self):
        if self.is_empty():
            raise IndexError('priority queue is empty')
        return self._heap[0][0]

    def extract_max(self):
        task = self.peek_max()
        last = self._heap.pop()
        del self._position[task.task_id]
        if self._heap:
            self._heap[0] = last
            self._position[last[0].task_id] = 0
            self._down(0)
        return task

    def change_priority(self, task_id, new_priority):
        if type(new_priority) is not int:
            raise ValueError('priority must be an integer')
        index = self._position[task_id]  # KeyError for absent task.
        task, sequence = self._heap[index]
        self._heap[index] = (replace(task, priority=new_priority), sequence)
        if new_priority > task.priority:
            self._up(index)
        elif new_priority < task.priority:
            self._down(index)

    def increase_key(self, task_id, new_priority):
        if type(new_priority) is not int:
            raise ValueError('priority must be an integer')
        if new_priority < self._heap[self._position[task_id]][0].priority:
            raise ValueError('increase_key cannot lower a priority')
        self.change_priority(task_id, new_priority)

    def decrease_key(self, task_id, new_priority):
        if type(new_priority) is not int:
            raise ValueError('priority must be an integer')
        if new_priority > self._heap[self._position[task_id]][0].priority:
            raise ValueError('decrease_key cannot raise a priority')
        self.change_priority(task_id, new_priority)
