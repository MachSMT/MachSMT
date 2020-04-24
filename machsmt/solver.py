from machsmt.benchmark import Benchmark

class Solver:
    def __init__(self, name:str):
        self.name = name
        self.benchmarks = []
        self.score = []
    def add_benchmark(self,benchmark:Benchmark, score: float): 
        self.benchmarks.append(benchmark)