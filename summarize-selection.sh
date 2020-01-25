#!/usr/bin/env bash

for csv in $(find -name selections.csv); do
  echo ""
  echo "$csv"

  awk -F ',' '
  NR > 1 {
   s[$NF]+=1;
   total+=1;
  }
  END {
   for (i in s)
   {
     print s[i],i
   }
   print total, "total"
  }' "$csv" | sort -n
done
