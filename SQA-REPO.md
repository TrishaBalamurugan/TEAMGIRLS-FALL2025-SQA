# SQA-REPO

## 1. Logging / Forensics Integration (25%)

### Files and Methods Instrumented
We integrated logging statements in 5 Python methods within `FAME_ML/py_parser.py`:

| Method                  | Logging Integration | Notes |
|-------------------------|------------------|-------|
| `checkLoggingPerData`    | ✅ Logs start of logging check and final result | Checks for logging imports, function calls, and tracked arguments |
| `getPythonParseObject`   | ✅ Logs parsing start and any syntax errors | Exception handling logs errors |
| `getFunctionAssignments` | ✅ Logs extraction start, line numbers of assignments, total assignments | Detailed tracing of function assignments |
| `getFunctionDefinitions` | ✅ Logs analysis start and total function calls | Captures function calls within AST |
| `getPythonAttributeFuncs`| ✅ Logs detection start and total attribute functions | Tracks attribute-level function calls |

### Lesson Learned
Integrating logging provides traceability of internal processing and helps identify bugs or unexpected behavior. Logging can serve as a form of lightweight forensics, particularly in a pipeline processing code ASTs.

## 2. Fuzzing Results
### Files and Methods Instrumented
### Lesson Learned

## 3. GitHub Actions Continuous Integration 
### Files and Methods Instrumented
### Lesson Learned
