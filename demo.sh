#!/usr/bin/env bash

# 1) Build and evaluate learned models.
#
# The build process creates the lib directory which contains 
# final learnt models for machsmt. This process also performs
# all preprocessing steps for evaluation

machsmt_build -f smt-comp-data/smtcomp_2019.csv smt-comp-data/smtcomp_2020.csv -l lib

# 2) Evaluate MachSMT
# This process evaluates machsmt under kfold cross validation
# based the preprocessing of the previous step.

machsmt_eval -l lib

i=1
for benchmark in $(find benchmarks/smt-lib/non-incremental/BV -name "*.smt2" | shuf | head -n $num_benchmarks)
do
  echo -n "$i/$num_benchmarks Select solver on $benchmark: "
  machsmt -l lib "$benchmark"
  ((i++))
done