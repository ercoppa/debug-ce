#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
BINARY=bsdtar

export SYMCC_NO_SYMBOLIC_INPUT=1
export SYMCC_LIBCXX_PATH=/debug-ce/libcxx_build/

function build() {
    SUFFIX=$1
    rm -rf build || echo "Nothing to clean"
    cp -a src build
    rm ${BINARY}.${SUFFIX} || echo "Nothing to clean"
    cd build
    mkdir inst 
    cd inst
    cmake -DCMAKE_BUILD_TYPE=Release .. && make -j `nproc`
    cp bin/${BINARY} ../../${BINARY}.${SUFFIX}
    cd ../..
}

rm -rf src || echo "Nothing to clean" 
git clone https://github.com/libarchive/libarchive/
cd libarchive && git checkout f3b1f9f239c580b38f4d1197a40c6dde9753672e && cd ..
mv libarchive src

source ${SCRIPTPATH}/../../source-symcc.sh
build "symcc"
# exit 0
source ${SCRIPTPATH}/../../source-native.sh
build "symqemu"
cp ${BINARY}.symqemu ${BINARY}.fuzzolic
