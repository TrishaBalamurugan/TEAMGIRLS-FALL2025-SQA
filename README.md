# TEAMGIRLS-FALL2025-SQA

Software Quality Assurance (SQA) project for COMP 5710/6710: integrates fuzz testing, forensics logging, and GitHub Actions CI into the MLForensics Python project.

## Team Information
- **Trisha Balamurugan** – tpb0023@auburn.edu  
- **Jaiden Cummings** – jec0130@auburn.edu  

## Project Overview
This project integrates **Software Quality Assurance (SQA)** activities into the existing `MLForensics` Python project as part of COMP 5710/6710. The main objectives are to implement fuzz testing, forensics logging, and continuous integration, and to document lessons learned.

# Project Structure

```text
Project Structure
├─ fuzz.py                      # Script to fuzz 5 Python methods and log crashes in fuzz_log.txt
├─ forensics/                    # Modified Python files with integrated logging
│  ├─ empty.txt                  # Placeholder/empty file
│  ├─ forensics.log              # Generated log capturing method execution and key variables
│  ├─ forensics_frequency.log    # Log for frequency module tests
│  ├─ forensics_mining.log       # Log for mining module tests
│  ├─ frequency.py               # Python file with logging instrumented methods
│  ├─ mining.py                  # Python file with logging instrumented methods
│  ├─ py_parser.py               # Python file instrumented with logging from FAME-ML
│  ├─ test_logging_frequency.py  # Script to test logging integration in frequency.py
│  ├─ test_logging_mining.py     # Script to test logging integration in mining.py
│  └─ test_logging_py_parser.py  # Script to test logging integration in py_parser.py
├─ workflows/                    # GitHub Actions workflows for CI
│  ├─ empty2.txt                 # Placeholder/empty file
│  └─ ci.yml                     # Executes tests, fuzzing, and logging automatically on push/pull_request
├─ LICENSE                       # License file
├─ README.md                      # Project overview, team info, and instructions
└─ SQA-REPO.md                   # Report describing activities such as logging, fuzzing, CI results, and lessons learned
```text

## SQA Activities

### 1. Fuzz Testing
- Automated fuzzing of 5 selected Python methods.  
- Reports any bugs found during execution (`fuzz_log.txt`).  

### 2. Forensics Logging
- Integrated logging in 5 Python methods.  
- Captures method entry/exit, exceptions, and key variables (`forensics/forensics.log`).  

### 3. Continuous Integration (CI)
- GitHub Actions workflow triggers on `push` or `pull_request`.  
- Automatically executes tests, fuzzing, and forensics scripts.  

## Lessons Learned
- Detailed lessons and observations are documented in `SQA-REPO.md`.  
- Logging greatly improves traceability and debugging.  
- Fuzzing identifies edge cases and unexpected crashes.  
- CI ensures code quality is continuously monitored.

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/TrishaBalamurugan/TEAMGIRLS-FALL2025-SQA.git
   cd TEAMGIRLS-FALL2025-SQA
2. Run fuzz testing:
   python3 fuzz.py
3. Check forensics logging output:
   cat forensics/forensics.log
4. CI workflow runs automatically on GitHub for any push or pull request.
