from ..db import database as db
from .predictor import Predictor

class Oracle(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self,benchmarks):
        predictions = {}
        for benchmark in benchmarks:
            predictions[benchmark] = {}
            for solver in db.get_solvers(benchmark):
                predictions[benchmark][solver] = db[benchmark,solver] 
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError