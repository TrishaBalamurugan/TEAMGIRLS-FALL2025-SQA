"""
Fuzz tester for MLForensics

Targets (5 functions):
  1. frequency.reportProportion(res_file, fields2explore)
  2. dataset_stats.getGeneralStats(repo_csv_file)
  3. py_parser.getPythonParseObject(py_file)
  4. git_repo_miner.getMLStats(res_file)
  5. lint_engine.getDataLoadCount(py_file)

This script:
  - Generates random and edge-case inputs
  - Calls each target function many times
  - Catches and logs all exceptions into fuzz_errors.txt

It is designed to be run locally and from GitHub Actions:
  python fuzz.py
"""

import random
import traceback
import json
import os
import string
from typing import Any, List, Tuple

# -------------------------
# Try to use Big List of Naughty Strings (BLNS) if available
# -------------------------
try:
    # pip install blns
    from blns import blns as BLNS  # type: ignore
except Exception:
    # Fallback: a small built-in naughty set
    BLNS = [
        "",
        "null",
        "None",
        "NaN",
        "\n",
        "\t",
        "💣",
        "𝔘𝔫𝔦𝔠𝔬𝔡𝔢",
        "\"; DROP TABLE users;--",
        "${7*7}",
        "../../../../../etc/passwd",
    ]

# -------------------------
# Import the project modules
# Adjust names if your repo layout differs
# -------------------------
import frequency
import dataset_stats      # expected file: dataset_stats.py (or rename dataset.stats.py)
import py_parser
import git_repo_miner    # expected file: git_repo_miner.py (or rename git.repo.miner.py)
import lint_engine


# -------------------------
# Known file-like targets in the repo for "semi-valid" paths
# (these help produce more interesting crashes than only FileNotFoundError)
# -------------------------
KNOWN_PY_FILES = [
    "main.py",
    "frequency.py",
    "lint_engine.py",
    "py_parser.py",
    "mining.py",
    "log.op.miner.py",
    "git.repo.miner.py",
    "dataset.stats.py",
]

KNOWN_RESULT_FILES = [
    "RQ1_RES.csv",
    "RQ2_RES.csv",
    "ML_STATS.csv",
    "DATASET_STATS.csv",
]

FIELDS2EXPLORE_DEFAULT = [
    "DATA_LOAD_COUNT", "MODEL_LOAD_COUNT", "DATA_DOWNLOAD_COUNT",
    "MODEL_LABEL_COUNT", "MODEL_OUTPUT_COUNT",
    "DATA_PIPELINE_COUNT", "ENVIRONMENT_COUNT", "STATE_OBSERVE_COUNT",
    "TOTAL_EVENT_COUNT",
]


# -------------------------
# Generic value generators
# -------------------------

def random_ascii_string(min_len: int = 0, max_len: int = 40) -> str:
    length = random.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits + string.punctuation + " "
    return "".join(random.choice(chars) for _ in range(length))


def generate_path_like() -> str:
    """
    Generate something that looks like a path:
      - a known repo file (sometimes)
      - a known "results" CSV (sometimes)
      - totally random garbage (sometimes)
    """
    kind = random.randint(0, 3)
    if kind == 0 and KNOWN_PY_FILES:
        return random.choice(KNOWN_PY_FILES)
    if kind == 1 and KNOWN_RESULT_FILES:
        return random.choice(KNOWN_RESULT_FILES)
    if kind == 2:
        return "./" + random_ascii_string(3, 12) + random.choice([".py", ".csv", ".txt"])
    # very malformed path
    return random.choice(BLNS)


def generate_basic_value() -> Any:
    """
    Generate a primitive/collection value used for fuzzing.
    """
    choice = random.randint(0, 7)
    if choice == 0:
        return random.randint(-10**9, 10**9)
    if choice == 1:
        return random.uniform(-1e9, 1e9)
    if choice == 2:
        return random.choice(BLNS)
    if choice == 3:
        return random_ascii_string()
    if choice == 4:
        return None
    if choice == 5:
        return [generate_basic_value() for _ in range(random.randint(0, 5))]
    if choice == 6:
        return {random_ascii_string(1, 5): generate_basic_value()
                for _ in range(random.randint(0, 4))}
    return bool(random.getrandbits(1))


# -------------------------
# Function-specific argument generators
# -------------------------

def gen_args_reportProportion() -> Tuple[Any, Any]:
    """
    frequency.reportProportion(res_file, fields2explore)
    """
    # res_file: often a CSV path
    res_file = generate_path_like()

    # fields2explore: usually a list of field names
    if random.random() < 0.6:
        fields = FIELDS2EXPLORE_DEFAULT
    else:
        # Garbage / mixed list
        fields = [
            random.choice(FIELDS2EXPLORE_DEFAULT + [random_ascii_string(3, 10)])
            for _ in range(random.randint(0, 8))
        ]
    return res_file, fields


def gen_args_getGeneralStats() -> Tuple[Any]:
    """
    dataset_stats.getGeneralStats(repo_csv_file)
    """
    # Usually a repo list CSV, but we deliberately give both valid-ish and junk
    if random.random() < 0.5:
        return (generate_path_like(),)
    else:
        return (generate_basic_value(),)


def gen_args_getPythonParseObject() -> Tuple[Any]:
    """
    py_parser.getPythonParseObject(py_file)
    """
    if random.random() < 0.7:
        # more likely to be a .py-ish path so we hit AST/parsing logic
        return (generate_path_like(),)
    else:
        return (generate_basic_value(),)


def gen_args_getMLStats() -> Tuple[Any]:
    """
    git_repo_miner.getMLStats(res_file)
    """
    if random.random() < 0.6:
        return (generate_path_like(),)
    else:
        return (generate_basic_value(),)


def gen_args_getDataLoadCount() -> Tuple[Any]:
    """
    lint_engine.getDataLoadCount(py_file)
    """
    if random.random() < 0.7:
        return (generate_path_like(),)
    else:
        return (generate_basic_value(),)


# -------------------------
# Target function registry
# -------------------------

TARGETS = [
    ("frequency.reportProportion",
     frequency.reportProportion,
     gen_args_reportProportion),

    ("dataset_stats.getGeneralStats",
     dataset_stats.getGeneralStats,
     gen_args_getGeneralStats),

    ("py_parser.getPythonParseObject",
     py_parser.getPythonParseObject,
     gen_args_getPythonParseObject),

    ("git_repo_miner.getMLStats",
     git_repo_miner.getMLStats,
     gen_args_getMLStats),

    ("lint_engine.getDataLoadCount",
     lint_engine.getDataLoadCount,
     gen_args_getDataLoadCount),
]


# -------------------------
# Logging helpers
# -------------------------

ERROR_LOG_FILE = "fuzz_errors.txt"


def log_error(target_name: str, args: Tuple[Any, ...], exc: Exception) -> None:
    """
    Append a structured error record to fuzz_errors.txt.
    """
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"TARGET   : {target_name}\n")
        f.write(f"ARGS     : {repr(args)}\n")
        f.write(f"EXC TYPE : {type(exc).__name__}\n")
        f.write(f"EXC MSG  : {str(exc)}\n")
        f.write("TRACEBACK:\n")
        f.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
        f.write("\n")


def reset_error_log() -> None:
    """
    Truncate fuzz_errors.txt at the start of a run.
    """
    with open(ERROR_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("MLForensics fuzzing error log\n")
        f.write("================================\n\n")


# -------------------------
# Main fuzzing loop
# -------------------------

def fuzz_target(target_name: str, func, arg_gen, iterations: int = 200) -> None:
    """
    Fuzz a single function.

    :param target_name: human-readable name of the target
    :param func:        the callable to fuzz
    :param arg_gen:     a callable returning a tuple of arguments
    :param iterations:  how many fuzzing iterations to run
    """
    print(f"[+] Fuzzing {target_name} for {iterations} iterations...")
    crashes = 0

    for i in range(iterations):
        args = arg_gen()
        try:
            _ = func(*args)
        except Exception as exc:
            crashes += 1
            log_error(target_name, args, exc)

    print(f"[+] Done fuzzing {target_name}: {crashes} exceptions recorded.")


def main() -> None:
    reset_error_log()
    print("[*] Starting MLForensics fuzzing session...")
    random.seed()  # use system randomness

    for target_name, func, arg_gen in TARGETS:
        fuzz_target(target_name, func, arg_gen, iterations=200)

    print("[*] Fuzzing complete. See fuzz_errors.txt for details.")


if __name__ == "__main__":
    main()

