#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd ../../../../symcc/

# git diff --exit-code --quiet
if ls; then
    echo -ne "Applying the patch... "
    git apply ${SCRIPT_DIR}/bug.patch 2>&1
    echo -e "DONE\n"
else
    echo "Tree is dirty, please commit changes before running this!"
    exit 1
fi

cd ${SCRIPT_DIR}

(cd ../../../../symcc/build/ && ninja)
../../../../symcc/build/symcc -o main.symcc main.c
SYMCC_OUTPUT_DIR=`pwd`/out SYMCC_INPUT_FILE=input.dat ./main.symcc input.dat

cd ../../../../symcc/
git apply -R ${SCRIPT_DIR}/bug.patch 2>&1