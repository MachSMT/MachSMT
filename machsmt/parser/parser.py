import argparse,multiprocessing

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--data-files",
                metavar="files[,files...]",
                action="store",
                dest="files",
                default=None,
                nargs='+',
                help="Input Data files containing solver, benchmark, runtime pairs"
)

parser.add_argument("-l", "--lib-directory",
            metavar="lib",
            action="store",
            dest="lib",
            default=None,
            type=str,
            help="Library directory, save state for machsmt"
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

parser.add_argument("-min", "--min-datapoints",
            metavar="min_dp",
            action="store",
            dest="min_dp",
            default=25,
            type=int,
            help="Minimum number of datapoints needed to build MachSMT.",
)

parser.add_argument("-c", "--num_cpus",
            metavar="cores",
            action="store",
            dest="cores",
            default=5,
            type=int,
            help="Number of CPUs to run in parallel."
)

parser.add_argument("-pca", "--pca-diminsions",
            metavar="pca",
            action="store",
            dest="pca",
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

parser.add_argument("--semantic-features",
            metavar="semantic_features",
            action="store",
            dest="semantic_features",
            default=True,
            type=bool,
            help="Run with semantic features"
)

parser.add_argument("-debug",
            metavar="debug",
            action="store",
            dest="debug",
            default=True,
            type=bool,
            help="Run in debug mode"
)

parser.add_argument("-wall",
            metavar="wall",
            action="store",
            dest="wall",
            default=False,
            type=bool,
            help="Exit on warning"
)

parser.add_argument("-t", "--timeout",
            metavar="timeout",
            action="store",
            dest="timeout",
            default=2400,
            type=int,
            help="Number of CPUs to run in parallel."
)

parser.add_argument("--feature-timeout",
            metavar="feature_timeout",
            action="store",
            dest="feature_timeout",
            default=10,
            type=int,
            help="Number of CPUs to run in parallel."
)

args = parser.parse_args()