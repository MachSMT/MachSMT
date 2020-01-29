#!/usr/bin/env bash

build_all=

usage() {
cat << EOF
usage: $0 [-h|-a]

-h       print this message and exit
-a       build models and generate data for BV, QF_NRA, QF_UFBV, and UFNIA

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

# 1) Build and evaluate learned models.
#
# The build process creates the results directory, which contains cactus plots,
# par2 scores, and a log file of features and each solver selections.
# Further, it also creates the lib/ folder will be made to save all models. We further provide
# our learned models for all logics and tracks. However, for space, they can't
# be fit into this VM.

echo
echo "Build and evaluate models"
echo "========================="
echo

machsmt_build -logic BV -track smt-comp/2019/results/Single_Query_Track --limit-training

if [ -n "$build_all" ]; then
  machsmt_build -logic QF_UFBV -track smt-comp/2019/results/Single_Query_Track --limit-training
  machsmt_build -logic QF_NRA  -track smt-comp/2019/results/Single_Query_Track --limit-training
  machsmt_build -logic UFNIA   -track smt-comp/2019/results/Unsat_Core_Track   --limit-training
fi


# 2) Demonstration of how to use MachSMT.
#
# Here we make selections over all benchmarks in the SMT-LIB BV benchmark
# database.

num_benchmarks=100
echo
echo "Call machsmt_select on $num_benchmarks random benchmarks"
echo "========================================================"
echo

i=1
for benchmark in $(find benchmarks/BV -name "*.smt2" | shuf | head -n $num_benchmarks)
do
  echo -n "$i/$num_benchmarks Select solver on $benchmark: "
  machsmt_select lib/BV/Single_Query_Track "$benchmark"
  ((i++))
done
