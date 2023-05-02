# Testing Concolic Execution Through Consistency Checks

## Fetch this repository
```
git clone https://github.com/ercoppa/debug-ce.git
```

## Fetch our forks of the three concolic executors
- SymCC:
```
git clone -b debug-ce https://github.com/ercoppa/symcc-debug-ce.git
cd symcc && git submodule init && git submodule update && cd ..
```
- SymQEMU
```
git clone -b debug-ce https://github.com/ercoppa/debug-ce-symqemu.git
```
- Fuzzolic:
```
git clone -b debug-ce https://github.com/season-lab/fuzzolic.git
cd fuzzolic && git submodule init && git submodule update && cd ..
```

## Enable/disable our fixes
Edit `config.h` to enable or disable a fix. 

## Build a container
To build the container:
```
cd runner && docker build -t ercoppa/debug-ce -f ./Dockerfile ../
```

## Runner script
We devised a script `run.py` in `tests/` for launching the experiments. The script has the following syntax:
```
$ ./run.py --help
usage: run.py [-h] [-n] [-e] [-f] [-o {eval,smt}] [-p {eval,smt}] [-i] [-c] [-w WORKDIR] [-b] [-g] -t {symcc,symqemu,fuzzolic} -s {simple,real} <program>

Run benchmarks for debug-ce

positional arguments:
  <program>             Program to run during the experiment

optional arguments:
  -h, --help            show this help message and exit
  -n, --count           Count checks and inconsistencies
  -e, --expr            Check expression consistency
  -f, --fuzz            Fuzz expressions
  -o {eval,smt}, --opt {eval,smt}
                        Check optimizations
  -p {eval,smt}, --path {eval,smt}
                        Check path constraints
  -i, --input           Check generated inputs
  -c, --cont            Do not abort on inconsistency
  -w WORKDIR, --workdir WORKDIR
                        Workir
  -b, --build           (Re)Build tool
  -g, --gdb             Run under GDB
  -t {symcc,symqemu,fuzzolic}, --tool {symcc,symqemu,fuzzolic}
                        Concolic executor to use during the experiment
  -s {simple,real}, --scenario {simple,real}
                        Simpliefied programs or real-world programs
```
The strategies can selected by following this mapping:
   * C1A: `-e`
   * C1B: `-f`
   * C2A: `-p eval` (or `-p smt` to use the variant based on the SMT solver)
   * C2B: `-i`
   * C3A: `-o eval`
   * C3B: `-o smt`


## Replay simplified scenario
```
$ docker run -ti --cap-add SYS_ADMIN --rm -w /debug-ce --name debug-ce-run-`date "+%y%m%d-%H%M"` bash
$ cd tests
$ ./run.py -t <tool> -s simple <check strategy> <program>
```
where:
 * `<tool>` is one of {`symcc`, `fuzzolic`, `symqemu`} 
 * `<check strategy>` is one of the option described in the previous section
 * `<program>` is one of {`S1A`, `S1B`, `S2A`, `S2B`, `S3`, `S4`, `S4A`, `S4B`, `S5`, `S6`, `S7`} 

## Replay real-world scenario
```
$ docker run -ti --cap-add SYS_ADMIN --rm -w /debug-ce --name debug-ce-run-`date "+%y%m%d-%H%M"` bash
$ cd tests
$ ./run.py -t <tool> -s real <check strategy> <program>
```
where:
 * `<tool>` is one of {`symcc`, `fuzzolic`, `symqemu`} 
 * `<check strategy>` is one of the option described in the previous section
 * `<program>` is one of {`01-objdump`, `02-readelf`, `03-tcpdump`, `04-bsdtar`, `05-libpng`, `06-libtiff`} 