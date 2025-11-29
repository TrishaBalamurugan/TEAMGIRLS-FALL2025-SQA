import sys
import os
import ast

# Add current folder (forensics) to sys.path so imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import py_parser  # now imports correctly

# Correct path to py_parser.py
py_file_path = os.path.join(os.path.dirname(__file__), 'py_parser.py')

# Parse the Python file
tree = py_parser.getPythonParseObject(py_file_path)

# ---------------------------------------
# Check logging for a sample variable
# ---------------------------------------
print("\n--- Checking Logging for 'some_var' ---")
logging_result = py_parser.checkLoggingPerData(tree, 'some_var')
print(f"Logging check result: {logging_result}")

# ---------------------------------------
# Get function assignments
# ---------------------------------------
print("\n--- Function Assignments ---")
func_assignments = py_parser.getFunctionAssignments(tree)
for lhs, func_name, line_no, args in func_assignments:
    print(f"Line {line_no}: {lhs} = {func_name}({', '.join([a[0] for a in args])})")

# ---------------------------------------
# Get function definitions / calls
# ---------------------------------------
print("\n--- Function Calls ---")
func_defs = py_parser.getFunctionDefinitions(tree)
for func_name, line_no, args in func_defs:
    print(f"Line {line_no}: {func_name}({', '.join([a[0] for a in args])})")

# ---------------------------------------
# Get attribute function calls
# ---------------------------------------
print("\n--- Attribute Function Calls ---")
attrib_funcs = py_parser.getPythonAttributeFuncs(tree)
for parent, func_name, line_no, args in attrib_funcs:
    print(f"Line {line_no}: {parent}.{func_name}({', '.join([a[0] for a in args])})")

# ---------------------------------------
# Get model features
# ---------------------------------------
print("\n--- Model Features ---")
features = py_parser.getModelFeature(tree)
for lhs, class_name, feature_name, line_no in features:
    print(f"Line {line_no}: {lhs} = {class_name}.{feature_name}")

