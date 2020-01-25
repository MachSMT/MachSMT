#!/usr/bin/env bash

for csv in $(find -name par2.csv); do
  awk -vcsv="$csv" -F ',' '
  NR > 1 {
   r[$1]=$2;
  }
  END {
   score_vbs = r["Virtual Best"]
   score_smtzilla = r["SMTZILLA"]
   ratio = score_smtzilla/score_vbs
   print ratio,csv,"(VBS:",score_vbs,", SMTZILLA:",score_smtzilla,")"
  }' "$csv"
done | sort -n -r
