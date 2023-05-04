#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
BINARY=readelf

export SYMCC_NO_SYMBOLIC_INPUT=1

function build() {
    SUFFIX=$1
    rm -rf build || echo "Nothing to clean"
    cp -a src build
    rm ${BINARY}.${SUFFIX} || echo "Nothing to clean"
    cd build
    ./configure && make -j `nproc`
    cp binutils/${BINARY} ../${BINARY}.${SUFFIX}
    cd ..
}

rm -rf src || echo "Nothing to clean" 
tar xvf binutils-2.34.tar.gz >/dev/null
mv binutils-2.34 src

source ${SCRIPTPATH}/../../source-symcc.sh
build "symcc"
# exit 0
source ${SCRIPTPATH}/../../source-native.sh
build "symqemu"
cp ${BINARY}.symqemu ${BINARY}.fuzzolic
