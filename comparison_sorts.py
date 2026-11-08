"""Educational comparison sorts; independent of other assignment folders."""
import random


def randomized_quicksort(values, seed=532):
    """Three-way randomized quicksort; smaller side processed first."""
    rng = random.Random(seed)
    stack = [(0, len(values) - 1)] if len(values) > 1 else []
    while stack:
        low, high = stack.pop()
        pivot = values[rng.randrange(low, high + 1)]
        left = index = low
        right = high
        while index <= right:
            if values[index] < pivot:
                values[left], values[index] = values[index], values[left]
                left += 1; index += 1
            elif values[index] > pivot:
                values[index], values[right] = values[right], values[index]
                right -= 1
            else:
                index += 1
        a, b = (low, left - 1), (right + 1, high)
        if a[1] - a[0] < b[1] - b[0]:
            a, b = b, a
        stack.extend((start, end) for start, end in (a, b) if start < end)
    return values


def merge_sort(values):
    """Stable top-down merge sort with O(n) auxiliary storage."""
    buffer = [None] * len(values)
    def sort(low, high):
        if high - low <= 1:
            return
        middle = (low + high) // 2
        sort(low, middle); sort(middle, high)
        left, right = low, middle
        for destination in range(low, high):
            if left < middle and (right >= high or values[left] <= values[right]):
                buffer[destination] = values[left]; left += 1
            else:
                buffer[destination] = values[right]; right += 1
        for index in range(low, high):
            values[index] = buffer[index]
    sort(0, len(values))
    return values
