# SQA-REPO

## 1. Logging / Forensics Integration (25%)

### Files and Methods Instrumented
We integrated logging statements across multiple Python files in the `forensics/` directory. Logging helps trace execution, capture errors, and provides lightweight forensics.

#### **1.1 `py_parser.py`**
| Method                  | Logging Integration | Notes |
|-------------------------|------------------|-------|
| `checkLoggingPerData`    | ✅ Logs start of logging check and final result | Checks for logging imports, function calls, and tracked arguments |
| `getPythonParseObject`   | ✅ Logs parsing start and any syntax errors | Exception handling logs errors |
| `getFunctionAssignments` | ✅ Logs extraction start, line numbers of assignments, total assignments | Detailed tracing of function assignments |
| `getFunctionDefinitions` | ✅ Logs analysis start and total function calls | Captures function calls within AST |
| `getPythonAttributeFuncs`| ✅ Logs detection start and total attribute functions | Tracks attribute-level function calls |

#### **1.2 `frequency.py`**
| Method                  | Logging Integration | Notes |
|-------------------------|------------------|-------|
| `giveTimeStamp`          | ✅ Logs generated timestamps | Verifies timestamp format and values |
| `getAllSLOC`             | ✅ Logs total SLOC from dummy and real files | Helps trace source code metrics |
| `reportProportion`       | ✅ Logs input data and computed proportions | Useful for debugging CSV/metric computations |
| `reportEventDensity`     | ✅ Logs input data and calculated densities | Tracks event-related calculations |

#### **1.3 `mining.py`**
| Method                  | Logging Integration | Notes |
|-------------------------|------------------|-------|
| `dumpContentIntoFile`    | ✅ Logs written content size and target filename | Tracks file output for debugging |
| `makeChunks`             | ✅ Logs chunked data | Ensures correct data segmentation |
| `getPythonFileCount`     | ✅ Logs total Python files counted | Helps verify repository analysis |
| `days_between`           | ✅ Logs calculated days difference | Useful for date/time calculations |
| `deleteRepo`             | ✅ Logs deletion attempts and results | Tracks repository cleanup operations |

### Lesson Learned
Integrating logging across all key methods provides **traceability**, **debugging support**, and a lightweight form of **forensic auditing**. Logs help identify unexpected behavior, validate outputs, and serve as a record of execution flow for analysis.


## 2. Fuzzing Results  

We developed a standalone fuzzing engine (`fuzz.py`) to automatically test five methods across the project. The goal was to identify robustness issues, unhandled exceptions, and assumptions about input validity.

### 2.1 Methods Fuzzed  

1. **frequency.giveTimeStamp()**  
   - Safe utility function.  
   - Fuzzed by repeatedly calling with zero arguments.  
   - Always stable.

2. **lint_engine.getDataLoadCount(py_file)**  
   - Sensitive to invalid paths.  
   - Fuzzed using random, nonexistent filenames.

3. **py_parser.getPythonParseObject(py_file)**  
   - Parses Python files.  
   - Fuzzed with random filenames to test parsing behavior.

4. **mining.dumpContentIntoFile(text, file)**  
   - Writes content to files.  
   - Fuzzed with random text and output paths.

5. **git.repo.miner.makeChunks(list, size)**  
   - Pure function.  
   - Fuzzed with randomly generated lists and chunk sizes.

### 2.2 Observed Behavior  

- All fuzzing results were logged to `fuzz_errors.txt`.  
- The fuzzer ran fully without crashing and successfully recorded all exceptions.

**Finding #1 — FileNotFoundError (Expected)**  
- Both `getDataLoadCount` and `getPythonParseObject` attempt to read files directly using:

    ```python
    open(pyFile).read()
    ```
- Fuzzing passed random filenames that did not exist.  
- This consistently produced `FileNotFoundError`.  
- Not a bug; it confirms these functions assume valid file paths.

**Finding #2 — makeChunks() is highly stable**  
- Handled random list sizes, contents, and chunk sizes without errors.

**Finding #3 — dumpContentIntoFile() behaved normally**  
- Writing random content to random filenames produced expected outcomes—successful writes when possible and IO errors otherwise.

**Finding #4 — giveTimeStamp() is fully robust**  
- This function never threw an exception.

### 2.3 Summary of Findings  

- No unexpected crashes occurred.  
- All logged errors were predictable and related to nonexistent input files.  
- Parsing functions are sensitive to invalid file paths.  
- Pure functions handled malformed data gracefully.

### 2.4 Lessons Learned From Fuzz Testing  

- Fuzzing exposes assumptions about input validity.  
- Many functions lack defensive programming (e.g., file existence checks).  
- Utility functions are robust.  
- IO-based components behave predictably under fuzzing.  
- Logging every error provides insight into system behavior.
  
  
## 3. GitHub Actions Continuous Integration  

We implemented a CI pipeline using GitHub Actions to automatically run all tests and logging verification on every push or pull request to the `main` branch. The CI runner (`ci_runner.py`) executes all forensic and logging tests and uploads log files as artifacts.

### 3.1 CI Runner Workflow  

1. **Checkout Repository**  
   - Uses `actions/checkout@v3` to pull the latest code.

2. **Setup Python Environment**  
   - Uses `actions/setup-python@v4` to install Python 3.11.
   - Installs project dependencies (`pandas`).

3. **Run Local CI (`ci_runner.py`)**  
   - Executes:
     - `forensics/test_logging_frequency.py`
     - `forensics/test_logging_mining.py`
     - `forensics/test_logging_py_parser.py`
   - Each test validates logging integration for its corresponding module.
   - Tests also print key AST analysis, function calls, and assignments to ensure accurate logging instrumentation.

4. **Upload Artifacts**  
   - Uploads:
     - `forensics/forensics.log`
     - `forensics/forensics_frequency.log`
     - `forensics/forensics_mining.log`
   - Provides a persistent record for CI analysis and debugging.

### 3.2 Tests Instrumented  

| Test File | Module Tested | Key Checks |
|-----------|---------------|------------|
| `test_logging_frequency.py` | `frequency.py` | Verifies timestamps, SLOC counting, and CSV logging |
| `test_logging_mining.py`    | `mining.py`    | Verifies content dumping, chunking, file counting, and date calculations |
| `test_logging_py_parser.py` | `py_parser.py` | AST parsing, function assignments, function calls, and attribute function detection |

### 3.3 Observed CI Behavior  

- All logging tests passed successfully after activating the Python virtual environment and installing dependencies.  
- Test logs were automatically generated and uploaded as artifacts for future reference.  
- AST parsing tests accurately reported function calls, assignments, and attribute usage.  
- Any missing dependencies (e.g., `pandas`) were caught early in the CI run.

### 3.4 Lessons Learned from CI Integration  

- CI automates validation of logging and ensures code changes do not break existing functionality.  
- Uploading log files as artifacts improves traceability and debugging.  
- Running CI in a clean environment highlights missing dependencies early.  
- Integrating fuzz testing results with CI could further improve system reliability.  
- CI enforces consistent testing practices across the team.
