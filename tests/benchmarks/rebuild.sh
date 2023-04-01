#!/bin/bash

cd 01* && ./build.sh || exit 1
cd ..
cd 02* && ./build.sh || exit 1
cd ..
cd 03* && ./build.sh || exit 1
cd ..
cd 04* && ./build.sh || exit 1
cd ..
cd 05* && ./build.sh || exit 1
cd ..
cd 06* && ./build.sh || exit 1

exit 0
