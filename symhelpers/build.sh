#!/bin/bash

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`

export PATH="$SCRIPTPATH/../symcc/build/:${PATH}"

clang -c wrappers.c -O1 -fPIC \
    -I../symqemu/include/ \
    -I../symqemu/ \
    `pkg-config --cflags glib-2.0` \
    -I../symqemu/tcg/ \
    -I../symqemu/tcg/i386/ \
    -I../symqemu/target/i386/ \
    -I../symqemu/x86_64-linux-user/ \
    -I../symqemu/accel/tcg/ && \
\
symcc -shared fpu_helper.c cc_helper.c int_helper.c \
    wrappers.o -o libsymhelpers.so -O1 -fPIC \
    -I../symqemu/include/ \
    -I../symqemu/ \
    `pkg-config --cflags --libs glib-2.0` \
    -I../symqemu/tcg/ \
    -I../symqemu/tcg/i386/ \
    -I../symqemu/target/i386/ \
    -I../symqemu/x86_64-linux-user/ \
    -I../symqemu/accel/tcg/
