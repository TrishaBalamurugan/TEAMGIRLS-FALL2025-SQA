"""
Simplified Fuzzer for MLForensics (NO CONSTANTS, NO logminer, NO FAME-ML)
We fuzz ONLY modules that import cleanly.
"""

import os
import sys
import random
import traceback
import string
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))

def load_module(name, path):
    """Load a Python module directly from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------
# Load safe modules ONLY (no constants, no FAME-ML)
# ------------------------------------------------------
frequency = load_module("frequency", os.path.join(BASE, "empirical", "frequency.py"))
report = load_module("report", os.path.join(BASE, "empirical", "report.py"))
mining_mod = load_module("mining_mod", os.path.join(BASE, "mining", "mining.py"))
gitminer = load_module("gitminer", os.path.join(BASE, "mining", "git.repo.miner.py"))


# ------------------------------------------------------
# Helper functions
# ------------------------------------------------------
ERROR_FILE = "fuzz_errors.txt"

def rand_str(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))

def rand_path():
    return rand_str(8) + ".txt"

def rand_url():
    return "http://" + rand_str(10) + ".git"

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
# Argument Generators
# ------------------------------------------------------
def gen_frequency():
    return (rand_path(),)

def gen_report():
    d = {rand_str(4): random.randint(1, 100) for _ in range(3)}
    return (d, rand_str(8) + ".csv")

def gen_clone():
    return (rand_url(), rand_str(6))

def gen_gitminer():
    return (rand_path(),)

def gen_mining_extra():
    return (rand_url(), rand_str(6))


# ------------------------------------------------------
# Choose callable from gitminer safely
# ------------------------------------------------------
gitminer_fn = None
for name, value in gitminer.__dict__.items():
    if callable(value):
        gitminer_fn = value
        break

if gitminer_fn is None:
    raise RuntimeError("No callable found in git.repo.miner.py")


# ------------------------------------------------------
# Build fuzz targets
# ------------------------------------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_frequency),
    ("report.generateCSV", report.generateCSV, gen_report),
    ("mining.cloneRepo", mining_mod.cloneRepo, gen_clone),
    ("gitminer.<function>", gitminer_fn, gen_gitminer),
    ("mining.cloneRepo (extra)", mining_mod.cloneRepo, gen_mining_extra),
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

    print("\n[*] Fuzzing finished. Check fuzz_errors.txt")


if __name__ == "__main__":
    main()
