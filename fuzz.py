"""
Final Fuzzer for TEAMGIRLS-FALL2025-SQA
This version FIXES py_parser import errors by adding forensics/ to sys.path.
"""

import os
import sys
import random
import traceback
import string
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
FORENSICS = os.path.join(BASE, "forensics")

# ------------------------------------------------------
# FIX: ensure all /forensics modules can import each other
# ------------------------------------------------------
sys.path.append(FORENSICS)


def load_module(name, filename):
    """Load a module from forensics/ directory."""
    path = os.path.join(FORENSICS, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------
# Load modules from /forensics
# ------------------------------------------------------
frequency = load_module("frequency", "frequency.py")
lint_engine = load_module("lint_engine", "lint_engine.py")
mining_mod = load_module("mining_mod", "mining.py")
gitminer = load_module("gitminer", "git.repo.miner.py")
py_parser = load_module("py_parser", "py_parser.py")


# ------------------------------------------------------
# Helpers
# ------------------------------------------------------
ERROR_FILE = "fuzz_errors.txt"

def rand_str(n=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))

def rand_path():
    return rand_str(8) + ".txt"

def rand_url():
    return "http://" + rand_str(10) + ".git"

def log_error(name, args, exc):
    with open(ERROR_FILE, "a") as f:
        f.write("\n---------------------------------\n")
        f.write(f"FUNCTION: {name}\n")
        f.write(f"ARGS: {args}\n")
        f.write(f"ERROR: {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


def reset_log():
    with open(ERROR_FILE, "w") as f:
        f.write("Fuzz Testing Errors\n====================\n")


# ------------------------------------------------------
# Argument Generators
# ------------------------------------------------------
def gen_freq():
    return (rand_path(),)

def gen_lint():
    return (rand_path(),)

def gen_parse():
    return (rand_path(),)

def gen_clone():
    return (rand_url(), rand_str(6))

def gen_git():
    return (rand_path(),)


# Pick first callable in gitminer
git_fn = None
for n, v in gitminer.__dict__.items():
    if callable(v):
        git_fn = v
        break


# ------------------------------------------------------
# Fuzz Targets
# ------------------------------------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_freq),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, gen_lint),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, gen_parse),
    ("mining.cloneRepo", mining_mod.cloneRepo, gen_clone),
    ("gitminer.<function>", git_fn, gen_git),
]


# ------------------------------------------------------
# Fuzz Loop
# ------------------------------------------------------
def fuzz(name, fn, gen):
    print(f"[+] Fuzzing {name} ...")
    for _ in range(50):
        try:
            args = gen()
            fn(*args)
        except Exception as e:
            log_error(name, args, e)
    print(f"[+] Done {name}")


def main():
    reset_log()
    print("[*] Starting fuzzing...\n")

    for name, fn, gen in TARGETS:
        fuzz(name, fn, gen)

    print("\n[*] Fuzzing complete. See fuzz_errors.txt.")


if __name__ == "__main__":
    main()
