#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source ../apply_patch.sh
source ../execute.sh

FILES="./out/*"
for f in $FILES
do
  SUB='opt'
  if [[ "$f" == *"$SUB"* ]]; then
    echo -e "\nSkipping optimistic input"
  else
    echo -e "\nChecking $f..."
    export SYMCC_OUTPUT_DIR=`pwd`/out2
    rm -rf $SYMCC_OUTPUT_DIR || echo "Nothing to clean"
    mkdir $SYMCC_OUTPUT_DIR
    HASH=`echo $f | cut -f2 -d'_'`
    COUNT=`echo $f | cut -f3 -d'_'`
    TAKEN=`echo $f | cut -f4 -d'_'`
    echo -e "\n################################\n# Checking $f"
    echo -ne "# hash=${HASH} count=${COUNT} taken=${TAKEN}"
    echo -e "\n################################\n"
    SYMCC_INPUT_FILE=$f SYMCC_SKIP_QUERIES=1 DEBUG_CHECK_INPUT=1 DEBUG_CHECK_INPUT_COUNT=${COUNT} DEBUG_CHECK_INPUT_HASH="${HASH}" DEBUG_CHECK_INPUT_TAKEN=${TAKEN} ./main.symcc $f
    EXIT_CODE=$?
    echo "EXIT STATUS: ${EXIT_CODE}"
  fi
done

source ../revert_patch.sh