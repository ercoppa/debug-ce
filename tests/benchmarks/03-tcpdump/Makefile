build: clean
	cd libpcap-1.9.1 && CFLAGS="--coverage -g -no-pie" ./configure && make clean && make
	cd tcpdump-4.9.3 && CFLAGS="--coverage -g -no-pie" ./configure --with-cap_ng=no && make clean && make
	cp ./tcpdump-4.9.3/tcpdump.gcno .
	cp ./tcpdump-4.9.3/tcpdump tcpdump.coverage
	#cd libpcap-1.9.1 && make clean
	#cd tcpdump-4.9.3 && make clean

clean:
	rm tcpdump.coverage || echo
	rm tcpdump.gcno || echo