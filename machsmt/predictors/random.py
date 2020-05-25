from ..db import database as db
from .predictor import Predictor
from ..parser import args as settings
import random
class Random(Predictor):
    def __init__(self,*args,**kwargs):
         super().__init__(*args,**kwargs)

    def eval(self,benchmarks):
        predictions = {}
        for benchmark in benchmarks:
            predictions[benchmark] = {}
            for solver in db.get_solvers(benchmark):
                predictions[benchmark][solver] = settings.timeout * random.random()
        return predictions

    def build(self,benchmarks):
        raise NotImplementedError

    def predict(self,benchmarks):
        raise NotImplementedError
