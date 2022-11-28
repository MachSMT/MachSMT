#!/bin/bash

set -e

pushd smt-comp-results/2019
pushd incremental
  tar xf incremental.csv.tar.xz
  mv Incremental_Track.csv incremental.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Incremental Track\///' incremental.csv
  sed -i 's/Competition - Incremental Track - CVC4-fixed\///' incremental.csv
  sed -i 's/Competition - Incremental Track - Best 2018\///' incremental.csv
  sed -i 's/Competition - Incremental Track - all solvers - benchmarks with status unknown\///' incremental.csv

  # Sanitize solver names
  sed -i 's/,Boolector,/,Boolector (2018),/' incremental.csv
  sed -i 's/Boolector incremental-wrapped-inc/Boolector/' incremental.csv
  sed -i 's/Boolector-ReasonLS-wrapped-inc/Boolector-ReasonLS/' incremental.csv
  sed -i 's/,CVC4,/,CVC4 (2018),/' incremental.csv
  sed -i 's/CVC4-inc-2019-06-03-d350fe1-wrapped-inc/CVC4/' incremental.csv
  sed -i 's/CVC4-inc-fixed-2019-06-26-0e351fa-wrapped-inc/CVC4-fixed/' incremental.csv
  sed -i 's/MinkeyRink ST-wrapped-inc/MinkeyRink ST/' incremental.csv
  sed -i 's/MinkeyRink MT-wrapped-inc/MinkeyRink MT/' incremental.csv
  sed -i 's/stp-incremental-2019-v2-wrapped-inc/STP/' incremental.csv
  sed -i 's/stp-mt-wrapped-inc/STP-mt/' incremental.csv
  sed -i 's/smtinterpol-2.5-514-wrapped-inc/SMTInterpol/' incremental.csv
  sed -i 's/,Yices,/,Yices (2018),/' incremental.csv
  sed -i 's/Yices 2.6.2 Incremental-wrapped-inc/Yices/' incremental.csv
  sed -i 's/,Z3,/,Z3 (2018),/' incremental.csv
  # Two different Z3 versions were used for incremental in two separate runs,
  # but were reported as one solver.
  sed -i 's/z3-4.7.4-wrapped-inc/Z3/' incremental.csv
  sed -i 's/z3-4.8.4-wrapped-inc/Z3/' incremental.csv
  sed -i 's/UltimateEliminator+MathSAT-5.5.4-wrapped-inc/UE+MathSAT/' incremental.csv
  sed -i 's/UltimateEliminator+SMTInterpol-wrapped-inc/UE+SMTInterpol/' incremental.csv
  sed -i 's/UltimateEliminator+Yices-2.6.1-wrapped-inc/UE+Yices/' incremental.csv
  sed -i 's/,MathSAT,/,MathSAT (2018),/' incremental.csv
  sed -i 's/MathSAT-wrapped-inc/MathSAT/' incremental.csv
  sed -i 's/MathSAT-na-wrapped-inc/MathSAT-na/' incremental.csv
  sed -i 's/Q3B-wrapped-inc/Q3B/' incremental.csv
popd

pushd single-query
  tar xf single_query.csv.tar.xz
  mv Single_Query_Track.csv single_query.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Single Query Track\///' single_query.csv
  sed -i 's/Competition - Single Query Track - Best 2018\///' single_query.csv
  sed -i 's/Competition - Single Query Track - Colibri fixed\///' single_query.csv
  sed -i 's/Competition - Single Query Track - STP fixed\///' single_query.csv

  # Sanitize solver names
  sed -i 's/AProVE NIA 2014-wrapped-sq/AProVE/' single_query.csv
  sed -i 's/Alt-Ergo-SMTComp-2019-wrapped-sq/Alt-Ergo/' single_query.csv
  sed -i 's/,Boolector,/,Boolector (2018),/' single_query.csv
  sed -i 's/Boolector-wrapped-sq/Boolector/' single_query.csv
  sed -i 's/COLIBRI 10_06_18 v2038/COLIBRI/' single_query.csv
  sed -i 's/colibri 2176-fixed-config-file-wrapped-sq/COLIBRI-fixed/' single_query.csv
  sed -i 's/CVC4-2019-06-03-d350fe1-wrapped-sq/CVC4/' single_query.csv
  sed -i 's/CVC4-SymBreak_03_06_2019-wrapped-sq/CVC4-SymBreak/' single_query.csv
  sed -i 's/Ctrl-Ergo-2019-wrapped-sq/Ctrl-Ergo/' single_query.csv
  sed -i 's/,Minkeyrink MT,/,MinkeyRink MT (2018),/' single_query.csv
  sed -i 's/MinkeyRink MT-wrapped-sq/MinkeyRink MT/' single_query.csv
  sed -i 's/MinkeyRink ST-wrapped-sq/MinkeyRink ST/' single_query.csv
  sed -i 's/OpenSMT-wrapped-sq/OpenSMT/' single_query.csv
  # Delete Par4 results
  sed -i '/Par4-wrapped-sq/d' single_query.csv
  sed -i 's/Poolector-wrapped-sq/Poolector/' single_query.csv
  sed -i 's/ProB-wrapped-sq/ProB/' single_query.csv
  sed -i 's/Q3B-wrapped-sq/Q3B/' single_query.csv
  sed -i 's/SMTRAT-5-wrapped-sq/SMTRAT/' single_query.csv
  sed -i 's/SMTRAT-MCSAT-4-wrapped-sq/SMTRAT-MCSAT/' single_query.csv
  sed -i 's/SMTRAT-Rat-final/SMTRAT-Rat (2018)/' single_query.csv
  sed -i 's/,SPASS-SATT,/,SPASS-SATT (2018),/' single_query.csv
  sed -i 's/SPASS-SATT-wrapped-sq/SPASS-SATT/' single_query.csv
  sed -i 's/STP-2019-wrapped-sq/STP/' single_query.csv
  sed -i 's/UltimateEliminator+MathSAT-5.5.4-wrapped-sq/UE+MathSAT/' single_query.csv
  sed -i 's/UltimateEliminator+SMTInterpol-wrapped-sq/UE+SMTInterpol/' single_query.csv
  sed -i 's/UltimateEliminator+Yices-2.6.1-wrapped-sq/UE+Yices/' single_query.csv
  sed -i 's/,Yices 2.6.0,/,Yices (2018),/' single_query.csv
  sed -i 's/Yices 2.6.2 Cadical-wrapped-sq/Yices+Cadical/' single_query.csv
  sed -i 's/Yices 2.6.2 Cryptominisat-wrapped-sq/Yices+Cryptominisat/' single_query.csv
  sed -i 's/Yices 2.6.2 MCSAT BV-wrapped-sq/Yices-MCSAT-BV/' single_query.csv
  sed -i 's/Yices 2.6.2 new bvsolver-wrapped-sq/Yices-newbv/' single_query.csv
  sed -i 's/Yices 2.6.2-wrapped-sq/Yices/' single_query.csv
  sed -i 's/boolector-ReasonLS-wrapped-sq/Boolector-ReasonLS/' single_query.csv
  sed -i 's/master-2018-06-10-b19c840-competition-default/CVC4 (2018)/' single_query.csv
  sed -i 's/mathsat-20190601-wrapped-sq/MathSAT/' single_query.csv
  sed -i 's/mathsat-na-20190601-wrapped-sq/MathSAT-na/' single_query.csv
  sed -i 's/smtinterpol-2.5-514-wrapped-sq/SMTInterpol/' single_query.csv
  sed -i 's/stp-incremental-2019-v2-wrapped-sq/STP (inc)/' single_query.csv
  sed -i 's/stp-mergesat-fixed-wrapped-sq/STP-MergeSat-fixed/' single_query.csv
  sed -i 's/stp-mergesat-wrapped-sq/STP-MergeSat/' single_query.csv
  sed -i 's/stp-minisat-wrapped-sq/STP-MiniSat/' single_query.csv
  sed -i 's/stp-mt-wrapped-sq/STP MT/' single_query.csv
  sed -i 's/stp-portfolio-fixed-wrapped-sq/STP-Portfolio-fixed/' single_query.csv
  sed -i 's/stp-portfolio-wrapped-sq/STP-Portfolio/' single_query.csv
  sed -i 's/stp-riss-wrapped-sq/STP-Riss/' single_query.csv
  sed -i 's/vampire-4.3-smt/Vampire (2018)/' single_query.csv
  sed -i 's/vampire-4.4-smtcomp-wrapped-sq/Vampire/' single_query.csv
  sed -i 's/veriT+raSAT+Redlog-wrapped-sq/veriT+raSAT+Redlog/' single_query.csv
  sed -i 's/veriT-wrapped-sq/veriT/' single_query.csv
  sed -i 's/,z3-4.7.1,/,Z3 (2018),/' single_query.csv
  sed -i 's/z3-4.8.4-d6df51951f4c-wrapped-sq/Z3/' single_query.csv
popd
popd

pushd smt-comp-results/2020
pushd incremental
  tar xf incremental.tar.xz
  cp Job_info_orig.csv incremental.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Incremental Track\///' incremental.csv

  # Sanitize solver names
  sed -i 's/Bitwuzla-wrapped-inc/Bitwuzla/' incremental.csv
  sed -i 's/CVC4-inc-final-wrapped-inc/CVC4/' incremental.csv
  sed -i 's/LazyBV2Int20200523-wrapped-inc/LazyBV2Int/' incremental.csv
  sed -i 's/MathSAT5-wrapped-inc/MathSAT5/' incremental.csv
  sed -i 's/OpenSMT-wrapped-inc/OpenSMT/' incremental.csv
  sed -i 's/STP ++ Mergsat v1-wrapped-inc-fixed/STP-MergeSat/' incremental.csv
  sed -i 's/STP-wrapped-inc/STP/' incremental.csv
  sed -i 's/UltimateEliminator+MathSAT-5.6.3_s-wrapped-inc/UE+MathSAT/' incremental.csv
  sed -i 's/Yices 2.6.2 Incremental for SMTCOMP2020-wrapped-inc/Yices/' incremental.csv
  sed -i 's/smtinterpol-2.5-671-g6d0a7c6e-wrapped-inc/SMTInterpol/' incremental.csv
  sed -i 's/z3-4.8.8-wrapped-inc/Z3/' incremental.csv

  cp Job_info_fixed.csv incremental_fixed.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Incremental Track - Fixed Solvers\///' incremental_fixed.csv

  # Sanitize solver names
  sed -i 's/Bitwuzla-fixed-wrapped-inc/Bitwuzla-fixed/' incremental_fixed.csv
  sed -i 's/Yices 2.6.2 bug fix incremental-wrapped-inc/Yices-fixed/' incremental_fixed.csv
  sed -i 's/smtinterpol-2.5-679-gacfde87a-wrapped-inc/SMTInterpol-fixed/' incremental_fixed.csv

  tail -n +2 incremental_fixed.csv >> incremental.csv

  cp Job_info_2019.csv incremental_2019.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Incremental Track - Bestof 2019\///' incremental_2019.csv

  # Sanitize solver names
  sed -i 's/,Boolector,/,Boolector (2019),/' incremental_2019.csv
  sed -i 's/,CVC4,/,CVC4 (2018),/' incremental_2019.csv
  sed -i 's/CVC4-inc-2019-06-03-d350fe1-wrapped-inc/CVC4 (2019)/' incremental_2019.csv
  sed -i 's/,MathSAT,/,MathSAT (2018),/' incremental_2019.csv
  sed -i 's/MathSAT-na-wrapped-inc/MathSAT-na (2019)/' incremental_2019.csv
  sed -i 's/MathSAT-wrapped-inc/MathSAT (2019)/' incremental_2019.csv
  sed -i 's/,Yices,/,Yices (2018),/' incremental_2019.csv
  sed -i 's/Yices 2.6.2 Incremental-wrapped-inc/Yices (2019)/' incremental_2019.csv
  sed -i 's/,Z3,/,Z3 (2018),/' incremental_2019.csv
  sed -i 's/z3-4.8.4-wrapped-inc/Z3 (2019)/' incremental_2019.csv

  tail -n +2 incremental_2019.csv >> incremental.csv

popd
pushd single-query
  tar xf single_query.tar.xz
  cp Job_info_orig.csv single_query.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Single Query track\///' single_query.csv

  # Sanitize solver names
  sed -i 's/AProVE NIA 2014/AProVE/' single_query.csv
  sed -i 's/Alt-Ergo-SMTComp-2020/Alt-Ergo/' single_query.csv
  sed -i 's/COLIBRI 20.5.25/COLIBRI/' single_query.csv
  sed -i 's/CVC4-sq-final/CVC4/' single_query.csv
  sed -i 's/LazyBV2Int20200523/LazyBV2Int/' single_query.csv
  sed -i 's/MinkeyRink Solver 2020.3.1/MinkeyRink/' single_query.csv
  sed -i 's/STP ++ Mergsat v1/STP-MergeSat/' single_query.csv
  sed -i 's/UltimateEliminator+MathSAT-5.6.3_s/UE+MathSAT/' single_query.csv
  sed -i 's/Yices 2.6.2 for SMTCOMP2020/Yices/' single_query.csv
  sed -i 's/Z3str4 SMTCOMP2020 v1.1/Z3str4/' single_query.csv
  sed -i 's/smtinterpol-2.5-671-g6d0a7c6e/SMTInterpol/' single_query.csv
  sed -i 's/smtrat-CDCAC/SMTRAT-CDCAC/' single_query.csv
  sed -i 's/smtrat-MCSAT/SMTRAT-MCSAT/' single_query.csv
  sed -i 's/smtrat-SMTCOMP/SMTRAT/' single_query.csv
  sed -i 's/vampire_smt_4.5/Vampire/' single_query.csv
  sed -i 's/z3-4.8.8/Z3/' single_query.csv

  cp Job_info_2019.csv single_query_2019.csv

  # Sanitize benchmark paths
  sed -i 's/Competition - Single Query track - Bestof 2019 and fixed solvers\///' single_query_2019.csv

  # Sanitize solver names
  sed -i 's/Boolector-wrapped-sq/Boolector (2019)/' single_query_2019.csv
  sed -i 's/CVC4-2019-06-03-d350fe1-wrapped-sq/CVC4 (2019)/' single_query_2019.csv
  sed -i 's/CVC4-SymBreak_03_06_2019-wrapped-sq/CVC4-SymBreak (2019)/' single_query_2019.csv
  sed -i 's/MinkeyRink Solver 2020.3/MinkeyRink-fixed/' single_query_2019.csv

  # Delete Par4 results
  sed -i '/Par4-wrapped-sq/d' single_query_2019.csv

  sed -i 's/Poolector-wrapped-sq/Poolector (2019)/' single_query_2019.csv
  sed -i 's/SMTRAT-Rat-final/SMTRAT-Rat (2019)/' single_query_2019.csv
  sed -i 's/SPASS-SATT-wrapped-sq/SPASS-SATT (2019)/' single_query_2019.csv
  sed -i 's/Yices 2.6.0/Yices (2018)/' single_query_2019.csv
  sed -i 's/Yices 2.6.2 bug fix/Yices-fixed/' single_query_2019.csv
  sed -i 's/Yices 2.6.2-wrapped-sq/Yices (2019)/' single_query_2019.csv
  sed -i 's/master-2018-06-10-b19c840-competition-default/CVC4 (2018)/' single_query_2019.csv
  sed -i 's/mathsat-20190601-wrapped-sq/MathSAT (2019)/' single_query_2019.csv
  sed -i 's/smtinterpol-2.5-514-wrapped-sq/SMTInterpol (2019)/' single_query_2019.csv
  sed -i 's/smtinterpol-2.5-679-gacfde87a/SMTInterpol-fixed/' single_query_2019.csv
  sed -i 's/vampire master4347 fixed/Vampire-fixed/' single_query_2019.csv
  sed -i 's/vampire-4.3-smt/Vampire (2018)/' single_query_2019.csv
  sed -i 's/vampire-4.4-smtcomp-wrapped-sq/Vampire (2019)/' single_query_2019.csv
  sed -i 's/z3-4.7.1/Z3 (2018)/' single_query_2019.csv
  sed -i 's/z3-4.8.4-d6df51951f4c-wrapped-sq/Z3 (2019)/' single_query_2019.csv

  tail -n +2 single_query_2019.csv >> single_query.csv
popd
popd
