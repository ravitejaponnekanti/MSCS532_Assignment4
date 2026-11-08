import random
import unittest
from dataclasses import FrozenInstanceError
from heapsort import heapsort, build_max_heap
from comparison_sorts import randomized_quicksort, merge_sort
from priority_queue import Task, MaxPriorityQueue
from scheduler import simulate, example_tasks


class SortTests(unittest.TestCase):
    def test_edge_cases(self):
        for values in ([], [1], [3, -2, 3, 0], [7]*100, list(range(200)), list(range(199, -1, -1))):
            for algorithm in (heapsort, randomized_quicksort, merge_sort):
                data = values.copy()
                with self.subTest(algorithm=algorithm.__name__, size=len(data)):
                    self.assertIs(algorithm(data), data)
                    self.assertEqual(data, sorted(values))

    def test_random_and_heap_property(self):
        rng = random.Random(532)
        for n in range(100):
            values = [rng.randrange(-100, 101) for _ in range(n)]
            heap = build_max_heap(values.copy())
            for i in range(1, n): self.assertGreaterEqual(heap[(i-1)//2], heap[i])
            for algorithm in (heapsort, randomized_quicksort, merge_sort):
                self.assertEqual(algorithm(values.copy()), sorted(values))


class QueueTests(unittest.TestCase):
    def check_invariants(self, queue):
        self.assertEqual(len(queue._position), len(queue))
        for i, (task, _) in enumerate(queue._heap):
            self.assertEqual(queue._position[task.task_id], i)
            if i: self.assertGreaterEqual(queue._rank((i-1)//2), queue._rank(i))

    def test_ties_and_priority_updates(self):
        q = MaxPriorityQueue()
        for t in (Task('A',2), Task('B',5), Task('C',5)): q.insert(t)
        q.increase_key('A',10)
        self.assertEqual(q.peek_max().task_id,'A')
        q.decrease_key('A',1)
        self.check_invariants(q)
        self.assertEqual([q.extract_max().task_id for _ in range(3)], ['B','C','A'])
        self.assertTrue(q.is_empty())

    def test_random_operations_against_reference(self):
        rng = random.Random(532); q = MaxPriorityQueue(); reference = {}; sequence = 0
        for _ in range(1000):
            choice = rng.randrange(3)
            if choice == 0 or not reference:
                task = Task(str(sequence),rng.randrange(-10,11),rng.randrange(10))
                q.insert(task); reference[task.task_id] = (task, sequence); sequence += 1
            elif choice == 1:
                key = rng.choice(list(reference)); priority = rng.randrange(-10,11)
                old, seq = reference[key]
                q.change_priority(key,priority)
                reference[key] = (Task(key,priority,old.arrival_time),seq)
            else:
                expected = max(reference.values(),key=lambda item:(item[0].priority,-item[0].arrival_time,-item[1]))[0]
                self.assertEqual(q.extract_max(),expected); del reference[expected.task_id]
            self.check_invariants(q)
            self.assertEqual(len(q),len(reference))

    def test_errors_and_immutable_tasks(self):
        q=MaxPriorityQueue()
        with self.assertRaises(IndexError): q.extract_max()
        with self.assertRaises(KeyError): q.change_priority('missing',3)
        t=Task('A',3); q.insert(t)
        with self.assertRaises(FrozenInstanceError): t.priority=5
        with self.assertRaises(ValueError): q.insert(t)
        with self.assertRaises(ValueError): q.increase_key('A',2)
        with self.assertRaises(ValueError): q.decrease_key('A',4)
        with self.assertRaises(ValueError): q.change_priority('A',float('nan'))
        with self.assertRaises(ValueError): Task('bad',1,duration=0)
        with self.assertRaises(ValueError): Task('bad',1,arrival_time=-1)


class SchedulerTests(unittest.TestCase):
    def test_expected_schedule_and_metrics(self):
        rows, summary=simulate(example_tasks())
        self.assertEqual([r['task_id'] for r in rows],['A','B','D','C','E'])
        self.assertEqual([(r['start'],r['finish']) for r in rows],[(0,4),(4,5),(5,7),(7,10),(12,13)])
        self.assertEqual(summary['mean_waiting'],2.4)
        self.assertEqual(summary['missed_deadlines'],2)
        self.assertEqual(summary['total_tardiness'],3)
        self.assertAlmostEqual(summary['utilization'],11/13)
        fcfs, other=simulate(example_tasks(),'fcfs')
        self.assertEqual([r['task_id'] for r in fcfs],['A','B','C','D','E'])
        self.assertEqual(other['total_tardiness'],6)

    def test_empty_idle_ties_and_invalid(self):
        rows, summary=simulate([])
        self.assertEqual(rows,[]); self.assertEqual(summary['utilization'],0)
        rows, summary=simulate([Task('late',1,5,2,7)])
        self.assertEqual(rows[0]['start'],5); self.assertEqual(summary['elapsed_time'],2)
        rows, _=simulate([Task('A',1),Task('B',1)])
        self.assertEqual([r['task_id'] for r in rows],['A','B'])
        with self.assertRaises(ValueError): simulate([Task('A',1),Task('A',2)])
        with self.assertRaises(ValueError): simulate([],'invalid')


if __name__=='__main__': unittest.main()
