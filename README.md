# MachSMT -- An ML-Driven Algorithm Selection Tool for SMT Solvers

This is the main repository for MachSMT.

## Authors
  * [Joseph Scott](https://www.joe-scott.net/)
  * [Aina Niemetz](https://cs.stanford.edu/~niemetz/)
  * [Mathias Preiner](https://cs.stanford.edu/~preiner/)
  * [Saeed Nejati](https://saeednj.github.io/)
  * [Vijay Ganesh](https://ece.uwaterloo.ca/~vganesh/)


## Publications

For all publications related to this project see [this file](https://github.com/MachSMT/MachSMT/blob/main/machsmt.bib).

For primary citation, please use the STTT Journal versional of the paper.

```
@article{DBLP:journals/sttt/ScottNPNG23,
  author       = {Joseph Scott and
                  Aina Niemetz and
                  Mathias Preiner and
                  Saeed Nejati and
                  Vijay Ganesh},
  title        = {Algorithm selection for {SMT}},
  journal      = {Int. J. Softw. Tools Technol. Transf.},
  volume       = {25},
  number       = {2},
  pages        = {219--239},
  year         = {2023},
  url          = {https://doi.org/10.1007/s10009-023-00696-0},
  doi          = {10.1007/s10009-023-00696-0},
  timestamp    = {Sun, 16 Apr 2023 20:30:55 +0200},
  biburl       = {https://dblp.org/rec/journals/sttt/ScottNPNG23.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```

## Recorded Talk

[![Recorded Talk at SMT 2020](https://img.youtube.com/vi/OfZaIUXltf4/0.jpg)](https://www.youtube.com/watch?v=OfZaIUXltf4&t=5795s)

## Installation

### From PIP

`pip install machsmt==1.0`

### From Source

Prerequisites
* Ubuntu 18.0+
* python 3.7+
* make

Please then clone this repository, and run `make` in a clean virtual environment or ubuntu machine.

For development mode, plz use `make dev`.

## Usage

Upon successful installation, the commandline interface `machsmt`will be available. 

The first argument to `machsmt` is the mode, where the `mode` is one of:  `build`, `train`, `eval`, or `predict`, with default mode of `predict`.

For a full example, please see `demo.sh`.

### Build

The `build` mode of machsmt populates its internal database. In this phase, a data file needs to be provided.

The data file can be provided with either the `-f` or the `--data-files` flag.

For example, `machsmt build -f a.csv b.csv c.csv`

All datafiles are required to specify the following 3 columns `benchmark`, `solver`, and `score`. The benchmark field provides the path to the `.smt2`file, the `solver` is the name of the solver, and `score` is the scoring function that MachSMT aims to minimize.

When building the entire SMT-LIB, this process could take several hours. On large jobs, please consider using the `-j` or `--num_cpus` to specify the number of jobs (default, `os.cpu_count()`).

Additional columns of intrested can be made explicit to MachSMT with the `--bonus-col` flag. These will be then be automatically  used in the supervised learning. 

The output of this phase is a pickled save state. This can be specified with `-l`, `-o`, or `--output` (default `main.machsmt`)

### Train

This mode builds the main production model for `machsmt` (not evaluated).

This phase presuposes the building of the internal database. This phase will load the pickled save state. To tell MachSMT where to find it, use the `-l`, `-o`, or `--output` flags.

MachSMT is ML framework agnostic, with head-start code for scikit learn, xgboost, and pytorch. MachSMT can be trained with GPUs (`--use-gpu`). To our support for thesse three frameworks out of box, please use the `--ml-core` flag to specify (`scikit`, `xgboost`, `torch`).

For higher fidelity control over the model construction and training, please insert code in MachSMT's [model_maker.py](https://github.com/MachSMT/MachSMT/blob/main/machsmt/ml/model_maker.py). Note that regression is used for EHMs while classifiers are used for PWC. For large and hard to train models, it is strongly reccomended to only use EHMs. This version of MachSMT trains a single model for the entire provided dataset for better GPU support. Please see older versions if this is not desired. This phase does not use k-fold, and only trains a single model.

We reccomend using empirical hardness models, which are enabled and the primary method by default. If you wish to enable greedy or pairwise comparators, please see use `-greedy` and `-pwc`.

### Eval

This mode builds lots of machine learned models under k-fold cross-validation to determine how well the tool is performing. 

This phase presuposes the building of the internal database. This phase will load the pickled save state. To tell MachSMT where to find it, use the `-l`, `-o`, or `--output` flags.

This script implements a k-fold evaluation. To specify the k value, please use the `-k` flag. 

This mode will create a results directory. To specify the location, please use `-results`. In this directory, a subdirectory will appear for every logic. Within each subdirectory, the cactus, CDF, and par2 tables of all solvers and MachSMT will be presented.

### Predict

This is the main prediction interface to machsmt. This is the default mode of machsmt.

This phase presuposes the building of the internal database. This phase will load the pickled save state. To tell MachSMT where to find it, use the `-l`, `-o`, or `--output` flags.

Example Usage:
`machsmt test.smt2`

## Archived Versions

Please see links to the various versions of this tool over time. Specifically for certain publications

* [TACAS Artifact](https://github.com/MachSMT/TACAS-Artifact)
* [STTT Artifact](https://github.com/MachSMT/STTT-Artifact) 
