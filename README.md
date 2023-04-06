# Debugging Concolic Execution

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
If you want to add the symbolic QEMU helpers in SymQEMU then:
```
cd runner && docker build -t ercoppa/debug-ce --build-arg ENV=symhelpers -f ./Dockerfile ../
```

## Replay simplified scenario
```
docker run -ti --cap-add SYS_ADMIN --rm -w /debug-ce --name debug-ce-run-`date "+%y%m%d-%H%M"`
```

## Replay real-world scenario
```
docker run -ti --cap-add SYS_ADMIN --rm -w /debug-ce --name debug-ce-run-`date "+%y%m%d-%H%M"`
```