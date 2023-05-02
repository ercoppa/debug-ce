#!/bin/python3

import os
import sys
import glob
import json
import argparse
import shutil
import subprocess
import time
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def wait_process(p, log):

    if log is None:
        p.wait()
        return

    offset = 0
    done = False
    while not done:
        try:
            p.wait(timeout=0.1)
            done = True
        except:
            pass
        if log:
            f = open(log, 'rb')
            f.seek(offset)
            data = f.read().decode('unicode_escape')
            sys.stdout.write(data)
            offset += len(data)

def run(tool, program, config, run_dir, check_expr=None, fuzz_expr=None, check_opt=None, check_pi=None, check_inputs=None, abort_on_inconsistency=False, count=False, timeout=90, rebuild=True, use_gdb=False):
    
    if rebuild:
        if tool == 'symcc':
            res = os.system("cd %s/%s && ninja" % (SCRIPT_DIR, "../../symcc/build-simple/"))
        elif tool == 'symqemu':
            res_solver = os.system("cd %s/%s && ninja" % (SCRIPT_DIR, "../../symcc/build/"))
            res_tracer = os.system("cd %s/%s && make" % (SCRIPT_DIR, "../../symqemu/"))
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
        if use_gdb:
            p_args += [ 'gdb', '-args' ]

        if tool == 'symqemu':
            p_args += [ SCRIPT_DIR + "/../../symqemu/x86_64-linux-user/symqemu-x86_64" ]
            if use_gdb:
                # p_args += [ '-d', 'in_asm,op_opt' ]
                pass

        p_args += [ exe ]
        p_args += config['args'].replace("@@", seed).split(" ")

    elif tool == 'fuzzolic':
        p_args = [
            SCRIPT_DIR + "/../../fuzzolic/fuzzolic/fuzzolic.py",
            '-i', seed,
            '-o', run_dir + "/dump" if fuzz_expr or check_inputs else run_dir,
            '-d', 'out', #'gdb_solver',
            '-k', '-l', 
            '-t', str(timeout * 1000),
            '--',
            exe
        ]
        p_args += config['args'].split(" ")
    else:
        assert False

    # print(env)
    print(' '.join(p_args))

    out_log = None
    log = None
    if count:
        out_log = tempfile.NamedTemporaryFile(prefix="debug_ce_")
        log = out_log.name
    cwd = run_dir if tool in ['symcc', 'symqemu'] else run_dir + "/../"

    start = time.time()
    p = subprocess.Popen(p_args,
                        stdout=out_log,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        cwd=cwd,
                        bufsize=0,
                        env=env)

    if use_gdb:
        gdb_cmd = "set disable-randomization off\nrun"
        p.stdin.write(gdb_cmd.encode())
        p.stdin.close()

    wait_process(p, log)

    end = time.time()
    print("\nExecution time: %.3f [return code: %d]\n" % (end - start, p.returncode))

    if count:
        if check_expr:
            # total checks
            m = subprocess.check_output(['grep', '-a', 'CHECK_EXPR', log])
            m = m.decode('unicode_escape')
            n = (len(m.split("\n")) - 1)
            print("CHECKS: %d" % n)
            # success
            m = subprocess.check_output(['grep', '-a', 'CHECK_EXPR: SUCCESS', log])
            m = m.decode('unicode_escape')
            n_ok = (len(m.split("\n")) - 1)
            print("SUCCESS: %d" % n_ok)
            print("FAILURE: %d" % (n - n_ok))
            # os.system("cp %s %s" % (log, run_dir + "/out.log"))
        if check_opt:
            # total checks
            m = subprocess.check_output(['grep', '-a', 'CHECKING OPT %s:' % ("EVAL" if check_opt == 'eval' else 'SMT'), log])
            m = m.decode('ascii')
            n = (len(m.split("\n")) - 1)
            print("CHECKS: %d" % n)
            # success
            m = subprocess.check_output(['grep', '-a', 'CHECKING OPT %s: OK' % ("EVAL" if check_opt == 'eval' else 'SMT'), log])
            m = m.decode('ascii')
            n_ok = (len(m.split("\n")) - 1)
            print("SUCCESS: %d" % n_ok)
            print("FAILURE: %d" % (n - n_ok))
        if check_pi:
            # total checks
            m = subprocess.check_output(['grep', '-a', 'CHECKING PI %s:' % ("EVAL" if check_pi == 'eval' else 'SMT'), log])
            m = m.decode('ascii')
            n = (len(m.split("\n")) - 1)
            print("CHECKS: %d" % n)
            # success
            m = subprocess.check_output(['grep', '-a', 'CHECKING PI %s: OK' % ("EVAL" if check_pi == 'eval' else 'SMT'), log])
            m = m.decode('ascii')
            n_ok = (len(m.split("\n")) - 1)
            print("SUCCESS: %d" % n_ok)
            print("FAILURE: %d" % (n - n_ok))

            # QSYM specific
            n_qsym_ko = 0
            try:
                m = subprocess.check_output(['grep', '-a', 'syncConstraints: Incorrect constraints are inserted', log])
                m = m.decode('ascii')
                n_qsym_ko = (len(m.split("\n")) - 1)
            except:
                pass
            print("QSYM FAILURE: %d" % n_qsym_ko)

    
    if out_log:
        out_log.close()

    if p.returncode == -11 or p.returncode == -6 or p.returncode == 245:
        print("ABORT DETECTED\n")
        if not(fuzz_expr or check_inputs) and abort_on_inconsistency:
            sys.exit(1)

    if fuzz_expr or check_inputs:
        seeds = glob.glob(run_dir + "/dump/" + ("fuzzolic-0*/" if tool == "fuzzolic" else "") + "%s*" % ("debug" if fuzz_expr else "input",))
        run_dir = run_dir + "/check"
        n_ok = 0
        n_unknown = 0
        n = len(seeds)
        for seed in sorted(seeds):

            if fuzz_expr:
                count = int(os.path.basename(seed).split("_")[1])
                value = int(os.path.basename(seed).split("_")[2].split('.')[0], 16)
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

            cwd = os.path.abspath(run_dir if tool in ['symcc', 'symqemu'] else run_dir + "/../")

            if os.path.exists(run_dir):
                shutil.rmtree(run_dir)
            if tool != "fuzzolic":
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

            if count:
                out_log = tempfile.NamedTemporaryFile(prefix="debug_ce_")
                log = out_log.name
            else:
                out_log = None
                log = None

            p = subprocess.Popen(p_args,
                        stdout=out_log,
                        stderr=subprocess.STDOUT,
                        stdin=subprocess.PIPE,
                        cwd=cwd,
                        bufsize=0,
                        env=env)
            
            wait_process(p, log)
            
            if not abort_on_inconsistency and count:
                if fuzz_expr:
                    e0 = 'Expression has expected value!'
                    e1 = 'Expression check has been bypassed'
                    e2 = 'Expression has wrong value'
                elif check_inputs:
                    e0 = 'Input is taking the expected direction!'
                    e1 = 'Input is divergent: it reaches the same branch but does not take the expected direction!'
                    e2 = 'Input is divergent: it does take the same path!'
                else:
                    sys.exit(1)

                try:
                    m = subprocess.check_output(['grep', e0, log])
                    m = m.decode('ascii')
                    n_ok += (len(m.split("\n")) - 1)
                except:
                    try:
                        m = subprocess.check_output(['grep', e1, log])
                    except:
                        try:
                            m = subprocess.check_output(['grep', e2, log])
                        except:
                            print("Cannot find expected pattern string!")
                            # sys.exit(1)
                            n_unknown += 1

            if out_log:
                out_log.close()

            if p.returncode == -11 or p.returncode == -6 or p.returncode == 245:
                print("Inconstency detected!")
                if abort_on_inconsistency:
                    sys.exit(1)
            else:
                if abort_on_inconsistency:
                    n_ok += 1
                    print("[%d] No inconsistency detected!\n" % p.returncode)

        end = time.time()
        print("\n\n\nExecution time: %.3f\n" % (end - start))

        if count:
            if check_inputs or fuzz_expr:
                print("INPUTS: %d" % n)
                print("SUCCESS: %d" % n_ok)
                print("UNKNOWN: %d" % n_unknown)
                print("FAILURE: %d" % (n - n_ok - n_unknown))


def main():

    programs = []
    for p in sorted(glob.glob(SCRIPT_DIR + "/0*")):
        p = os.path.basename(p)
        programs.append(p)

    parser = argparse.ArgumentParser(
        description='Run benchmarks for debug-ce')

    parser.add_argument(
        '-n', '--count', 
        help='Count checks and inconsistencies', 
        action='store_true')

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

    parser.add_argument(
        '-w', '--workdir', 
        help='Workir')

    parser.add_argument(
        '-b', '--build', 
        help='(Re)Build tool', 
        action='store_true')

    parser.add_argument(
        '-g', '--gdb', 
        help='Run under GDB', 
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

    if args.workdir is None:
        work_dir = SCRIPT_DIR + "/workdir"
    else:
        work_dir = args.workdir
    if os.path.exists(work_dir):
        if os.path.exists("%s/.fuzzolic_workdir" % work_dir):
            shutil.rmtree(work_dir)
        else:
            print("Remove %s manually!" % work_dir)
            sys.exit(1)

    os.mkdir(work_dir)
    os.system("touch %s/.fuzzolic_workdir" % work_dir)

    if args.tool in ['symcc', 'symqemu', 'fuzzolic']:
        f = False if args.cont else True
        run(args.tool, args.program, config, work_dir, check_expr=args.expr, fuzz_expr=args.fuzz, check_opt=args.opt, check_pi=args.path, check_inputs=args.input, abort_on_inconsistency=f, count=args.count, rebuild=args.build, use_gdb=args.gdb)
    else:
        print("Not yet implemented: %s" % args.tool)
        sys.exit(1)

if __name__ == "__main__":
    main()


