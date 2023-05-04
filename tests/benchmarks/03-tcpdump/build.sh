#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
BINARY=tcpdump

export SYMCC_NO_SYMBOLIC_INPUT=1

# flex bison

function build() {
    SUFFIX=$1
    rm ${BINARY}.${SUFFIX} || echo "Nothing to clean"
    rm -rf libpcap-1.9.1 || echo "Nothing to clean"
    cp -a src_libpcap libpcap-1.9.1
    cd libpcap-1.9.1
    ./configure && make -j `nproc`
    cd ..
    rm -rf build_tcpdump || echo "Nothing to clean"
    cp -a src_tcpdump build_tcpdump
    cd build_tcpdump
    ./configure --with-cap_ng=no && make -j `nproc`
    cp ${BINARY} ../${BINARY}.${SUFFIX}
    cd ..
}

rm -rf libpcap-1.9.1 || echo "Nothing to clean"

rm -rf src_libpcap || echo "Nothing to clean" 
tar xvf libpcap-1.9.1.tar.gz >/dev/null
mv libpcap-1.9.1 src_libpcap

rm -rf src_tcpdump || echo "Nothing to clean" 
tar xvf tcpdump-4.9.3.tar.gz >/dev/null
mv tcpdump-4.9.3 src_tcpdump

source ${SCRIPTPATH}/../../source-symcc.sh
build "symcc"
# exit 0
source ${SCRIPTPATH}/../../source-native.sh
build "symqemu"
cp ${BINARY}.symqemu ${BINARY}.fuzzolic
