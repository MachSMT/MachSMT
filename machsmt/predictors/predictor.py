from ..db import database as db
from ..util import MachSMTException
class Predictor:
    def __init__(self):
        if len(db) == 0: raise MachSMTException("Empty Database.")
    def eval(self,benchmarks):
        raise NotImplementedError
    def build(self,benchmarks):
        raise NotImplementedError
    def predict(self,benchmarks):
        raise NotImplementedError