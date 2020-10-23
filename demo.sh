#!/usr/bin/env bash

build_all=
usage() {
cat << EOF
usage: $0 [-h|-a]
-h       print this message and exit
-a       build models and generate data for BV, NRA, QF_UFBV, QF_LIA, and QF_BVFPLRA
By default $0 builds the model and generates the data for BV only.
EOF
  exit 0
}

while [ $# -gt 0 ]
do
  opt=$1
  case $opt in
      -h|--help) usage;;
      -a) build_all=yes;;
 esac
 shift
done

files="smt-comp-data/bv.csv"
if [ -n "$build_all" ]; then
  files="smt-comp-data/bv.csv smt-comp-data/nra.csv smt-comp-data/qf_bvfplra.csv smt-comp-data/qf_lia.csv smt-comp-data/qf_ufbv.csv"
fi


# 1) Build and evaluate learned models.
#
# The build process creates the lib directory which contains 
# final learnt models for machsmt. This process also performs
# all preprocessing steps for evaluation

machsmt_build -f $files -l lib

# 2) Evaluate MachSMT
# This process evaluates machsmt under kfold cross validation
# based the preprocessing of the previous step.

machsmt_eval -l lib


# 3) Example MachSMT Usage
# This process evaluates machsmt under kfold cross validation
# based the preprocessing of the previous step.

i=1
num_benchmarks=10
for benchmark in $(find benchmarks/smt-lib/non-incremental/BV -name "*.smt2" | shuf | head -n $num_benchmarks)
do
  echo -n "$i/$num_benchmarks Select solver on $benchmark: "
  machsmt -l lib "$benchmark"
  ((i++))
done