#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
BINARY=tiff2pdf

export SYMCC_NO_SYMBOLIC_INPUT=1
export SYMCC_LIBCXX_PATH=/debug-ce/libcxx_build/

function build() {
    SUFFIX=$1
    rm -rf build || echo "Nothing to clean"
    cp -a src build
    rm ${BINARY}.${SUFFIX} || echo "Nothing to clean"
    cd build
    ./autogen.sh && ./configure --disable-shared --prefix="$PWD/work" --disable-jbig && make -j `nproc` && make install
    cp work/bin/${BINARY} ../${BINARY}.${SUFFIX}
    cd ..
}

rm -rf src || echo "Nothing to clean" 
tar xvf tiff-4.1.0.tar.gz >/dev/null
mv tiff-4.1.0 src

source ${SCRIPTPATH}/../../source-symcc.sh
build "symcc"
# exit 0
source ${SCRIPTPATH}/../../source-native.sh
build "symqemu"
cp ${BINARY}.symqemu ${BINARY}.fuzzolic
