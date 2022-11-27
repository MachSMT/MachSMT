'''
Solver
'''


from ..benchmark import Benchmark


class Solver:
    def __init__(self, name):
        self.name = name
        self.benchmarks = {}
        self.scores = {}

    def get_name(self): return self.name

    def add_benchmark(self, benchmark, score):
        self.benchmarks[benchmark.get_path()] = benchmark
        self.scores[benchmark.get_path()] = score

    def remove_benchmark(self, benchmark):
        if benchmark.get_path() in self.benchmarks:
            self.benchmarks.pop(benchmark.get_path())
            self.scores.pop(benchmark.get_path())

    def get_benchmarks(self):
        return sorted(self.benchmarks.values(), key=lambda b: b.get_path())

    def get_logics(self):
        ret = set()
        for benchmark in self.benchmarks.values():
            ret.add(benchmark.get_logic())
        return sorted(ret)

    def get_score(self, benchmark):
        return self.scores[benchmark.get_path()]

    def __getitem__(self, key):
        return self.get_score(key)

    def __contains__(self, key):
        return key.get_path() in self.benchmarks
    
    def __lt__(self, other):
        return self.name < other.name

    def __str__(self): return f"Solver(self.name={self.name} len(self.benchmarks)={len(self.benchmarks)})"
    __repr__ = __str__
