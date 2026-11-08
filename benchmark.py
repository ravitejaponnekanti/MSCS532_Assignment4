"""Five timing trials on identical inputs for three educational sorts."""
import csv
import json
import platform
import random
import statistics
import time
from pathlib import Path
from heapsort import heapsort
from comparison_sorts import randomized_quicksort, merge_sort

SIZES=(500,2000,8000)
REPEATS=5
SEED=532
ROOT=Path(__file__).resolve().parent


def make_input(n, distribution, trial):
    rng=random.Random(SEED+n+trial)
    if distribution=='sorted': return list(range(n))
    if distribution=='reverse': return list(range(n-1,-1,-1))
    if distribution=='random': return rng.sample(range(n*10),n)
    if distribution=='repeated': return [rng.randrange(8) for _ in range(n)]
    raise ValueError(distribution)


def run():
    algorithms=[heapsort,randomized_quicksort,merge_sort]; rows=[]
    for n in SIZES:
        for distribution in ('random','sorted','reverse','repeated'):
            samples={a.__name__:[] for a in algorithms}
            for trial in range(REPEATS):
                source=make_input(n,distribution,trial); expected=sorted(source)
                # Rotate order to reduce consistent first/last execution bias.
                offset=trial%len(algorithms)
                for algorithm in algorithms[offset:]+algorithms[:offset]:
                    data=source.copy()
                    start=time.perf_counter_ns()
                    if algorithm is randomized_quicksort:
                        algorithm(data,seed=SEED+n+trial)
                    else: algorithm(data)
                    samples[algorithm.__name__].append((time.perf_counter_ns()-start)/1e6)
                    assert data==expected
            for name,measurements in samples.items():
                row=dict(size=n,distribution=distribution,algorithm=name,
                         median_ms=round(statistics.median(measurements),6),
                         min_ms=round(min(measurements),6),max_ms=round(max(measurements),6))
                rows.append(row); print(row,flush=True)
    with (ROOT/'benchmark_results.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (ROOT/'environment.json').write_text(json.dumps(dict(python=platform.python_version(),
        platform=platform.platform(),sizes=SIZES,repeats=REPEATS,seed=SEED,
        note='Median/min/max wall time. Input copying and validation excluded; algorithm allocations and quicksort RNG construction included.'),indent=2),encoding='utf-8')


if __name__=='__main__': run()
