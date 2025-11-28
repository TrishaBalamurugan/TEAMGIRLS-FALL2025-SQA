"""
MLForensics Fuzzer - Clean Version (No invalid dotted modules)

This version ONLY uses modules with valid Python import names.

Fuzz targets:
  1. frequency.getFrequencies(file_path)
  2. report.generateCSV(res_dict, out_file)
  3. lint_engine.getDataLoadCount(py_file)
  4. py_parser.getPythonParseObject(py_file)
  5. mining.cloneRepo(repo_url, dest_folder)

All crashes will be logged to fuzz_errors.txt
"""

import os
import sys
import random
import traceback
import string

# Ensure project root is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import ONLY valid modules
import frequency
import report
import lint_engine
import py_parser
import mining    # this exists in your uploaded files


# ----------------------------
# Helpers
# ----------------------------

ERROR_FILE = "fuzz_errors.txt"

def rand_string(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))

def rand_path():
    """Sometimes return a real file, sometimes garbage."""
    files = [
        "main.py", "frequency.py", "report.py", "py_parser.py",
        "lint_engine.py", "mining.py"
    ]
    if random.random() < 0.5:
        return random.choice(files)
    return rand_string(8) + ".txt"

def log_error(name, args, exc):
    with open(ERROR_FILE, "a") as f:
        f.write("\n====================================\n")
        f.write(f"FUNC: {name}\n")
        f.write(f"ARGS: {args}\n")
        f.write(f"ERROR: {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        f.write("\n")

def reset_log():
    with open(ERROR_FILE, "w") as f:
        f.write("Fuzzing Errors\n===============\n")


# ----------------------------
# Argument Generators
# ----------------------------

def gen_args_getFrequencies():
    return (rand_path(),)

def gen_args_generateCSV():
    random_dict = {
        rand_string(4): random.randint(0, 100)
        for _ in range(random.randint(1, 5))
    }
    out_file = rand_string(6) + ".csv"
    return (random_dict, out_file)

def gen_args_getDataLoadCount():
    return (rand_path(),)

def gen_args_getPythonParseObject():
    return (rand_path(),)

def gen_args_cloneRepo():
    url = "http://" + rand_string(10) + ".com/repo.git"
    dest = rand_string(8)
    return (url, dest)


# ----------------------------
# Targets
# ----------------------------

TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_args_getFrequencies),
    ("report.generateCSV", report.generateCSV, gen_args_generateCSV),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, gen_args_getDataLoadCount),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, gen_args_getPythonParseObject),
    ("mining.cloneRepo", mining.cloneRepo, gen_args_cloneRepo),
]


# ----------------------------
# Main Fuzzer Loop
# ----------------------------

def fuzz_function(name, func, arg_gen, iterations=100):
    print(f"[+] Fuzzing {name} ...")
    for _ in range(iterations):
        args = arg_gen()
        try:
            func(*args)
        except Exception as e:
            log_error(name, args, e)
    print(f"[+] Finished {name}")

def main():
    reset_log()
    print("[*] Starting fuzzing run...\n")

    for name, func, gen in TARGETS:
        fuzz_function(name, func, gen)

    print("\n[*] Done. Check fuzz_errors.txt for results.")

if __name__ == "__main__":
    main()
