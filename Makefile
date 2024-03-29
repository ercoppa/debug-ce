all:
	@echo "Targets: build"

configure-symcc:
	rm -rf symcc/build-simple || echo "Nothing to clean"
	mkdir symcc/build-simple && cd symcc/build-simple && cmake -G Ninja \
		-DQSYM_BACKEND=OFF \
		-DCMAKE_BUILD_TYPE=RelWithDebInfo \
		-DZ3_DIR=/debug-ce/z3/build/dist/lib/cmake/z3 \
		-DLLVM_DIR=`llvm-config-10 --cmakedir` \
		/debug-ce/symcc \
		&& ninja

configure-symcc-symqemu:
	rm -rf symcc/build || echo "Nothing to clean"
	mkdir symcc/build && cd symcc/build && cmake -G Ninja \
		-DQSYM_BACKEND=ON \
		-DCMAKE_BUILD_TYPE=RelWithDebInfo \
		-DZ3_DIR=/debug-ce/z3/build/dist/lib/cmake/z3 \
		-DLLVM_DIR=`llvm-config-10 --cmakedir` \
		/debug-ce/symcc \
		&& ninja

configure-symqemu: configure-symcc-symqemu
	cd symqemu && ./configure                                       \
    --audio-drv-list=                                               \
    --disable-bluez                                                 \
    --disable-sdl                                                   \
    --disable-gtk                                                   \
    --disable-vte                                                   \
    --disable-opengl                                                \
    --disable-virglrenderer                                         \
    --disable-werror                                                \
    --target-list=x86_64-linux-user                                 \
    --enable-capstone=git                                           \
    --symcc-source=/debug-ce/symcc/                                 \
    --symcc-build=/debug-ce/symcc/build

build-symcc:
	cd symcc/build-simple && ninja

build-symqemu:
	cd symcc/build && ninja
	cd symqemu && make -j `nproc`

build-fuzzolic:
	cd fuzzolic/tracer && make

build: build-symcc build-symqemu build-fuzzolic
	@echo "Done"
