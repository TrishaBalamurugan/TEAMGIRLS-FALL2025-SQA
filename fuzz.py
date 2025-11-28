"""
MLForensics Fuzzer (Final Version)
Works with nested folders without needing imports or __init__.py.
Uses importlib to load modules by file path.
"""

import os
import sys
import random
import traceback
import string
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    """Dynamically load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------
# Load modules DIRECTLY from your project’s file paths
# ------------------------------------------------------
frequency = load_module("frequency", os.path.join(BASE, "empirical", "frequency.py"))
report = load_module("report", os.path.join(BASE, "empirical", "report.py"))
lint_engine = load_module("lint_engine", os.path.join(BASE, "FAME-ML", "lint_engine.py"))
py_parser = load_module("py_parser", os.path.join(BASE, "FAME-ML", "py_parser.py"))
mining = load_module("mining", os.path.join(BASE, "mining", "mining.py"))


# ------------------------------------------------------
# Helper Functions
# ------------------------------------------------------
ERROR_FILE = "fuzz_errors.txt"

def rand_str(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))


def rand_path():
    """Sometimes return real files, sometimes garbage."""
    possible = []

    # empirical/
    for f in os.listdir(os.path.join(BASE, "empirical")):
        if f.endswith(".py"):
            possible.append("empirical/" + f)

    # FAME-ML/
    for f in os.listdir(os.path.join(BASE, "FAME-ML")):
        if f.endswith(".py"):
            possible.append("FAME-ML/" + f)

    # mining/
    for f in os.listdir(os.path.join(BASE, "mining")):
        if f.endswith(".py"):
            possible.append("mining/" + f)

    if random.random() < 0.5:
        return os.path.join(BASE, random.choice(possible))
    return rand_str(10) + ".txt"


def log_error(name, args, exc):
    with open(ERROR_FILE, "a") as f:
        f.write("\n-----------------------------\n")
        f.write(f"FUNCTION: {name}\n")
        f.write(f"ARGS    : {args}\n")
        f.write(f"ERROR   : {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ))


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

    print("\n[*] Fuzzing finished — see fuzz_errors.txt for results.")


if __name__ == "__main__":
    main()
