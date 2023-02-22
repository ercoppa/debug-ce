build: clean
	cd libpng-1.6.37 && CFLAGS="--coverage" ./configure && make clean && make -j4
	g++ --coverage libpngExample1.cpp -o libpng.coverage -I./libpng-1.6.37/ libpng-1.6.37/.libs/libpng16.a -lz
	cd libpng-1.6.37 && make clean

clean:
	rm libpng-1.6.37/*.gcno || echo
	rm libpngExample1.gcno || echo