#!/bin/bash

SCRIPT_DIR=`pwd`

PATCH=`ls ${SCRIPT_DIR}/*.patch`
PATCH=`basename ${PATCH}`

if [[ ${PATCH} == symcc* ]]; then
    SRC_DIR="/debug-ce/symcc/"
elif [[ ${PATCH} == qsym* ]]; then
    SRC_DIR="/debug-ce/symcc/runtime/qsym_backend/qsym/"
else
    echo "Cannot recognize project!"
    exit 1
fi

# git diff --exit-code --quiet
if ls 2>&1 >/dev/null; then
    cd ${SRC_DIR}
    echo -ne "Applying the patch... "
    git apply ${SCRIPT_DIR}/${PATCH} 2>&1 && echo -e "DONE\n"
else
    echo "Tree is dirty, please commit changes before running this!"
    exit 1
fi

cd ${SCRIPT_DIR}