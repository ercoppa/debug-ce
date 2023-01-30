all:
	@echo "Targets: build, run"

build:
	docker build -t ercoppa/debug-ce -f ./Dockerfile ../

run:
	docker run -ti --cap-add SYS_ADMIN --rm \
		-w /debug-ce \
		-v `pwd`/../Makefile:/debug-ce/Makefile \
		-v `pwd`/../config.h:/debug-ce/config.h \
		-v `pwd`/../tests:/debug-ce/tests \
		-v `pwd`/../symcc:/debug-ce/symcc \
		-v `pwd`/../symqemu:/debug-ce/symqemu \
		-v `pwd`/../fuzzolic:/debug-ce/fuzzolic \
		--name debug-ce-run-`date "+%y%m%d-%H%M"` \
		ercoppa/debug-ce bash