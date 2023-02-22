build: clean
	cd binutils-2.34 && rm ./*/config.cache ; CFLAGS="--coverage -g -no-pie" ./configure && make clean && make -j2
	cp binutils-2.34/binutils/objdump.gcno .
	cp binutils-2.34/binutils/objdump objdump.coverage
	# cd binutils-2.34 && make clean

clean:
	rm objdump.coverage || echo
	rm objdump.gcno || echo