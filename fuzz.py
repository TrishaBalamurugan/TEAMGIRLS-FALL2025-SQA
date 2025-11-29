"""
Ultra-simple fuzz.py
Works without modifying ANY source files.
Makes the forensics folder behave like a package in memory.
"""

import os
import sys
import random
import string
import traceback
import importlib.util
import types

BASE = os.path.dirname(os.path.abspath(__file__))
FORENSICS = os.path.join(BASE, "forensics")

# ---------------------------------------------------------
# Make "forensics" behave like a real package (no file edits)
# ---------------------------------------------------------
pkg = types.ModuleType("forensics")
pkg.__path__ = [FORENSICS]
sys.modules["forensics"] = pkg

# Stub missing forensics.constants so py_parser can import it
const = types.ModuleType("forensics.constants")
sys.modules["forensics.constants"] = const
sys.modules["constants"] = const   # fallback import

def load(name, filename):
    """Load a module and register it under package + top level."""
    path = os.path.join(FORENSICS, filename)
    full = f"forensics.{name}"

    spec = importlib.util.spec_from_file_location(full, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # register both names so imports succeed
    sys.modules[full] = mod
    sys.modules[name] = mod
    return mod

# ---------------------------------------------------------
# Load required modules (NOW THEY WILL IMPORT CLEANLY)
# ---------------------------------------------------------
frequency   = load("frequency", "frequency.py")
py_parser   = load("py_parser", "py_parser.py")
lint_engine = load("lint_engine", "lint_engine.py")
mining      = load("mining", "mining.py")
gitminer    = load("git_repo_miner", "git.repo.miner.py")

# Pick first callable in gitminer
git_fn = next(v for v in gitminer.__dict__.values() if callable(v))

# ---------------------------------------------------------
# Simple fuzzing helpers
# ---------------------------------------------------------
def rstr(n=12):
    return ''.join(random.choice(string.ascii_letters) for _ in range(n))

def rpath():
    return rstr(8) + ".txt"

def rurl():
    return "http://" + rstr(12) + ".git"

def log_error(name, args, exc):
    with open("fuzz_errors.txt", "a") as f:
        f.write(f"\n--- {name} ---\nArgs: {args}\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

# ---------------------------------------------------------
# Targets (5 total, required by assignment)
# ---------------------------------------------------------
TARGETS = [
    ("frequency.getFrequencies", frequency.getFrequencies, lambda: (rpath(),)),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, lambda: (rpath(),)),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, lambda: (rpath(),)),
    ("mining.cloneRepo", mining.cloneRepo, lambda: (rurl(), rstr(6))),
    ("gitminer.fn", git_fn, lambda: (rpath(),)),
]

# ---------------------------------------------------------
# Run fuzzer
# ---------------------------------------------------------
def fuzz(name, fn, gen):
    print(f"[+] Fuzzing {name}")
    for _ in range(25):
        try:
            args = gen()
            fn(*args)
        except Exception as e:
            log_error(name, args, e)

def main():
    open("fuzz_errors.txt", "w").write("Fuzzing Errors\n==============\n")
    for name, fn, gen in TARGETS:
        fuzz(name, fn, gen)
    print("\n[*] Done. See fuzz_errors.txt")

if __name__ == "__main__":
    main()
