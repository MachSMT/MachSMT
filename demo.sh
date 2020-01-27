## Build and evaluate learned models

## Following creates a results/ folder that
## contains cactus plots and par2
## scores, plus a log of features
## and each  selection made

## further, a lib/ folder will be made
## to save all models. We further
## provide our learned models for
## all logics and tracks. However,
## for space, they can't be fit into
## this VM

machsmt_build -logic BV       -track smt-comp/2019/results/Single_Query_Track --limit-training
machsmt_build -logic QF_NRA   -track smt-comp/2019/results/Single_Query_Track --limit-training
machsmt_build -logic QF_UFBV  -track smt-comp/2019/results/Single_Query_Track --limit-training
machsmt_build -logic UFNIA    -track smt-comp/2019/results/Unsat_Core_Track   --limit-training


## Demonstration of how to use MachSMT
## Here make selections over all benchmarks
## in the SMT-LIB BV benchmark database

for file in $(find benchmarks/BV -name "*.smt2")
do
  machsmt_select -f $file -l BV -t smt-comp/2019/results/Single_Query_Track
done
