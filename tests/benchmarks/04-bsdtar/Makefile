build: clean
	cd libarchive && mkdir inst && cd inst && CFLAGS="--coverage -g -no-pie" cmake -DCMAKE_BUILD_TYPE=Release .. && make -j `nproc`
	cp libarchive/inst/bin/bsdtar bsdtar.coverage

clean:
	rm -rf libarchive/inst
	rm bsdtar.coverage || echo