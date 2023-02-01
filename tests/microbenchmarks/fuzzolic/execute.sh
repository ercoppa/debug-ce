(cd ../../../../fuzzolic/tracer && make || exit 1)
(cd ../../../../fuzzolic/solver && make || exit 1)
clang-10 -o main.fuzzolic main.c
../../../../fuzzolic/fuzzolic/fuzzolic.py -i input.dat -o out -d out -k -l -- ./main.fuzzolic @@