from machsmt.benchmark import Benchmark

class Solver:
    def __init__(self, name):
        self.name = name
        self.benchmarks = {}
    def add_benchmark(self, benchmark, score): 
        self.benchmarks[str(benchmark)] = score
    def remove_benchmark(self, benchmark:Benchmark):
        if benchmark in self.benchmarks: self.benchmarks.pop(benchmark)
    def get_benchmarks(self):
        for benchmark in self.benchmarks: yield str(benchmark)

    def get_score(self,benchmark): return self.benchmarks[benchmark]

    def __getitem__(self,key): return self.benchmarks[key]
