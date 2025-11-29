import subprocess
import sys
import os

print("*" * 50)
print("Starting local CI runner")
print("*" * 50)
print()

# List of tests to run (relative paths)
tests = [
    "forensics/test_logging_frequency.py",
    "forensics/test_logging_mining.py",
    "forensics/test_logging_py_parser.py"
]

def run_test(test_path):
    print(f"Running {test_path}...\n")

    result = subprocess.run(
        ["python3", test_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        print(f"❌ {test_path} failed!")
        return False
    
    print(f"✅ {test_path} passed!\n")
    return True


all_passed = True

for test in tests:
    ok = run_test(test)
    if not ok:
        all_passed = False

print("*" * 50)
if all_passed:
    print("All tests passed successfully!")
else:
    print("Some tests failed! Check logs.")
print("*" * 50)
