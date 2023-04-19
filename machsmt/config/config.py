import argparse
import os, sys

def implies (A, B): return (not A) or B

class Config:
    def __init__(self, args) -> None:
        for arg in dir(args):
            if arg[:2] != '__':
                self.__setattr__(arg, args.__getattribute__(arg))
        self.check()

    def check(self):
        if hasattr(self, 'mode'):
            if self.mode not in ['build', 'eval', 'predict', 'train']:
                if self.mode.split(".")[-1] == "smt2":
                    self.benchmark = self.mode
                    self.mode = 'predict'
        assert self.ml_core in ['torch', 'scikit', 'xgboost']

    def __str__(self) -> str:
        return str(self.__dict__)

    __repr__ = __str__ 
parser = argparse.ArgumentParser()
bin_file = sys.argv[0].split('/')[-1]

if bin_file in ['machsmt']:
    parser.add_argument("mode",
        action="store",
        default='predict',
        nargs='?',
    )

parser.add_argument("benchmark",
                    action="store",
                    # dest="input_benchmark",
                    nargs='?',
                    default=None,
                    help="Input benchmark to be predicted"
                    )

parser.add_argument("-f", "--data-files",
                    metavar="files[,files...]",
                    action="store",
                    dest="files",
                    default=[],
                    nargs='+',
                    help="Input Data files containing solver, benchmark, runtime pairs"
                    )

parser.add_argument("-l", "-o", "--output",
                    metavar="lib",
                    action="store",
                    dest="lib",
                    default=f'{os.getcwd()}/main.machsmt',
                    type=str,
                    help="Output datafile"
                    )

parser.add_argument("-r", "--results", "--results-directory",
                    metavar="results",
                    action="store",
                    dest="results",
                    default="results",
                    type=str,
                    help="Results directory, save results of machsmt"
                    )

parser.add_argument( "--ml-core",
                    metavar="ml_core",
                    action="store",
                    dest="ml_core",
                    default="scikit",
                    type=str,
                    help="Results directory, save results of machsmt"
                    )

parser.add_argument("--max-score",
                    metavar="max_score",
                    action="store",
                    dest="max_score",
                    default=60,
                    type=int,
                    help="Max Score for Evaluation",
                    )

parser.add_argument("--par-N",
                    metavar="par_n",
                    action="store",
                    dest="par_n",
                    default=2,
                    type=int,
                    help="K Fold Cross Validation parameter",
                    )

parser.add_argument("-k", "--k-fold-value",
                    metavar="k",
                    action="store",
                    dest="k",
                    default=2,
                    type=int,
                    help="K Fold Cross Validation parameter",
                    )

parser.add_argument("-profile",
                    action="store_true",
                    dest="profile",
                    default=False,
                    help="Profile MachSMT"
                    )

parser.add_argument("-c", '-j', "--num_cpus",
                    metavar="cores",
                    action="store",
                    dest="cores",
                    default=os.cpu_count(),
                    type=int,
                    help="Number of CPUs to run in parallel."
                    )

parser.add_argument("-min_datapoints", "--min_datapoints",
                    metavar="min_datapoints",
                    action="store",
                    dest="min_datapoints",
                    default=5,
                    type=int,
                    help="Number of diminsions in PCA",
                    )

parser.add_argument("-rng",
                    metavar="rng",
                    action="store",
                    dest="rng",
                    default=42,
                    type=int,
                    help="Library directory, save state of the database of machsmt"
                    )

parser.add_argument('--no-semantic-features',
                    action='store_false',
                    dest="semantic",
                    help="Disable semantic features"
                    )

parser.add_argument('-d', '-debug', '--debug',
                    action='store_true',
                    dest="debug",
                    default=False,
                    help="Debug mode -- enter PDB on exception"
                    )

parser.add_argument("-wall", "--kill-on-warning",
                    metavar="wall",
                    action="store",
                    dest="wall",
                    default=False,
                    type=bool,
                    help="Kill MachSMT on first warning"
                    )

parser.add_argument("-greedy", "--greedy",
                    metavar="greedy",
                    action="store",
                    dest="greedy",
                    default=True,
                    type=bool,
                    help="Enable greedy selectors when unperformant"
                    )

parser.add_argument("-pwc", "--pairwise-comparator",
                    action='store_true',
                    dest="pwc",
                    default=False,
                    help="Run with PWC Selection"
                    )

parser.add_argument("--feature-timeout",
                    metavar="feature_timeout",
                    action="store",
                    dest="feature_timeout",
                    default=10,
                    type=int,
                    help="Feature timeout"
                    )

parser.add_argument("--logic-filter",
                    action='store_true',
                    dest="logic_filter",
                    help="Run with Logic Filtered Models",
                    default=False,
                    )


parser.add_argument("--use-gpu",
                    action='store_true',
                    dest="use_gpu",
                    help="Use GPU?",
                    default=False,
                    )


CONFIG_OBJ = Config(parser.parse_args())
