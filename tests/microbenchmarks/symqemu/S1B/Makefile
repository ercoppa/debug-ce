all: clean
	./run.sh

gdb:
	SYMCC_OUTPUT_DIR=`pwd`/out SYMCC_INPUT_FILE=input.dat gdb ./main.symcc 

clean:
	rm -rf out || echo "Nothing to clean"
	mkdir out
