from ..db import database as db
from .predictor import Predictor

class Oracle(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self):
        predictions = {}
        for benchmark in db.get_benchmarks():
            predictions[benchmark] = {}
            for solver in db.get_solvers(benchmark=benchmark):
                predictions[benchmark][solver] = db[benchmark,solver] 
        return predictions