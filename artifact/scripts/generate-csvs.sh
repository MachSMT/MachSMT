#!/bin/bash

#scripts/download-smt-comp-results.sh
#scripts/sanitize-smt-comp-data.sh


# Note: Make sure to checkout the 2019 release of SMT-LIB before running this

#mkdir -p csv/2019/{incremental,single-query}
#echo "Generate CSVs for 2019 incremental"
#python scripts/make_csvs.py --incremental smt-comp-results/2019/incremental/incremental.csv 2019 /data/SMT-LIB-incremental/ csv/2019/incremental/
#echo "Generate CSVs for 2019 single query"
#python scripts/make_csvs.py smt-comp-results/2019/single-query/single_query.csv 2019 /data/SMT-LIB-non-incremental/ csv/2019/single-query/

# Note: Make sure to checkout the 2020 release of SMT-LIB before running this

mkdir -p csv/2020/{incremental,single-query}
echo "Generate CSVs for 2020 incremental"
python scripts/make_csvs.py --incremental smt-comp-results/2020/incremental/incremental.csv 2020 /data/SMT-LIB-incremental/ csv/2020/incremental/
echo "Generate CSVs for 2020 single query"
python scripts/make_csvs.py smt-comp-results/2020/single-query/single_query.csv 2020 /data/SMT-LIB-non-incremental/ csv/2020/single-query/
