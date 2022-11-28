#!/bin/bash

# for logic in lib-sq/2019/single-query/*; do
#    machsmt_eval -l "$logic" -r results-2019
# done

for logic in lib-inc/2019/incremental/*; do
    machsmt_eval -l "$logic" -r results-2019-inc
done

#for logic in lib-sq/2020/single-query/*; do
#    machsmt_eval -l "$logic" -r results-2020
#done

#for logic in lib-inc/2020/incremental/*; do
#    machsmt_eval -l "$logic" -r results-2020-inc
#done
