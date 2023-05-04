#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
BINARY=libpng

export SYMCC_NO_SYMBOLIC_INPUT=1
export SYMCC_LIBCXX_PATH=/debug-ce/libcxx_build/

function build() {
    SUFFIX=$1
    rm -rf build || echo "Nothing to clean"
    cp -a src build
    rm ${BINARY}.${SUFFIX} || echo "Nothing to clean"
    cd build
    ./configure && make -j `nproc`
    cd ..
    ${CC} libpng-short-example.c -o ${BINARY}.${SUFFIX} -I./build/ build/.libs/libpng16.a -lz -lm
}

rm -rf src || echo "Nothing to clean" 
tar xvf libpng-1.6.37.tar.gz >/dev/null
mv libpng-1.6.37 src

source ${SCRIPTPATH}/../../source-symcc.sh
build "symcc"
# exit 0
source ${SCRIPTPATH}/../../source-native.sh
build "symqemu"
cp ${BINARY}.symqemu ${BINARY}.fuzzolic
