'''
Akond Rahman 
Nov 15, 2020
Frequency: RQ2
'''
import numpy as np
import os
import pandas as pd
import time
import datetime
import logging

# ----------------------------
# Configure Forensics Logging
# ----------------------------
logging.basicConfig(
    filename='forensics_frequency.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ----------------------------
# MLForensics Frequency Functions
# ----------------------------

def giveTimeStamp():
    tsObj = time.time()
    strToret = datetime.datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Timestamp generated: {strToret}")
    return strToret

def getAllSLOC(df_param, csv_encoding='latin-1'):
    logging.info("Calculating total SLOC from dataframe")
    total_sloc = 0
    all_files = np.unique(df_param['FILE_FULL_PATH'].tolist())
    for file_ in all_files:
        try:
            total_sloc += sum(1 for line in open(file_, encoding=csv_encoding))
        except Exception as e:
            logging.error(f"Error reading file {file_}: {e}")
    logging.info(f"Total SLOC calculated: {total_sloc}")
    return total_sloc

def reportProportion(res_file, output_file):
    logging.info(f"Generating proportion report from {res_file}")
    res_df = pd.read_csv(res_file)
    repo_names = np.unique(res_df['REPO_FULL_PATH'].tolist())
    
    fields2explore = ['DATA_LOAD_COUNT', 'MODEL_LOAD_COUNT', 'DATA_DOWNLOAD_COUNT',
                      'MODEL_LABEL_COUNT', 'MODEL_OUTPUT_COUNT', 'DATA_PIPELINE_COUNT',
                      'ENVIRONMENT_COUNT', 'STATE_OBSERVE_COUNT', 'TOTAL_EVENT_COUNT']
    df_list = []

    for repo in repo_names:
        logging.info(f"Processing repo: {repo}")
        repo_entity = res_df[res_df['REPO_FULL_PATH'] == repo]
        all_py_files = np.unique(repo_entity['FILE_FULL_PATH'].tolist())
        for field in fields2explore:
            field_atleast_one_df = repo_entity[repo_entity[field] > 0]
            atleast_one_files = np.unique(field_atleast_one_df['FILE_FULL_PATH'].tolist())
            prop_metric = round(len(atleast_one_files) / len(all_py_files), 5) * 100
            logging.info(f"{repo} | Field: {field} | Total Files: {len(all_py_files)} | At least one: {len(atleast_one_files)} | Proportion: {prop_metric}")
            df_list.append((repo, len(all_py_files), field, len(atleast_one_files), prop_metric))
    
    CSV_HEADER = ['REPO_NAME', 'TOTAL_FILES', 'CATEGORY', 'ATLEASTONE', 'PROP_VAL']
    full_df = pd.DataFrame(df_list)
    full_df.to_csv(output_file, header=CSV_HEADER, index=False, encoding='utf-8')
    logging.info(f"Proportion report saved to {output_file}")

def reportEventDensity(res_file, output_file):
    logging.info(f"Generating event density report from {res_file}")
    res_df = pd.read_csv(res_file)
    repo_names = np.unique(res_df['REPO_FULL_PATH'].tolist())
    
    fields2explore = ['DATA_LOAD_COUNT', 'MODEL_LOAD_COUNT', 'DATA_DOWNLOAD_COUNT',
                      'MODEL_LABEL_COUNT', 'MODEL_OUTPUT_COUNT', 'DATA_PIPELINE_COUNT',
                      'ENVIRONMENT_COUNT', 'STATE_OBSERVE_COUNT', 'TOTAL_EVENT_COUNT']
    df_list = []

    for repo in repo_names:
        logging.info(f"Processing repo: {repo}")
        repo_entity = res_df[res_df['REPO_FULL_PATH'] == repo]
        all_py_files = np.unique(repo_entity['FILE_FULL_PATH'].tolist())
        all_py_size = getAllSLOC(repo_entity)

        for field in fields2explore:
            field_res_list = repo_entity[field].tolist()
            field_res_count = sum(field_res_list)
            try:
                event_density = round((field_res_count * 1000) / all_py_size, 5)
            except ZeroDivisionError:
                event_density = 0
                logging.warning(f"All Python file size is zero for repo {repo}")
            logging.info(f"{repo} | Field: {field} | Total LOC: {all_py_size} | Total Events: {field_res_count} | Event Density: {event_density}")
            df_list.append((repo, all_py_size, field, field_res_count, event_density))

    CSV_HEADER = ['REPO_NAME', 'TOTAL_LOC', 'CATEGORY', 'TOTAL_EVENT_COUNT', 'EVENT_DENSITY']
    full_df = pd.DataFrame(df_list)
    full_df.to_csv(output_file, header=CSV_HEADER, index=False, encoding='utf-8')
    logging.info(f"Event density report saved to {output_file}")

if __name__ == '__main__':
    logging.info('*' * 100)
    t1 = time.time()
    logging.info(f"Started at: {giveTimeStamp()}")
    logging.info('*' * 100)

    # Example usage: update with actual CSV paths if needed
    # RESULTS_FILE = 'V5_OUTPUT_GITHUB.csv'
    # PROPORTION_FILE = 'PROPORTION_GITHUB.csv'
    # DENSITY_FILE = 'DENSITY_GITHUB.csv'
    
    # Uncomment below lines to run with actual files
    # reportProportion(RESULTS_FILE, PROPORTION_FILE)
    # reportEventDensity(RESULTS_FILE, DENSITY_FILE)

    logging.info(f"Ended at: {giveTimeStamp()}")
    logging.info(f"Duration: {(time.time() - t1)/60:.5f} minutes")
    logging.info('*' * 100)

