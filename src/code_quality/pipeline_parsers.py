"""
Pipeline parsers module.

This module contains functions for parsing the output of various code quality checks.
"""

import re
from typing import Any, Dict, Optional, Union

from .utils import CheckResult, CheckStatus


def parse_details(check_name: str, details: str) -> Dict[str, Any]:
    """
    Parse the details text to extract structured information.

    Args:
        check_name: Name of the check
        details: Details text from the check result

    Returns:
        A dictionary containing structured details information
    """
    # Default structure
    parsed: Dict[str, Any] = {
        "summary": details.split("\n")[0] if details else "",
        "issues": [],
    }

    # Delegate to specific parsers based on check name
    if "Code Formatting" in check_name:
        parse_formatting_details(details, parsed)
    elif "Import Sorting" in check_name:
        parse_import_sorting_details(details, parsed)
    elif "Linting" in check_name:
        parse_linting_details(details, parsed)
    elif "Type Checking" in check_name:
        parse_type_checking_details(details, parsed)
    elif "Security Check" in check_name:
        parse_security_details(details, parsed)
    elif "Test Coverage" in check_name:
        parse_coverage_details(details, parsed)
    elif (
        "Naming Conventions" in check_name
        or "File Length" in check_name
        or "Function Length" in check_name
    ):
        parse_code_structure_details(details, parsed)
    elif "Docstring Check" in check_name:
        parse_docstring_details(details, parsed)

    return parsed


def parse_formatting_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse formatting check details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    if "Files need formatting" in details:
        # Extract file list if present
        files = [line.strip() for line in details.split("\n")[1:] if line.strip()]
        parsed["files"] = files


def parse_import_sorting_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse import sorting check details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Import sorting might include diffs
    if "Imports need sorting" in details:
        # Try to extract file paths and diffs
        files = []
        current_file = None
        for line in details.split("\n"):
            if line.startswith("---") and "before" in line:
                current_file = line.split("---")[1].strip().split(":before")[0].strip()
                files.append(current_file)
        parsed["files"] = files


def parse_linting_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse linting check details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract individual linting issues
    issues = []
    current_issue = None
    for line in details.split("\n"):
        if line.strip() and ":" in line and any(char.isdigit() for char in line):
            # This looks like a linting issue with line numbers
            current_issue = line.strip()
            issues.append(current_issue)
    if issues:
        parsed["issues"] = issues


def parse_type_checking_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse type checking details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract type checking issues
    issues = []
    current_issue = None
    for line in details.split("\n"):
        if line.strip() and ":" in line and any(char.isdigit() for char in line):
            if "error:" in line or "note:" in line:
                current_issue = line.strip()
                issues.append(current_issue)
    if issues:
        parsed["issues"] = issues


def parse_security_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse security check details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract security issues
    issues = []
    for line in details.split("\n"):
        if "Issue:" in line:
            issues.append(line.strip())
    if issues:
        parsed["issues"] = issues


def parse_coverage_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse test coverage details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract coverage percentage
    for line in details.split("\n"):
        if "coverage is" in line.lower():
            match = re.search(r"(\d+(?:\.\d+)?)%", line)
            if match:
                coverage_value = match.group(1)
                try:
                    # Ensure coverage_percentage is typed correctly
                    parsed["coverage_percentage"] = float(coverage_value)
                except ValueError:
                    pass


def parse_code_structure_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse naming, file length, and function length details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract files/functions exceeding limits
    issues = []
    for line in details.split("\n"):
        if line.strip() and ":" in line and ("/" in line or "\\" in line):
            issues.append(line.strip())
    if issues:
        parsed["issues"] = issues


def parse_docstring_details(details: str, parsed: Dict[str, Any]) -> None:
    """
    Parse docstring check details.

    Args:
        details: The raw details string from the check
        parsed: The dictionary to populate with structured data
    """
    # Extract missing docstrings
    issues = []
    for line in details.split("\n"):
        if line.strip() and "-" in line and "function" in line:
            issues.append(line.strip())
    if issues:
        parsed["issues"] = issues
