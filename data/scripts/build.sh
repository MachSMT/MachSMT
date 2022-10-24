#!/bin/bash

# Note: Make sure to checkout the 2019 release of SMT-LIB before running this

# Build models for 2019 single query data
#for csv in csv/2019/single-query/*.csv; do
#    logic=$(basename $csv)
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-sq/2019/single-query/$logic"
#done

# Build models for 2019 incremental data
#for csv in csv/2019/incremental/*.csv; do
#    logic=$(basename $csv)
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-inc/2019/incremental/$logic"
#done


# Note: Make sure to checkout the 2020 release of SMT-LIB before running this

## Build models for 2020 single query data
#for csv in csv/2020/single-query/*.csv; do
#    logic=$(basename "$csv")
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-sq/2020/single-query/$logic"
#done
#
### Build models for 2020 incremental data
#for csv in csv/2020/incremental/*.csv; do
#    logic=$(basename $csv)
#    logic=${logic%.csv}
#    machsmt_build -f "$csv" -l "lib-inc/2020/incremental/$logic"
#done

