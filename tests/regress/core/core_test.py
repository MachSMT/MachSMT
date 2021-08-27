import unittest
from .db.db_test import *
from .benchmark.benchmark_test import *
from .ml.ml_test import *
from .features.features_test import *
from .util.util_test import *
from .smtlib.smtlib_test import *
from .solver.solver_test import *
from .selectors.selector_test import *
from .machsmt_test import *
from .parser.parser_test import *
if __name__ == '__main__':
    unittest.main()
