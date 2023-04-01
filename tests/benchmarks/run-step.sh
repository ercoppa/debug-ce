#!/bin/bash

TOOL="symqemu"
STEP="-e"
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir01 01-* 2>&1 > workdir01.log &
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir02 02-* 2>&1 > workdir02.log &
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir03 03-* 2>&1 > workdir03.log &
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir04 04-* 2>&1 > workdir04.log &
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir05 05-* 2>&1 > workdir05.log &
./run.py -t ${TOOL} -n -c ${STEP} -w `pwd`/workdir06 06-* 2>&1 > workdir06.log &

wait

exit 0
