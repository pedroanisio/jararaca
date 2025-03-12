"""
Check link for Python naming conventions.

This module contains the NamingConventionsCheck class which verifies that Python code
follows PEP 8 naming conventions.
"""

import os
from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus
from .naming_conventions_checks import (
    check_file_content,
    check_module_name,
)


class NamingConventionsCheck(CheckLink):
    """
    Check link for Python naming conventions according to PEP 8.
    """

    def __init__(self) -> None:
        """Initialize a naming conventions check link."""
        super().__init__("Naming Conventions")

    def _process_python_file(self, file_path: str) -> List[str]:
        """
        Process a Python file and check for naming convention issues.

        Args:
            file_path: The path to the file to check.

        Returns:
            A list of naming convention issues found in the file.
        """
        issues: List[str] = []

        # Check module name (file name)
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        issues.extend(check_module_name(module_name, file_path))

        # Check file content for class, function, and variable names
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_issues = check_file_content(content, file_path)
                issues.extend(file_issues)
        except Exception as e:
            issues.append(f"Error reading {file_path}: {str(e)}")

        return issues

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check naming conventions in Python files.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the naming conventions check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        issues = []

        # Check each source directory
        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            # Walk through the directory
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    issues.extend(self._process_python_file(file_path))

        # Determine the status based on issues found
        if issues:
            status = CheckStatus.FAILED
            details = "Naming convention issues found:\n" + "\n".join(issues)
        else:
            status = CheckStatus.PASSED
            details = "All code follows naming conventions."

        return [CheckResult(self.name, status, details)]
