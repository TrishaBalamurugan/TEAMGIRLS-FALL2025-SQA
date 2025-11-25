import os
import logging
import pandas as pd
from empirical import frequency

# -----------------------------
# Setup dedicated logger
# -----------------------------
logger = logging.getLogger('frequency_logger')
logger.setLevel(logging.INFO)

log_file = 'forensics_frequency.log'
fh = logging.FileHandler(log_file)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(fh)

print("=== Testing giveTimeStamp ===")
ts = frequency.giveTimeStamp()
print("Timestamp:", ts)
logger.info(f"giveTimeStamp returned: {ts}")

print("\n=== Testing getAllSLOC with dummy files ===")
dummy_dir = 'dummy_sloc_test'
os.makedirs(dummy_dir, exist_ok=True)
dummy_files = [os.path.join(dummy_dir, f'file{i}.py') for i in range(3)]
for idx, f in enumerate(dummy_files):
    with open(f, 'w') as fh_dummy:
        fh_dummy.write("print('Hello World')\n" * (idx + 1))  # 1,2,3 lines

# Create dummy dataframe for getAllSLOC
df_dummy = pd.DataFrame({'FILE_FULL_PATH': dummy_files})
total_sloc = frequency.getAllSLOC(df_dummy)
print("Total SLOC:", total_sloc)
logger.info(f"getAllSLOC returned: {total_sloc}")

# Cleanup dummy files
for f in dummy_files:
    os.remove(f)
os.rmdir(dummy_dir)

print("\n=== Testing reportProportion and reportEventDensity with dummy CSV ===")
dummy_csv = 'dummy_results.csv'
proportion_csv = 'dummy_proportion.csv'
density_csv = 'dummy_density.csv'

# Create dummy CSV data
dummy_data = {
    'REPO_FULL_PATH': ['repo1', 'repo1', 'repo2'],
    'FILE_FULL_PATH': ['file1.py', 'file2.py', 'file3.py'],
    'DATA_LOAD_COUNT': [1,0,2],
    'MODEL_LOAD_COUNT': [0,0,1],
    'DATA_DOWNLOAD_COUNT':[1,0,0],
    'MODEL_LABEL_COUNT':[0,1,0],
    'MODEL_OUTPUT_COUNT':[1,0,0],
    'DATA_PIPELINE_COUNT':[0,0,0],
    'ENVIRONMENT_COUNT':[0,0,0],
    'STATE_OBSERVE_COUNT':[1,0,0],
    'TOTAL_EVENT_COUNT':[3,1,3]
}
df_dummy_csv = pd.DataFrame(dummy_data)
df_dummy_csv.to_csv(dummy_csv, index=False)

# Test reportProportion
frequency.reportProportion(dummy_csv, proportion_csv)
logger.info(f"reportProportion ran and output saved to {proportion_csv}")

# Test reportEventDensity
frequency.reportEventDensity(dummy_csv, density_csv)
logger.info(f"reportEventDensity ran and output saved to {density_csv}")

# Cleanup dummy CSV files
os.remove(dummy_csv)
os.remove(proportion_csv)
os.remove(density_csv)

print("\n=== All tests completed. Check", log_file, "for details ===")

