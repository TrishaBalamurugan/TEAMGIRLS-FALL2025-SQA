"""
MLForensics Fuzzer (FINAL — Forced constants FIX)
This version injects a dummy constants module BEFORE py_parser loads.
"""

import os
import sys
import types
import random
import traceback
import string
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------
# 1. FORCE-INJECT A DUMMY CONSTANTS MODULE
# ------------------------------------------------------
dummy_constants = types.ModuleType("constants")
sys.modules["constants"] = dummy_constants
# (If any code does "import constants", it now succeeds safely)


# ------------------------------------------------------
# 2. Loader helper (unchanged)
# ------------------------------------------------------
def load_module(name, path):
    """Load a module and register it in sys.modules."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------
# 3. Load modules NOW THAT constants is guaranteed to exist
# ------------------------------------------------------
py_parser = load_module("py_parser", os.path.join(BASE, "FAME-ML", "py_parser.py"))
frequency = load_module("frequency", os.path.join(BASE, "empirical", "frequency.py"))
report = load_module("report", os.path.join(BASE, "empirical", "report.py"))
lint_engine = load_module("lint_engine", os.path.join(BASE, "FAME-ML", "lint_engine.py"))
mining_module = load_module("mining", os.path.join(BASE, "mining", "mining.py"))


# ------------------------------------------------------
# 4. Helpers
# ------------------------------------------------------
ERROR_FILE = "fuzz_errors.txt"

def rand_str(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))

def rand_path():
    """Return real project files 50% of the time."""
    possible = []
    for folder in ["empirical", "FAME-ML", "mining"]:
        d = os.path.join(BASE, folder)
        for f in os.listdir(d):
            if f.endswith(".py"):
                possible.append(os.path.join(d, f))

    if random.random() < 0.5:
        return random.choice(possible)

    return rand_str(10) + ".txt"

def log_error(name, args, exc):
    with open(ERROR_FILE, "a") as f:
        f.write("\n-----------------------------\n")
        f.write(f"FUNCTION: {name}\nARGS    : {args}\n")
        f.write(f"ERROR   : {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

def reset_log():
    with open(ERROR_FILE, "w") as f:
        f.write("Fuzzing Errors Log\n===================\n\n")


# ------------------------------------------------------
# 5. Argument generators
# ------------------------------------------------------
def gen_args_frequency():
    return (rand_path(),)

def gen_args_report():
    return (
        {rand_str(4): random.randint(1, 100) for _ in range(random.randint(1,4))},
        rand_str(8) + ".csv"
    )

def gen_args_lint():
    return (rand_path(),)

def gen_args_parse():
    return (rand_path(),)

def gen_args_clone():
    return ("http://" + rand_str(12) + ".git", rand_str(10))


# ------------------------------------------------------
# 6. Fuzz targets
# ------------------------------------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_args_frequency),
    ("report.generateCSV", report.generateCSV, gen_args_report),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, gen_args_lint),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, gen_args_parse),
    ("mining.cloneRepo", mining_module.cloneRepo, gen_args_clone),
]


# ------------------------------------------------------
# 7. Fuzzer core
# ------------------------------------------------------
def fuzz_func(name, fn, arg_gen):
    print(f"[+] Fuzzing {name} ...")
    for _ in range(100):
        try:
            args = arg_gen()
            fn(*args)
        except Exception as e:
            log_error(name, args, e)
    print(f"[+] Done {name}")

def main():
    reset_log()
    print("[*] Starting fuzzing...\n")
    for name, fn, gen in TARGETS:
        fuzz_func(name, fn, gen)
    print("\n[*] Fuzzing finished — see fuzz_errors.txt.")


if __name__ == "__main__":
    main()
