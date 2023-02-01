#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source ../apply_patch.sh
source ../execute.sh

FILES=`ls ./out/fuzzolic-00000/test_case_*_0-*.dat`
for f in $FILES
do
  HASH=`basename $f | cut -f2 -d'-' | cut -f1 -d'_'`
  COUNT=`basename $f | cut -f2 -d'-' | cut -f2 -d'_'`
  TAKEN=`basename $f | cut -f2 -d'-' | cut -f3 -d'_' | cut -f1 -d'.'`
  echo -e "\n################################\n# Checking $f"
  echo -ne "# hash=${HASH} count=${COUNT} taken=${TAKEN}"
  echo -e "\n################################\n"
  DEBUG_SKIP_QUERIES=1 DEBUG_CHECK_INPUT=1 DEBUG_CHECK_INPUT_COUNT=${COUNT} DEBUG_CHECK_INPUT_HASH="${HASH}" DEBUG_CHECK_INPUT_TAKEN=${TAKEN} ../../../../fuzzolic/fuzzolic/fuzzolic.py -i $f -o out2 -d out -k -l -- ./main.fuzzolic @@
done

source ../revert_patch.sh