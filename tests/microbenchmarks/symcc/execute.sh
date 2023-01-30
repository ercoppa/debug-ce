(cd ../../../../symcc/build/ && ninja || exit 1)
../../../../symcc/build/symcc -o main.symcc main.c
export SYMCC_OUTPUT_DIR=`pwd`/out
rm -rf $SYMCC_OUTPUT_DIR || echo "Nothing to clean"
mkdir $SYMCC_OUTPUT_DIR
SYMCC_INPUT_FILE=input.dat ./main.symcc input.dat