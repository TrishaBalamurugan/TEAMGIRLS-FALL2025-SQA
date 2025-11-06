# TEAMGIRLS-FALL2025-SQA
Software Quality Assurance (SQA) project for COMP 5710/6710: integrates fuzz testing, forensics logging, and GitHub Actions CI into the MLForensics Python project.

## Team Information
- **Trisha Balamurugan** – tpb0023@auburn.edu  
- **Jaiden Cummings** – jec0130@auburn.edu  

## Project Overview
This project integrates **Software Quality Assurance (SQA)** activities into the existing `MLForensics` Python project as part of COMP 5710/6710. The main objectives are to implement fuzz testing, forensics logging, and continuous integration, and to document lessons learned.

## Project Structure
├─ fuzz.py # Script to fuzz 5 Python methods
├─ forensics/ # Modified Python files with logging
├─ workflows/ # GitHub Actions workflows
│ └─ ci.yml
├─ README.md
├─ SQA-REPO.md # Report describing activities and lessons learned
└─ MLForensics.zip # Original project files


## SQA Activities
1. **Fuzz Testing**  
   - Automated fuzzing of 5 selected Python methods.  
   - Reports any bugs found during execution.  

2. **Forensics Logging**  
   - Integrated logging in 5 Python methods.  
   - Captures method entry/exit, exceptions, and key variables.  

3. **Continuous Integration (CI)**  
   - GitHub Actions workflow triggers on `push` or `pull_request`.  
   - Automatically executes tests, fuzzing, and forensics scripts.  

## Lessons Learned
- Documented in `SQA-REPO.md`.

## How to Run
1. Clone the repository:  
   ```bash
   git clone https://github.com/TrishaBalamurugan/TEAMGIRLS-FALL2025-SQA.git
   cd TEAMGIRLS-FALL2025-SQA
2. Run fuzz testing:
      python fuzz.py
3. Check forensics/forensics.log for logging outputs.
4. CI workflow runs automatically on GitHub for any push or pull request.
