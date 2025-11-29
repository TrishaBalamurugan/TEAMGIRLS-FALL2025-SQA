"""
Guaranteed working fuzz.py
Loads py_parser FIRST so lint_engine can import it.
Mocks numpy/pandas/git, no project modifications needed.
"""

import os, sys, random, string, traceback, importlib.util, types

BASE = os.path.dirname(os.path.abspath(__file__))
FORENSICS = os.path.join(BASE, "forensics")

# ---------------------------------------------------------
# MOCK numpy
# ---------------------------------------------------------
fake_np = types.ModuleType("numpy")
fake_np.array = lambda *a, **k: a
fake_np.mean = fake_np.std = fake_np.var = (lambda *a, **k: 0)
sys.modules["numpy"] = fake_np
sys.modules["np"] = fake_np

# ---------------------------------------------------------
# MOCK pandas
# ---------------------------------------------------------
fake_pd = types.ModuleType("pandas")
fake_pd.read_csv = lambda *a, **k: []
fake_pd.DataFrame = lambda *a, **k: []
sys.modules["pandas"] = fake_pd
sys.modules["pd"] = fake_pd

# ---------------------------------------------------------
# MOCK git and git.exc
# ---------------------------------------------------------
fake_git = types.ModuleType("git")

class FakeRepo:
    def __init__(self, *a, **k): pass
    def clone_from(self, *a, **k): pass

fake_git.Repo = FakeRepo

fake_exc = types.ModuleType("git.exc")
fake_exc.GitError = Exception
fake_git.exc = fake_exc

sys.modules["git"] = fake_git
sys.modules["git.exc"] = fake_exc

# ---------------------------------------------------------
# Make the forensics folder a pseudo-package
# ---------------------------------------------------------
pkg = types.ModuleType("forensics")
pkg.__path__ = [FORENSICS]
sys.modules["forensics"] = pkg

# fake constants
const = types.ModuleType("forensics.constants")
sys.modules["constants"] = const
sys.modules["forensics.constants"] = const

# ---------------------------------------------------------
# Loader
# ---------------------------------------------------------
def load(name, filename):
    """Load module from forensics/ and register names."""
    path = os.path.join(FORENSICS, filename)
    full = f"forensics.{name}"

    spec = importlib.util.spec_from_file_location(full, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # populate sys.modules under many aliases
    sys.modules[full] = mod
    sys.modules[name] = mod
    return mod

# ---------------------------------------------------------
# LOAD py_parser FIRST (critical)
# ---------------------------------------------------------
py_parser = load("py_parser", "py_parser.py")

# register EVERY possible import alias BEFORE loading lint_engine
sys.modules["py_parser"] = py_parser
sys.modules["forensics.py_parser"] = py_parser

# ---------------------------------------------------------
# NOW load the rest
# ---------------------------------------------------------
frequency   = load("frequency", "frequency.py")
lint_engine = load("lint_engine", "lint_engine.py")
mining      = load("mining", "mining.py")
gitminer    = load("gitminer", "git.repo.miner.py")

git_fn = next(v for v in gitminer.__dict__.values() if callable(v))

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def rstr(n=10): return ''.join(random.choice(string.ascii_letters) for _ in range(n))
def rpath(): return rstr(8) + ".txt"
def rurl(): return "http://" + rstr(12) + ".git"
def rlist(): return [random.randint(0, 50) for _ in range(random.randint(2, 10))]

def log_error(name, args, exc):
    with open("fuzz_errors.txt", "a") as f:
        f.write(f"\n--- {name} ---\nArgs={args}\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))

# ---------------------------------------------------------
# SAFE real functions
# ---------------------------------------------------------
TARGETS = [
    ("frequency.giveTimeStamp", frequency.giveTimeStamp, lambda: ()),
    ("lint_engine.getDataLoadCount", lint_engine.getDataLoadCount, lambda: (rpath(),)),
    ("py_parser.getPythonParseObject", py_parser.getPythonParseObject, lambda: (rpath(),)),
    ("mining.dumpContentIntoFile", mining.dumpContentIntoFile, lambda: (rstr(20), rpath())),
    ("gitminer.makeChunks", gitminer.makeChunks, lambda: (rlist(), random.randint(1, 5))),
]

# ---------------------------------------------------------
# Fuzz loop
# ---------------------------------------------------------
def fuzz(name, fn, gen):
    print(f"[+] Fuzzing {name}")
    for _ in range(20):
        try:
            args = gen()
            fn(*args)
        except Exception as e:
            log_error(name, args, e)

def main():
    open("fuzz_errors.txt", "w").write("Fuzzing Errors\n==============\n")
    for name, fn, gen in TARGETS:
        fuzz(name, fn, gen)
    print("\n[*] Complete — see fuzz_errors.txt")

if __name__ == "__main__":
    main()
