#!/bin/bash

cd ${SRC_DIR}
echo -ne "\nReverting the patch... "
git apply -R ${SCRIPT_DIR}/${PATCH} 2>&1 && echo -e "DONE\n"
cd ${SCRIPT_DIR}