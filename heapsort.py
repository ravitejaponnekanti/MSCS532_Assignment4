"""Array-based, in-place ascending Heapsort; no heapq or built-in sort."""


def sift_down(values, root, size):
    """Restore a max-heap below root; size is the exclusive heap boundary."""
    while 2 * root + 1 < size:
        child = 2 * root + 1
        if child + 1 < size and values[child] < values[child + 1]:
            child += 1
        if not values[root] < values[child]:
            break
        values[root], values[child] = values[child], values[root]
        root = child


def build_max_heap(values):
    """Bottom-up heap construction in O(n) time and O(1) extra space."""
    for root in range(len(values) // 2 - 1, -1, -1):
        sift_down(values, root, len(values))
    return values


def heapsort(values):
    """Sort and return the same list. O(n log n) time, O(1) auxiliary space.

    Equal keys can stop sifting early; all-equal input takes Theta(n) time.
    The algorithm is not stable.
    """
    build_max_heap(values)
    for end in range(len(values) - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        sift_down(values, 0, end)
    return values


if __name__ == '__main__':
    while True:
        try:
            numbers = [int(x) for x in input('Enter integers separated by spaces: ').split()]
            break
        except ValueError:
            print('Please enter integers only.')
    print('Sorted:', heapsort(numbers))
