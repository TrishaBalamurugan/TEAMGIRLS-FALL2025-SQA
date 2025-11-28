"""
MLForensics Fuzzer (FINAL IMPORT FIX)
Ensures py_parser is loaded FIRST and registered as 'py_parser'
so FAME-ML/lint_engine.py can import it.
"""

import os
import sys
import random
import traceback
import string
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))


def load_module(name, path):
    """Load a module from a file path AND register it so internal imports work."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module        # <-- CRITICAL
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------
# LOAD py_parser FIRST (lint_engine depends on it)
# ------------------------------------------------------
py_parser = load_module("py_parser", os.path.join(BASE, "FAME-ML", "py_parser.py"))

# ------------------------------------------------------
# Load remaining modules
# ------------------------------------------------------
frequency = load_module("frequency", os.path.join(BASE, "empirical", "frequency.py"))
report = load_module("report", os.path.join(BASE, "empirical", "report.py"))

lint_engine = load_module("lint_engine", os.path.join(BASE, "FAME-ML", "lint_engine.py"))

mining = load_module("mining", os.path.join(BASE, "mining", "mining.py"))


# ------------------------------------------------------
# Helper Functions
# ------------------------------------------------------
ERROR_FILE = "fuzz_errors.txt"

def rand_str(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))


def rand_path():
    """Sometimes return real files, sometimes random garbage."""
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
        f.write(f"FUNCTION: {name}\n")
        f.write(f"ARGS    : {args}\n")
        f.write(f"ERROR   : {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


def reset_log():
    with open(ERROR_FILE, "w") as f:
        f.write("Fuzzing Errors Log\n===================\n\n")


# ------------------------------------------------------
# Argument Generators
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
    return ("http://" + rand_str(10) + ".git", rand_str(8))


# ------------------------------------------------------
# Fuzz Targets
# ------------------------------------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_args_frequency),
    ("report.generateCSV", report.generateCSV, gen_args_report),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, gen_args_lint),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, gen_args_parse),
    ("mining.cloneRepo", mining.cloneRepo, gen_args_clone),
]


# ------------------------------------------------------
# Fuzz Loop
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
