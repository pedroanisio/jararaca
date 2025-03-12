"""
Individual check functions for naming conventions.

This module contains functions that check different aspects of naming conventions,
such as module names, class names, function names, and variable names.
"""

import re
from typing import List

from .naming_conventions_utils import (
    AST_VISITOR_PATTERN,
    CLASS_PATTERN,
    COMMON_WORDS,
    CONSTANT_PATTERN,
    DUNDER_PATTERN,
    FUNCTION_PATTERN,
    MODULE_PATTERN,
    PYTHON_KEYWORDS,
    VARIABLE_PATTERN,
    should_skip_variable,
    strip_comments_and_docstrings,
)


def check_module_name(module_name: str, file_path: str) -> List[str]:
    """
    Check if a module name follows the snake_case convention.

    Args:
        module_name: The name of the module to check.
        file_path: The path to the file being checked.

    Returns:
        A list of naming convention issues found.
    """
    issues: List[str] = []

    # Skip special module names like __init__, __main__
    if module_name.startswith("__") and module_name.endswith("__"):
        return issues

    if not MODULE_PATTERN.match(module_name):
        issues.append(
            f"Module name '{module_name}' in {file_path} does not follow snake_case convention"
        )
    return issues


def check_class_names(content: str, file_path: str) -> List[str]:
    """
    Check class names in a file for PascalCase convention.

    Args:
        content: The content of the file to check.
        file_path: The path to the file being checked.

    Returns:
        A list of naming convention issues found.
    """
    issues = []

    # Remove docstrings and comments to avoid false positives
    cleaned_content = strip_comments_and_docstrings(content)

    # Use a more specific pattern that matches 'class name:' or 'class name('
    class_pattern = re.compile(r"class\s+([A-Za-z0-9_]+)[\s\(:]")
    for match in class_pattern.finditer(cleaned_content):
        class_name = match.group(1)
        # Skip common words that might appear in docstrings
        if class_name.lower() in COMMON_WORDS or class_name in PYTHON_KEYWORDS:
            continue

        if not CLASS_PATTERN.match(class_name):
            issues.append(
                f"Class name '{class_name}' in {file_path} does not follow PascalCase convention"
            )
    return issues


def check_function_names(content: str, file_path: str) -> List[str]:
    """
    Check function names in a file for snake_case convention.

    Args:
        content: The content of the file to check.
        file_path: The path to the file being checked.

    Returns:
        A list of naming convention issues found.
    """
    issues = []

    # Remove docstrings and comments to avoid false positives
    cleaned_content = strip_comments_and_docstrings(content)

    # Use a more specific pattern that matches 'def name(' or 'def name:'
    function_pattern = re.compile(r"def\s+([A-Za-z0-9_]+)[\s\(:]")
    for match in function_pattern.finditer(cleaned_content):
        function_name = match.group(1)

        # Skip special methods and recognized naming patterns
        if DUNDER_PATTERN.match(function_name):
            continue
        if AST_VISITOR_PATTERN.match(function_name):
            continue
        if function_name.startswith("_"):
            # For private methods, check if rest follows snake_case
            if FUNCTION_PATTERN.match(function_name[1:]):
                continue

        # Skip common words that might appear in docstrings
        if function_name.lower() in COMMON_WORDS:
            continue

        if not FUNCTION_PATTERN.match(function_name):
            issues.append(
                f"Function name '{function_name}' in {file_path} does not follow snake_case convention"
            )
    return issues


def check_constant_name(variable_name: str, file_path: str) -> List[str]:
    """
    Check if a constant name follows the UPPER_CASE convention.

    Args:
        variable_name: The name of the constant to check
        file_path: The path to the file being checked

    Returns:
        A list of naming convention issues found
    """
    issues = []
    if not CONSTANT_PATTERN.match(variable_name):
        issues.append(
            f"Constant '{variable_name}' in {file_path} does not follow UPPER_CASE convention"
        )
    return issues


def check_regular_variable_name(variable_name: str, file_path: str) -> List[str]:
    """
    Check if a regular variable name follows the snake_case convention.

    Args:
        variable_name: The name of the variable to check
        file_path: The path to the file being checked

    Returns:
        A list of naming convention issues found
    """
    issues = []
    if not VARIABLE_PATTERN.match(variable_name):
        issues.append(
            f"Variable '{variable_name}' in {file_path} does not follow snake_case convention"
        )
    return issues


def check_variable_names(content: str, file_path: str) -> List[str]:
    """
    Check variable names in a file for snake_case convention.

    Args:
        content: The content of the file to check.
        file_path: The path to the file being checked.

    Returns:
        A list of naming convention issues found.
    """
    issues = []

    # Remove docstrings and comments to avoid false positives
    cleaned_content = strip_comments_and_docstrings(content)

    # Find variable assignments
    # This is simplified and may not catch all variable names
    variable_pattern = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=")
    for match in variable_pattern.finditer(cleaned_content):
        variable_name = match.group(1)

        # Skip variables that should be ignored
        if should_skip_variable(variable_name):
            continue

        # Check if it's a constant (all uppercase)
        if variable_name.isupper():
            issues.extend(check_constant_name(variable_name, file_path))
        # Skip dunder and private variables
        elif variable_name.startswith("__") or variable_name.startswith("_"):
            continue
        # Otherwise it should be a regular variable
        else:
            issues.extend(check_regular_variable_name(variable_name, file_path))

    return issues


def check_file_content(content: str, file_path: str) -> List[str]:
    """
    Check the content of a file for naming convention issues.

    Args:
        content: The content of the file to check
        file_path: The path to the file being checked

    Returns:
        A list of naming convention issues found in the file
    """
    issues = []

    # Check class names
    issues.extend(check_class_names(content, file_path))

    # Check function names
    issues.extend(check_function_names(content, file_path))

    # Check variable names
    issues.extend(check_variable_names(content, file_path))

    return issues
