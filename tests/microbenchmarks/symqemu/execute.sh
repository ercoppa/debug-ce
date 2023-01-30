(cd ../../../../symcc/build/ && ninja || exit 1)
(cd ../../../../symqemu && make || exit 1)
clang-10 -o main.symqemu main.c
export SYMCC_OUTPUT_DIR=`pwd`/out
rm -rf $SYMCC_OUTPUT_DIR || echo "Nothing to clean"
mkdir $SYMCC_OUTPUT_DIR
# -d in_asm,op_opt
SYMCC_INPUT_FILE=input.dat ../../../../symqemu/x86_64-linux-user/symqemu-x86_64 ./main.symqemu input.dat # 2> qemu.log