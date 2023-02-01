FROM ubuntu:20.04 AS builder

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak
RUN sed -Ei 's/^# deb-src /deb-src /' /etc/apt/sources.list

# Install dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    cargo \
    clang-10 \
    cmake \
    g++ \
    git wget \
    libz3-dev \
    llvm-10-dev \
    llvm-10-tools \
    ninja-build \
    python2 \
    python3-pip \
    zlib1g-dev \
    ca-certificates \
    sudo nano gdb xxd \
    && DEBIAN_FRONTEND=noninteractive apt build-dep -y qemu && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/llvm-config-10 /usr/bin/llvm-config

RUN pip3 install lit psutil

RUN groupadd --gid 1008 ubuntu && \
     useradd --uid 1008 --gid ubuntu --shell /bin/bash --create-home ubuntu && \
     echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu

RUN mkdir /debug-ce
RUN chown -R ubuntu:ubuntu /debug-ce
COPY --chown=ubuntu:ubuntu config.h /debug-ce/config.h
USER ubuntu

# install GEF
WORKDIR /tmp
RUN wget -q https://raw.githubusercontent.com/hugsy/gef/main/scripts/gef.sh && chmod +x ./gef.sh && bash -c ./gef.sh && rm gef.sh 

# Build AFL++
RUN mkdir -p /debug-ce/fuzzolic/utils
COPY --chown=ubuntu:ubuntu fuzzolic/utils/afl-showmap.c.patch /debug-ce/fuzzolic/utils/
WORKDIR /debug-ce/fuzzolic/utils
RUN git clone https://github.com/AFLplusplus/AFLplusplus.git && \
	cd AFLplusplus && git checkout 2dac4e7 && \
	git apply ../afl-showmap.c.patch && \
	make -j `nproc` all && cd qemu_mode && ./build_qemu_support.sh
ENV AFL_PATH=/debug-ce/fuzzolic/utils/AFLplusplus

# Download the LLVM sources for SymCC
RUN git clone -b llvmorg-10.0.1 --depth 1 https://github.com/llvm/llvm-project.git /debug-ce/llvm_source

# Build new Z3 (old one has a regression)
WORKDIR /tmp
RUN wget https://github.com/Z3Prover/z3/archive/refs/tags/z3-4.8.14.tar.gz && tar xvf z3-4.8.14.tar.gz && cp -a z3-z3-4.8.14 /debug-ce/z3 && rm -rf /tmp/z3*
RUN sudo rm /debug-ce/z3/build || echo "Nothing to clean" 
RUN mkdir /debug-ce/z3/build
WORKDIR /debug-ce/z3/build
RUN cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=`pwd`/dist && make -j `nproc` && make install

# Build SymCC
COPY --chown=ubuntu:ubuntu symcc /debug-ce/symcc/ 
RUN sudo rm -rf /debug-ce/symcc/build || echo "Nothing to remove" 
RUN mkdir /debug-ce/symcc/build
WORKDIR /debug-ce/symcc/build
RUN cmake -G Ninja \
    -DQSYM_BACKEND=ON \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DZ3_DIR=/debug-ce/z3/build/dist/lib/cmake/z3 \
    -DLLVM_DIR=`llvm-config-10 --cmakedir` \
    /debug-ce/symcc \
    && ninja

# RUN cargo install --path /debug-ce/symcc/util/symcc_fuzzing_helper

# Build libc++ with SymCC
RUN mkdir /debug-ce/libcxx_build
WORKDIR /debug-ce/libcxx_build
RUN export SYMCC_REGULAR_LIBCXX=yes SYMCC_NO_SYMBOLIC_INPUT=yes \
     && cmake -G Ninja /debug-ce/llvm_source/llvm \
          -DLLVM_ENABLE_PROJECTS="libcxx;libcxxabi" \
          -DLLVM_TARGETS_TO_BUILD="X86" \
          -DLLVM_DISTRIBUTION_COMPONENTS="cxx;cxxabi;cxx-headers" \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=/debug-ce/libcxx_build \
          -DCMAKE_C_COMPILER=/debug-ce/symcc/build/symcc \
          -DCMAKE_CXX_COMPILER=/debug-ce/symcc/build/sym++ \
     && ninja distribution \
     && ninja install-distribution

# Build SymQEMU
COPY --chown=ubuntu:ubuntu symqemu /debug-ce/symqemu/ 
WORKDIR /debug-ce/symqemu/
RUN sed -Ei 's#https://git.qemu.org/git#https://gitlab.com/qemu-project#' .git/config
RUN sed -Ei 's#https://git.qemu.org/git#https://gitlab.com/qemu-project#' .gitmodules
RUN ./configure                                                     \
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
    --symcc-build=/debug-ce/symcc/build &&                          \
    make -j `nproc`

# Build Fuzzolic
RUN mv /debug-ce/fuzzolic /debug-ce/fuzzolic.afl
COPY --chown=ubuntu:ubuntu fuzzolic /debug-ce/fuzzolic/ 
WORKDIR /debug-ce/fuzzolic/
RUN mv /debug-ce/fuzzolic.afl/utils/AFLplusplus utils/ && rm -rf /debug-ce/fuzzolic.afl
# RUN git submodule sync && git submodule update --init --recursive
RUN sudo rm -rf /debug-ce/fuzzolic/tracer/build || echo "Nothing to remove" 
RUN cd tracer && ./configure --prefix=`pwd`/../build --target-list=x86_64-linux-user && make -j `nproc` 
RUN sudo rm -rf /debug-ce/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build || echo "Nothing to remove"
RUN cd solver/fuzzy-sat/fuzzolic-z3 && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=`pwd`/dist && make -j `nproc` && make install
ENV C_INCLUDE_PATH=/debug-ce/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/include
ENV LIBRARY_PATH=/debug-ce/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib
ENV LD_LIBRARY_PATH=/debug-ce/fuzzolic/solver/fuzzy-sat/fuzzolic-z3/build/dist/lib
RUN cd solver/fuzzy-sat && make -j `nproc`
RUN cd solver && cmake . && make -j `nproc`


WORKDIR /debug-ce/