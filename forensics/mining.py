import os
import pandas as pd 
import numpy as np
import csv 
import time 
from datetime import datetime
import subprocess
import shutil
from git import Repo
from git import exc
import logging

# ----------------------------
# Configure Forensics Logging
# ----------------------------
logging.basicConfig(
    filename='forensics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ----------------------------
# MLForensics Mining Functions
# ----------------------------

def giveTimeStamp():
    tsObj = time.time()
    strToret = datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Timestamp generated: {strToret}")
    return strToret

def deleteRepo(dirName, type_):
    logging.info(f"Deleting directory {dirName} due to {type_}")
    try:
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
            logging.info(f"Deleted directory {dirName}")
    except OSError as e:
        logging.error(f"Failed deleting {dirName}: {e}")

def dumpContentIntoFile(strP, fileP):
    logging.info(f"Writing content to file {fileP}")
    with open(fileP, 'w') as fileToWrite:
        fileToWrite.write(strP)
    size = os.stat(fileP).st_size
    logging.info(f"Wrote {size} bytes to {fileP}")
    return str(size)

def makeChunks(the_list, size_):
    logging.info(f"Creating chunks of size {size_} from list of length {len(the_list)}")
    for i in range(0, len(the_list), size_):
        yield the_list[i:i+size_]

def cloneRepo(repo_name, target_dir):
    logging.info(f"Cloning repo {repo_name} into {target_dir}")
    cmd_ = f"git clone {repo_name} {target_dir}"
    try:
        subprocess.check_output(['bash', '-c', cmd_])
        logging.info(f"Successfully cloned {repo_name}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Trouble cloning repo {repo_name}: {e}")

def checkPythonFile(path2dir):
    logging.info(f"Checking Python files in {path2dir}")
    usageCount = 0
    patternDict = ['sklearn', 'h5py', 'gym', 'rl', 'tensorflow', 'keras', 'tf', 'stable_baselines', 'tensorforce', 'rl_coach', 'pyqlearning', 'MAMEToolkit', 'chainer', 'torch', 'chainerrl']
    for root_, _, filenames in os.walk(path2dir):
        for file_ in filenames:
            full_path_file = os.path.join(root_, file_) 
            if os.path.exists(full_path_file) and (file_.endswith('py') or file_.endswith('ipynb')):
                with open(full_path_file, 'r', encoding='latin-1') as f:
                    pythonFileContent = f.read().split('\n')
                    pythonFileContent = [z_.lower() for z_ in pythonFileContent if z_ != '\n']
                    for content_ in pythonFileContent:
                        for item_ in patternDict:
                            if item_ in content_:
                                usageCount += 1
                                logging.info(f"Pattern found in {full_path_file}: {content_}")
    logging.info(f"Total patterns found: {usageCount}")
    return usageCount

def days_between(d1_, d2_):
    delta_days = abs((d2_ - d1_).days)
    logging.info(f"Days between {d1_} and {d2_}: {delta_days}")
    return delta_days

def getDevEmailForCommit(repo_path_param, hash_):
    logging.info(f"Getting developer emails for commit {hash_} in {repo_path_param}")
    author_emails = []
    cdCommand = f"cd {repo_path_param} ; "
    commitCountCmd = f"git log --format='%ae'{hash_}^!"
    command2Run = cdCommand + commitCountCmd

    try:
        author_emails = str(subprocess.check_output(['bash', '-c', command2Run])).split('\n')
        author_emails = [x_.replace(hash_, '').replace('^','').replace('!','').replace('\\n',',') 
                         for x_ in author_emails if '@' in x_]
        author_emails = list(np.unique(author_emails[0].split(',')))
    except (IndexError, subprocess.CalledProcessError) as e:
        logging.error(f"Error getting emails for commit {hash_}: {e}")
        author_emails = []
    logging.info(f"Developer emails found: {author_emails}")
    return author_emails

def getDevDayCount(full_path_to_repo, branchName='master', explore=1000):
    logging.info(f"Calculating developer day count for {full_path_to_repo} on branch {branchName}")
    repo_emails, all_commits, all_time_list = [], [], []
    if os.path.exists(full_path_to_repo):
        repo_  = Repo(full_path_to_repo)
        try:
            all_commits = list(repo_.iter_commits(branchName))
        except exc.GitCommandError:
            logging.warning(f"Skipping repo {full_path_to_repo} due to branch name problem")
        for commit_ in all_commits:
            commit_hash = commit_.hexsha
            emails = getDevEmailForCommit(full_path_to_repo, commit_hash)
            repo_emails += emails
            all_time_list.append(commit_.committed_datetime.strftime('%Y-%m-%d'))

    all_day_list = [datetime(int(x_.split('-')[0]), int(x_.split('-')[1]), int(x_.split('-')[2]), 12, 30) for x_ in all_time_list]
    try:
        ds_life_days = days_between(min(all_day_list), max(all_day_list))
    except (ValueError, TypeError):
        ds_life_days = 0
    ds_life_months = round(ds_life_days / 30.0, 5)
    logging.info(f"Repo {full_path_to_repo}: {len(repo_emails)} devs, {len(all_commits)} commits, {ds_life_days} days, {ds_life_months} months")
    return len(repo_emails), len(all_commits), ds_life_days, ds_life_months

def getPythonFileCount(path2dir):
    valid_list = [file_ for _, _, filenames in os.walk(path2dir) for file_ in filenames if file_.endswith(('py', 'ipynb'))]
    logging.info(f"Python file count in {path2dir}: {len(valid_list)}")
    return len(valid_list)

def cloneRepos(repo_list, dev_threshold=3, python_threshold=0.10, commit_threshold=25):
    logging.info(f"Starting cloning of {len(repo_list)} repo batches")
    counter, str_, all_list = 0, '', []
    for repo_batch in repo_list:
        for repo_ in repo_batch:
            counter += 1
            logging.info(f"Processing repo {counter}: {repo_}")
            dirName = '../FSE2021_REPOS/' + repo_.split('/')[-2] + '@' + repo_.split('/')[-1]
            cloneRepo(repo_, dirName)
            checkPattern, dev_count, python_count, commit_count, age_months, flag = 0, 0, 0, 0, 0, True
            all_fil_cnt = sum([len(files) for r_, d_, files in os.walk(dirName)])
            python_count = getPythonFileCount(dirName)

            if all_fil_cnt <= 0:
                deleteRepo(dirName, 'NO_FILES')
                flag = False
            elif python_count < (all_fil_cnt * python_threshold):
                deleteRepo(dirName, 'NOT_ENOUGH_PYTHON_FILES')
                flag = False
            else:
                dev_count, commit_count, age_days, age_months = getDevDayCount(dirName)
                if dev_count < dev_threshold:
                    deleteRepo(dirName, 'LIMITED_DEVS')
                    flag = False
                elif commit_count < commit_threshold:
                    deleteRepo(dirName, 'LIMITED_COMMITS')
                    flag = False

            if flag:
                checkPattern = checkPythonFile(dirName)
                if checkPattern == 0:
                    deleteRepo(dirName, 'NO_PATTERN')
                    flag = False

            str_ += f"{counter},{repo_},{dirName},{checkPattern},{dev_count},{flag}\n"
            all_list.append((counter, dirName, dev_count, all_fil_cnt, python_count, commit_count, age_months, flag))
            logging.info(f"Completed repo {counter}: {repo_}, flag={flag}")

            if counter % 100 == 0:
                dumpContentIntoFile(str_, 'tracker_completed_repos.csv')
                df_ = pd.DataFrame(all_list)
                df_.to_csv('PYTHON_BREAKDOWN.csv', header=['INDEX','REPO','DEVS','FILES','PYTHON_FILES','COMMITS','AGE_MONTHS','FLAG'], index=False, encoding='utf-8')
    logging.info("Finished processing all repos")

if __name__ == '__main__':
    repos_df = pd.read_csv('PARTIAL_REMAINING_GITHUB.csv', sep='delimiter')
    logging.info(f"Repos dataframe loaded: {repos_df.shape}")
    list_ = np.unique(repos_df['url'].tolist())
    logging.info(f"Total unique repos to process: {len(list_)}")

    t1 = time.time()
    logging.info(f"Started at: {giveTimeStamp()}")
    chunked_list = list(makeChunks(list_, 100))
    cloneRepos(chunked_list)
    logging.info(f"Ended at: {giveTimeStamp()}")
    logging.info(f"Duration: {(time.time() - t1)/60:.5f} minutes")

