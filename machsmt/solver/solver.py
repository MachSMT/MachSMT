from ..benchmark import Benchmark

class Solver:
    def __init__(self, name):
        self.name = name
        self.benchmarks = {}

    def add_benchmark(self, benchmark, score): 
        self.benchmarks[benchmark] = score

    def remove_benchmark(self, benchmark):
        if benchmark in self.benchmarks: self.benchmarks.pop(benchmark)

    def get_score(self,benchmark): return self.benchmarks[benchmark]

    def __getitem__(self,key): return self.get_score(key)

    def __contains__(self, key): return key in self.benchmarks