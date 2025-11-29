# test_logging_mining.py
import logging

# -----------------------------
# Configure root logger BEFORE importing mining
# -----------------------------
log_file = 'forensics_mining.log'
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import mining
from datetime import datetime, timedelta

print("=== Testing giveTimeStamp ===")
ts = mining.giveTimeStamp()
print("Timestamp:", ts)
logging.info(f"giveTimeStamp returned: {ts}")

print("\n=== Testing dumpContentIntoFile ===")
test_file = 'test_file.txt'
size_written = mining.dumpContentIntoFile("Hello World", test_file)
print("Written size:", size_written)
logging.info(f"dumpContentIntoFile wrote {size_written} bytes to {test_file}")

print("\n=== Testing makeChunks ===")
chunks = list(mining.makeChunks(list(range(10)), 3))
print("Chunks:", chunks)
logging.info(f"makeChunks returned: {chunks}")

print("\n=== Testing getPythonFileCount on current dir ===")
python_count = mining.getPythonFileCount('.')
print("Python file count:", python_count)
logging.info(f"getPythonFileCount returned: {python_count}")

print("\n=== Testing days_between ===")
d1 = datetime.now()
d2 = d1 + timedelta(days=30)
days = mining.days_between(d1, d2)
print("Days between:", days)
logging.info(f"days_between returned: {days}")

print("\n=== Testing deleteRepo ===")
dummy_dir = 'dummy_delete_test'
os.makedirs(dummy_dir, exist_ok=True)
mining.deleteRepo(dummy_dir, 'TEST_DELETE')
logging.info(f"deleteRepo called on {dummy_dir}")

print("\n=== All tests completed. Check", log_file, "for details ===")

