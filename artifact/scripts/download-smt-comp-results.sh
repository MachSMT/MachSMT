#!/bin/bash

mkdir -p smt-comp-results/2019/{incremental,single-query}
wget https://github.com/SMT-COMP/smt-comp/raw/master/2019/results/Incremental_Track.csv.tar.xz -O smt-comp-results/2019/incremental/incremental.csv.tar.xz
wget https://github.com/SMT-COMP/smt-comp/raw/master/2019/results/Single_Query_Track.csv.tar.xz -O smt-comp-results/2019/single-query/single_query.csv.tar.xz

mkdir -p smt-comp-results/2020/{incremental,single-query}
wget https://github.com/SMT-COMP/smt-comp/raw/master/2020/results/incremental/Job_infos.tar.xz -O smt-comp-results/2020/incremental/incremental.tar.xz
wget https://github.com/SMT-COMP/smt-comp/raw/master/2020/results/single-query/Job_infos.tar.xz -O smt-comp-results/2020/single-query/single_query.tar.xz
