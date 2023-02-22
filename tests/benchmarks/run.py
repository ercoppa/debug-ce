#!/bin/python3

import os
import sys
import glob
import json
import argparse
import shutil
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def run(tool, program, config, run_dir, check_expr=None, fuzz_expr=None, check_opt=None, check_pi=None, check_inputs=None, abort_on_inconsistency=False, timeout=10, rebuild=True):
    
    if rebuild:
        if tool == 'symcc':
            res = os.system("cd %s/%s && ninja" % (SCRIPT_DIR, "../../symcc/build-simple/"))
        elif tool == 'symqemu':
            res_tracer = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../symqemu/"))
            res_solver = os.system("cd %s/%s && ninja" % (SCRIPT_DIR, "../../symcc/build/"))
            res = res_tracer + res_solver
        elif tool == 'fuzzolic':
            res_tracer = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../fuzzolic/tracer/"))
            res_solver = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../fuzzolic/solver"))
            res = res_tracer + res_solver
        else:
            assert False
        if res != 0:
            print("Error when building %s" % tool)
            sys.exit(1)

    seed = "%s/%s/%s" % (SCRIPT_DIR, program, config['seed'])
    exe = "%s/%s/%s.%s" % (SCRIPT_DIR, program, config['binary'], tool)

    env = os.environ.copy()

    if tool in ['symcc', 'symqemu']:
        env['SYMCC_OUTPUT_DIR'] = run_dir + "/dump" if fuzz_expr or check_inputs else run_dir
        env['SYMCC_INPUT_FILE'] = seed
        env['SYMCC_SKIP_OPTIMISTIC'] = "1"
        if check_inputs or fuzz_expr:
            os.mkdir(env['SYMCC_OUTPUT_DIR'])

    if check_expr:
        env['DEBUG_EXPR_CONSISTENCY'] = "1"
    if fuzz_expr:
        env['DEBUG_FUZZ_EXPR'] = "DUMP"
    if check_opt:
        if check_opt == 'eval':
            env['DEBUG_CHECK_OPT'] = "EVAL"
        elif check_opt == 'smt':
            env['DEBUG_CHECK_OPT'] = "SMT"
        else:
            assert False
    if check_pi:
        if check_pi == 'eval':
            env['DEBUG_CHECK_PI'] = "EVAL"
        elif check_pi == 'smt':
            env['DEBUG_CHECK_PI'] = "SMT"
        else:
            assert False
    if check_inputs:
        env['DEBUG_CHECK_INPUT'] = "DUMP"
    else:
        env['SYMCC_SKIP_QUERIES'] = "1"
        env['DEBUG_SKIP_QUERIES'] = "1"

    if abort_on_inconsistency:
        env['DEBUG_ABORT_ON_INCONSISTENCY'] = '1'

    p_args = []
    if timeout > 0:
        p_args += [ "timeout", "-k", "1", "%d" % timeout ]
    
    if tool in ['symcc', 'symqemu']:
        if tool == 'symqemu':
            p_args += [ SCRIPT_DIR + "/../../symqemu/x86_64-linux-user/symqemu-x86_64" ]
    
        p_args += [ exe ]
        p_args += config['args'].replace("@@", seed).split(" ")

    elif tool == 'fuzzolic':
        p_args = [
            SCRIPT_DIR + "/../../fuzzolic/fuzzolic/fuzzolic.py",
            '-i', seed,
            '-o', run_dir,
            '-d', 'out',
            '-k', '-l', '--',
            exe
        ]
        p_args += config['args'].split(" ")
    else:
        assert False

    print(env)
    print(p_args)

    start = time.time()
    p = subprocess.Popen(p_args,
                        stdout=None,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        cwd=run_dir if tool in ['symcc', 'symqemu'] else run_dir + "/../",
                        bufsize=0,
                        env=env)

    p.wait()
    end = time.time()
    print("\nExecution time: %.3f [return code: %d]\n" % (end - start, p.returncode))

    if p.returncode == -11 or p.returncode == -6:
        print("ABORT DETECTED\n")
        sys.exit(1)

    if fuzz_expr or check_inputs:
        seeds = glob.glob(run_dir + "/dump/%s*" % ("debug" if fuzz_expr else "input",))
        run_dir = run_dir + "/check"
        for seed in sorted(seeds):

            if fuzz_expr:
                count = int(os.path.basename(seed).split("_")[1])
                value = int(os.path.basename(seed).split("_")[2], 16)
                s = "count=%d value=%x" % (count, value)
                env['DEBUG_FUZZ_EXPR'] = "CHECK"
                env['DEBUG_FUZZ_EXPR_COUNT'] = "%d" % count
                env['DEBUG_FUZZ_EXPR_VALUE'] = "%x" % value
            elif check_inputs:
                count = int(os.path.basename(seed).split("_")[1])
                hash = int(os.path.basename(seed).split("_")[2], 16)
                taken = int(os.path.basename(seed).split("_")[3])
                s = "hash=%x count=%d taken=%x" % (hash, count, taken)
                env['DEBUG_CHECK_INPUT'] = "CHECK"
                env['DEBUG_CHECK_INPUT_HASH'] = "%x" % hash
                env['DEBUG_CHECK_INPUT_COUNT'] = "%d" % count
                env['DEBUG_CHECK_INPUT_TAKEN'] = "%d" % taken

            print("\n################################\n# Checking %s" % os.path.basename(seed))
            print("# %s" % s)
            print("################################\n")
            if os.path.exists(run_dir):
                shutil.rmtree(run_dir)
            os.mkdir(run_dir)
            
            if tool in ['symcc', 'symqemu']:
                env['SYMCC_INPUT_FILE'] = seed
                env['SYMCC_OUTPUT_DIR'] = run_dir
                env['SYMCC_SKIP_QUERIES'] = "1"

            p_args = [ ]

            if timeout > 0:
                p_args += [ "timeout", "-k", "1", "%d" % timeout ]

            if tool in ['symcc', 'symqemu']:
                if tool == 'symqemu':
                    p_args += [ SCRIPT_DIR + "/../../symqemu/x86_64-linux-user/symqemu-x86_64" ]
            
                p_args += [ exe ]
                p_args += config['args'].replace("@@", seed).split(" ")
            else:
                p_args = [
                    SCRIPT_DIR + "/../../fuzzolic/fuzzolic/fuzzolic.py",
                    '-i', seed,
                    '-o', run_dir,
                    '-d', 'out',
                    '-k', '-l', '--',
                    exe
                ]
                p_args += config['args'].split(" ")

            # print(p_args)

            p = subprocess.Popen(p_args,
                        stdout=None,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        cwd=run_dir,
                        bufsize=0,
                        env=env)
            p.wait()

            if p.returncode == -11 or p.returncode == -6:
                print("Inconstency detected!")
                sys.exit(1)
            else:
                print("[%d] No inconsistency detected!\n" % p.returncode)

        end = time.time()
        print("\nExecution time: %.3f\n" % (end - start))

# def run_symqemu(program, config, run_dir, check_expr=None, fuzz_expr=None, check_opt=None, check_pi=None, rebuild=True):
    
#     if rebuild:
#         res = os.system("cd %s/%s && ninja" % (SCRIPT_DIR, "../../symcc/build/"))
#         if res != 0:
#             print("Error when building SymQEMU runtime")
#             sys.exit(1)

#     res = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../symqemu/"))
#     if res != 0:
#         print("Error when building SymQEMU")
#         sys.exit(1)

#     seed = "%s/%s/%s" % (SCRIPT_DIR, program, config['seed'])
#     exe = "%s/%s/%s.symqemu" % (SCRIPT_DIR, program, config['binary'])

#     env = os.environ.copy()
#     env['SYMCC_OUTPUT_DIR'] = run_dir
#     env['SYMCC_INPUT_FILE'] = seed
#     env['SYMCC_SKIP_QUERIES'] = "1"

#     p_args = [ 
#         SCRIPT_DIR + "/../../symqemu/x86_64-linux-user/symqemu-x86_64",
#         exe
#     ]
#     p_args += config['args'].replace("@@", seed).split(" ")

#     p = subprocess.Popen(p_args,
#                         stdout=None,
#                         stderr=subprocess.STDOUT,
#                         stdin=subprocess.PIPE,
#                         cwd=run_dir,
#                         bufsize=0,
#                         env=env)

#     p.wait()


# def run_fuzzolic(program, config, run_dir, check_expr=None, fuzz_expr=None, check_opt=None, check_pi=None, rebuild=True):
    
#     if rebuild:
#         res = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../fuzzolic/tracer/"))
#         if res != 0:
#             print("Error when building fuzzolic tracer")
#             sys.exit(1)

#     res = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../fuzzolic/solver"))
#     if res != 0:
#         print("Error when building fuzzolic solver")
#         sys.exit(1)

#     seed = "%s/%s/%s" % (SCRIPT_DIR, program, config['seed'])
#     exe = "%s/%s/%s.fuzzolic" % (SCRIPT_DIR, program, config['binary'])

#     env = os.environ.copy()

#     p_args = [
#         SCRIPT_DIR + "/../../fuzzolic/fuzzolic/fuzzolic.py",
#         '-i', seed,
#         '-o', run_dir,
#         '-d', 'out',
#         '-k', '-l', '--',
#         exe
#     ]
#     p_args += config['args'].split(" ")

#     print(' '.join(p_args))

#     p = subprocess.Popen(p_args,
#                         stdout=None,
#                         stderr=subprocess.STDOUT,
#                         stdin=subprocess.PIPE,
#                         cwd=run_dir + "/../",
#                         bufsize=0,
#                         env=env)

#     p.wait()


def main():

    programs = []
    for p in sorted(glob.glob(SCRIPT_DIR + "/0*")):
        p = os.path.basename(p)
        programs.append(p)

    parser = argparse.ArgumentParser(
        description='Run benchmarks for debug-ce')

    # S1A
    parser.add_argument(
        '-e', '--expr', 
        help='Check expression consistency', 
        action='store_true')

    # S1B
    parser.add_argument(
        '-f', '--fuzz', 
        help='Fuzz expressions', 
        action='store_true')

    # S2{A, B}
    parser.add_argument(
        '-o', '--opt', 
        help='Check optimizations', 
        choices=['eval', 'smt'])

    # S3A
    parser.add_argument(
        '-p', '--path', 
        help='Check path constraints', 
        choices=['eval', 'smt'])

    # S3B
    parser.add_argument(
        '-i', '--input', 
        help='Check generated inputs', 
        action='store_true')

    parser.add_argument(
        '-c', '--cont', 
        help='Do not abort on inconsistency', 
        action='store_true')

    # required args
    parser.add_argument(
        '-t', '--tool', 
        help='Concolic executor to use during the experiment', 
        required=True, 
        choices=['symcc', 'symqemu', 'fuzzolic'])

    # positional args
    parser.add_argument('program', metavar='<program>',
                        type=str, help='Program to run during the experiment',
                        choices=programs)

    args = parser.parse_args()

    config_file = "%s/%s/config.json" % (SCRIPT_DIR, args.program)
    if not os.path.exists(config_file):
        print("Missing config file for %s" % args.program)
        sys.exit(1)

    config = {}
    with open(config_file, "r") as fp:
        config = json.loads(fp.read())
    
    assert 'binary' in config
    assert 'args' in config
    assert 'seed' in config

    print("Running %s with %s..." % (args.tool, args.program))

    work_dir = SCRIPT_DIR + "/workdir"
    if os.path.exists(work_dir):
        if os.path.exists("%s/.fuzzolic_workdir" % work_dir):
            shutil.rmtree(work_dir)
        else:
            print("Remove %s manually!" % work_dir)
            sys.exit(1)

    os.mkdir("workdir")
    os.system("touch %s/.fuzzolic_workdir" % work_dir)

    if args.tool in ['symcc', 'symqemu', 'fuzzolic']:
        f = False if args.cont else True
        run(args.tool, args.program, config, work_dir, check_expr=args.expr, fuzz_expr=args.fuzz, check_opt=args.opt, check_pi=args.path, check_inputs=args.input, abort_on_inconsistency=f)
    else:
        print("Not yet implemented: %s" % args.tool)
        sys.exit(1)

if __name__ == "__main__":
    main()


