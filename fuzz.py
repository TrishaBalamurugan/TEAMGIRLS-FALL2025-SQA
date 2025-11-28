"""
Clean Working Fuzzer for MLForensics-farzana
This version supports subfolders without needing __init__.py
"""

import os
import sys
import random
import traceback
import string

# -----------------------------
# Add subfolders to Python path
# -----------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE, "empirical"))
sys.path.append(os.path.join(BASE, "FAME-ML"))
sys.path.append(os.path.join(BASE, "mining"))

# -----------------------------
# Import modules from folders
# -----------------------------
import frequency              # empirical/
import report                 # empirical/
import lint_engine            # FAME-ML/
import py_parser              # FAME-ML/
import mining                 # mining/

# -----------------------------
# Helper functions
# -----------------------------
OUTFILE = "fuzz_errors.txt"

def rand_str(n=20):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(n))

def rand_path():
    possible = [
        "empirical/" + f for f in os.listdir(os.path.join(BASE, "empirical"))
        if f.endswith(".py")
    ] + [
        "FAME-ML/" + f for f in os.listdir(os.path.join(BASE, "FAME-ML"))
        if f.endswith(".py")
    ] + [
        "mining/" + f for f in os.listdir(os.path.join(BASE, "mining"))
        if f.endswith(".py")
    ]

    if random.random() < 0.5:
        return random.choice(possible)
    return rand_str(10) + ".txt"

def log_error(name, args, exc):
    with open(OUTFILE, "a") as f:
        f.write("\n-----------------------------\n")
        f.write(f"FUNCTION: {name}\n")
        f.write(f"ARGS    : {args}\n")
        f.write(f"ERROR   : {type(exc).__name__}: {exc}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

def reset_log():
    with open(OUTFILE, "w") as f:
        f.write("Fuzzing Errors Log\n===================\n\n")

# -----------------------------
# Argument generators
# -----------------------------
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
    # fuzz unsafe repo URL patterns
    return ("http://" + rand_str(10) + ".git", rand_str(8))

# -----------------------------
# Functions to fuzz
# -----------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, gen_args_frequency),
    ("report.generateCSV", report.generateCSV, gen_args_report),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, gen_args_lint),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, gen_args_parse),
    ("mining.cloneRepo", mining.cloneRepo, gen_args_clone),
]

# -----------------------------
# Fuzzing loop
# -----------------------------
def fuzz_func(name, fn, arg_gen):
    print(f"[+] Fuzzing {name} ...")
    for _ in range(100):
        try:
            args = arg_gen()
            fn(*args)
        except Exception as e:
            log_error(name, args, e)
    print(f"[+] Done with {name}")

def main():
    reset_log()
    print("[*] Starting fuzzing...\n")
    for name, fn, gen in TARGETS:
        fuzz_func(name, fn, gen)
    print("\n[*] Fuzzing finished. Check fuzz_errors.txt.")

if __name__ == "__main__":
    main()
