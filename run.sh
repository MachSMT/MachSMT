
#
#
#
#

sudo python3 setup.py develop

machsmt_build -f smt-comp-data/smtcomp_2019.csv smt-comp-data/smtcomp_2020.csv -l lib


machsmt_eval -l lib