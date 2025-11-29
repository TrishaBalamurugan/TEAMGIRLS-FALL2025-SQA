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

We developed a standalone fuzzing engine (fuzz.py) to automatically test five methods across the project. The goal was to identify robustness issues, unhandled exceptions, and assumptions made by the program when receiving malformed or unexpected input.

2.1 Methods Fuzzed

1. frequency.giveTimeStamp()
- Safe utility function
- Fuzzed by repeatedly calling with zero arguments
- Always stable

2. lint_engine.getDataLoadCount(py_file)
- Sensitive to invalid paths
- Fuzzed using random, nonexistent filenames

3. py_parser.getPythonParseObject(py_file)
- Parses Python files
- Fuzzed with random filenames to test parsing behavior

4. mining.dumpContentIntoFile(text, file)
- Writes content to files
- Fuzzed with random text and output paths

5. git.repo.miner.makeChunks(list, size)
- Pure function
- Fuzzed with randomly generated lists and chunk sizes

2.2 Observed Behavior

All fuzzing results were logged to fuzz_errors.txt.
The fuzzer ran fully without crashing and successfully recorded all exceptions.

Finding #1 — FileNotFoundError (Expected)
Both getDataLoadCount and getPythonParseObject attempt to read files directly using:

    open(pyFile).read()

Because fuzzing passed random filenames, these files did not exist.
This consistently produced FileNotFoundError.
This is not a program bug; it confirms the functions assume valid file paths.

Finding #2 — makeChunks() is highly stable
makeChunks handled random list sizes, contents, and chunk sizes without errors.

Finding #3 — dumpContentIntoFile() behaved normally
Writing random content to random filenames resulted in expected outcomes—successful writes when possible and IO errors otherwise.

Finding #4 — giveTimeStamp() is fully robust
This function never threw an exception.

2.3 Summary of Findings
- No unexpected crashes occurred.
- All logged errors were predictable and related to nonexistent input files.
- Parsing functions are sensitive to invalid file paths.
- Pure functions handled malformed data gracefully.

2.4 Lessons Learned From Fuzz Testing
- Fuzzing exposes assumptions about input validity.
- Many functions lack defensive programming (e.g., file existence checks).
- Utility functions are robust.
- IO-based components behave predictably under fuzzing.
- Logging every error provides insight into system behavior.

  
## 3. GitHub Actions Continuous Integration 
### Files and Methods Instrumented
*TODO: List tests and CI runner behavior*

### Lesson Learned
*TODO: Add insights on CI integration, benefits, and lessons learned*
