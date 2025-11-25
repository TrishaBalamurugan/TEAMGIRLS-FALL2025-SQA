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
### Files and Methods Instrumented
*TODO: List methods fuzzed and observed behavior/bugs*

### Lesson Learned
*TODO: Add insights on fuzz testing results and lessons learned*

## 3. GitHub Actions Continuous Integration 
### Files and Methods Instrumented
*TODO: List tests and CI runner behavior*

### Lesson Learned
*TODO: Add insights on CI integration, benefits, and lessons learned*
