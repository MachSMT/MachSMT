import argparse
import os


class Config:
    def __init__(self, args) -> None:
        for arg in dir(args):
            if arg[:2] != '__':
                self.__setattr__(arg, args.__getattribute__(arg))
        self.check()

    def check(self):
        pass


parser = argparse.ArgumentParser()

parser.add_argument("benchmarks",
                    action="store",
                    # dest="input_benchmark",
                    default=[],
                    nargs='?',
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

parser.add_argument("-o", "--output",
                    metavar="lib",
                    action="store",
                    dest="lib",
                    default=f'{os.getcwd()}/main.machsmt',
                    type=str,
                    help="Output datafile"
                    )

parser.add_argument("-r", "--results-directory",
                    metavar="results",
                    action="store",
                    dest="results",
                    default="results",
                    type=str,
                    help="Results directory, save results of machsmt"
                    )

parser.add_argument("-k", "--k-fold-value",
                    metavar="k",
                    action="store",
                    dest="k",
                    default=5,
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

parser.add_argument("-pca", "--pca-diminsions",
                    metavar="pca",
                    action="store",
                    dest="pca",
                    default=35,
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
                    help="Run with Greedy Selection"
                    )

parser.add_argument("-pwc", "--pairwise-comparator",
                    metavar="pwc",
                    action="store",
                    dest="pwc",
                    default=False,
                    type=bool,
                    help="Run with PWC Selection"
                    )

parser.add_argument("--feature-timeout",
                    metavar="feature_timeout",
                    action="store",
                    dest="feature_timeout",
                    default=10,
                    type=int,
                    help="Number of CPUs to run in parallel."
                    )
CONFIG_OBJ = Config(parser.parse_args())
