import logging
import ast
import os
import constants

# Configure logging
logging.basicConfig(
    filename='forensics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------------------------------
# FAME-ML Python AST parser with forensics
# ------------------------------------------

def checkLoggingPerData(tree_object, name2track):
    logging.info(f"Checking logging existence for data: {name2track}")
    LOGGING_EXISTS_FLAG = False 
    IMPORT_FLAG, FUNC_FLAG, ARG_FLAG  = False, False , False 

    # Check imports for logging
    for stmt_ in tree_object.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Import):
                funcDict = node_.__dict__     
                import_name_objects = funcDict[constants.NAMES_KW]
                for obj in import_name_objects:
                    if constants.LOGGING_KW in obj.__dict__[constants.NAME_KW]: 
                        IMPORT_FLAG = True 

    # Check function attribute calls
    func_decl_list = getPythonAttributeFuncs(tree_object)
    for func_decl_ in func_decl_list:
        # Safe unpack: handle possible missing fields
        if len(func_decl_) == 4:
            func_parent_id, func_name, funcLineNo, call_arg_list = func_decl_
        else:
            func_parent_id, func_name, funcLineNo = func_decl_
            call_arg_list = []

        if constants.LOGGING_KW in func_parent_id or constants.LOGGING_KW in func_name:
            FUNC_FLAG = True
            for arg_ in call_arg_list:
                if name2track in arg_:
                    ARG_FLAG = True

    LOGGING_EXISTS_FLAG = IMPORT_FLAG and FUNC_FLAG and ARG_FLAG
    logging.info(f"Logging check result: {LOGGING_EXISTS_FLAG}")
    return LOGGING_EXISTS_FLAG 


def getPythonParseObject(pyFile):
    try:
        logging.info(f"Parsing Python file: {pyFile}")
        full_tree = ast.parse(open(pyFile).read())
    except SyntaxError as e:
        logging.error(f"Syntax error parsing {pyFile}: {e}")
        full_tree = ast.parse(constants.EMPTY_STRING)
    return full_tree


def getFunctionAssignments(pyTree):
    logging.info("Extracting function assignments from AST")
    call_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
                logging.info(f"Found assignment at line {getattr(node_, 'lineno', 'unknown')}")
                lhs = ''
                assign_dict = node_.__dict__
                targets, value = assign_dict[constants.TARGETS_KW], assign_dict[constants.VALUE_KW]

                if isinstance(value, ast.Call):
                    funcDict = value.__dict__ 
                    funcName, funcArgs, funcLineNo = funcDict.get(constants.FUNC_KW), funcDict.get(constants.ARGS_KW, []), funcDict.get(constants.LINE_NO_KW)

                    for target in targets:
                        if isinstance(target, ast.Name):
                            lhs = target.id

                    call_arg_list = []
                    for i, funcArg in enumerate(funcArgs):
                        # Handle Name, Constant, JoinedStr, fallback
                        if isinstance(funcArg, ast.Name):
                            call_arg_list.append((funcArg.id, f'arg{i+1}'))
                        elif isinstance(funcArg, ast.Constant) and isinstance(funcArg.value, str):
                            call_arg_list.append((funcArg.value, f'arg{i+1}'))
                        elif isinstance(funcArg, ast.JoinedStr):
                            joined_str = ''.join([elem.s if isinstance(elem, ast.Constant) else '{expr}' for elem in funcArg.values])
                            call_arg_list.append((joined_str, f'arg{i+1}'))
                        else:
                            call_arg_list.append((str(funcArg), f'arg{i+1}'))

                    # funcName may be ast.Name or ast.Attribute
                    if isinstance(funcName, ast.Name):
                        funcNameStr = funcName.id
                    elif isinstance(funcName, ast.Attribute):
                        funcNameStr = funcName.attr
                    else:
                        funcNameStr = str(funcName)

                    call_list.append((lhs, funcNameStr, funcLineNo, call_arg_list))
    logging.info(f"Total function assignments extracted: {len(call_list)}")
    return call_list


def getFunctionDefinitions(pyTree):
    func_list = []
    logging.info("Analyzing function definitions")
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Call):
                funcDict = node_.__dict__ 
                func_, funcArgs, funcLineNo = funcDict.get(constants.FUNC_KW), funcDict.get(constants.ARGS_KW, []), funcDict.get(constants.LINE_NO_KW)

                # func_ can be Name or Attribute
                if isinstance(func_, ast.Name):
                    func_name = func_.id
                elif isinstance(func_, ast.Attribute):
                    func_name = func_.attr
                else:
                    func_name = str(func_)

                call_arg_list = []
                for i, arg in enumerate(funcArgs):
                    if isinstance(arg, ast.Name):
                        call_arg_list.append((arg.id, f'arg{i+1}'))
                    elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        call_arg_list.append((arg.value, f'arg{i+1}'))
                    elif isinstance(arg, ast.JoinedStr):
                        joined_str = ''.join([elem.s if isinstance(elem, ast.Constant) else '{expr}' for elem in arg.values])
                        call_arg_list.append((joined_str, f'arg{i+1}'))
                    else:
                        call_arg_list.append((str(arg), f'arg{i+1}'))

                func_list.append((func_name, funcLineNo, call_arg_list))
    logging.info(f"Total function calls found: {len(func_list)}")
    return func_list


def getPythonAttributeFuncs(pyTree):
    logging.info("Detecting attribute function calls")
    attrib_call_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Call):
                func = node_.func
                if isinstance(func, ast.Attribute):
                    parent_name = func.value.id if isinstance(func.value, ast.Name) else str(func.value)
                    func_name = func.attr
                    call_arg_list = []
                    for i, arg in enumerate(node_.args):
                        if isinstance(arg, ast.Name):
                            call_arg_list.append((arg.id, f'arg{i+1}'))
                        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            call_arg_list.append((arg.value, f'arg{i+1}'))
                        elif isinstance(arg, ast.JoinedStr):
                            joined_str = ''.join([elem.s if isinstance(elem, ast.Constant) else '{expr}' for elem in arg.values])
                            call_arg_list.append((joined_str, f'arg{i+1}'))
                        else:
                            call_arg_list.append((str(arg), f'arg{i+1}'))

                    attrib_call_list.append((parent_name, func_name, node_.lineno, call_arg_list))
    logging.info(f"Total attribute functions found: {len(attrib_call_list)}")
    return attrib_call_list


def getModelFeature(pyTree):
    feature_list = []
    logging.info("Detecting model features from AST")
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
                logging.info(f"Processing assignment at line {getattr(node_, 'lineno', 'unknown')}")
                assign_dict = node_.__dict__
                targets, value = assign_dict[constants.TARGETS_KW], assign_dict[constants.VALUE_KW]
                lhs = ''
                for target in targets:
                    if isinstance(target, ast.Name):
                        lhs = target.id

                if isinstance(value, ast.Attribute):
                    funcDict = value.__dict__ 
                    className, featureName, funcLineNo = funcDict.get(constants.VALUE_KW), funcDict.get(constants.ATTRIB_KW), funcDict.get(constants.LINE_NO_KW)
                    if isinstance(className, ast.Name):
                        feature_list.append((lhs, className.id, featureName, funcLineNo))
    logging.info(f"Total features extracted: {len(feature_list)}")
    return feature_list

