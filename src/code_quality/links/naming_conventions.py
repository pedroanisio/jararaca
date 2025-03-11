"""
Check link for Python naming conventions.

This module contains the NamingConventionsCheck class which verifies that Python code
follows PEP 8 naming conventions.
"""

import os
import re
from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class NamingConventionsCheck(CheckLink):
    """
    Check link for Python naming conventions according to PEP 8.
    """

    def __init__(self):
        """Initialize a naming conventions check link."""
        super().__init__("Naming Conventions")

        # Regex patterns for different naming conventions
        self.module_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.class_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
        self.function_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.variable_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.constant_pattern = re.compile(r"^[A-Z][A-Z0-9_]*$")

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

                    # Check module name (file name)
                    module_name = os.path.splitext(file)[0]
                    if not self.module_pattern.match(module_name):
                        issues.append(
                            f"Module name '{module_name}' in {file_path} does not follow snake_case convention"
                        )

                    # Check file content for class, function, and variable names
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            file_issues = self._check_file_content(content, file_path)
                            issues.extend(file_issues)
                    except Exception as e:
                        issues.append(f"Error reading {file_path}: {str(e)}")

        # Determine the status based on issues found
        if issues:
            status = CheckStatus.FAILED
            details = "Naming convention issues found:\n" + "\n".join(issues)
        else:
            status = CheckStatus.PASSED
            details = "All code follows naming conventions."

        return [CheckResult(self.name, status, details)]

    def _check_file_content(self, content: str, file_path: str) -> List[str]:
        """
        Check the content of a file for naming convention issues.

        Args:
            content: The content of the file to check
            file_path: The path to the file being checked

        Returns:
            A list of naming convention issues found in the file
        """
        issues = []

        # Extract class definitions
        class_pattern = re.compile(r"class\s+([A-Za-z0-9_]+)")
        for match in class_pattern.finditer(content):
            class_name = match.group(1)
            if not self.class_pattern.match(class_name):
                issues.append(
                    f"Class name '{class_name}' in {file_path} does not follow PascalCase convention"
                )

        # Extract function definitions
        function_pattern = re.compile(r"def\s+([A-Za-z0-9_]+)")
        for match in function_pattern.finditer(content):
            function_name = match.group(1)
            # Skip special methods like __init__
            if function_name.startswith("__") and function_name.endswith("__"):
                continue
            if not self.function_pattern.match(function_name):
                issues.append(
                    f"Function name '{function_name}' in {file_path} does not follow snake_case convention"
                )

        # Extract variable assignments
        # This is a simplified approach and may not catch all variables
        variable_pattern = re.compile(r"([A-Za-z0-9_]+)\s*=")
        for match in variable_pattern.finditer(content):
            variable_name = match.group(1)
            # Skip special variables, imports, and function calls
            if (
                variable_name.startswith("__")
                or variable_name == "self"
                or variable_name == "cls"
                or variable_name in ["import", "from", "as", "class", "def"]
            ):
                continue

            # Check if it's a constant (all uppercase)
            if variable_name.isupper():
                if not self.constant_pattern.match(variable_name):
                    issues.append(
                        f"Constant '{variable_name}' in {file_path} does not follow UPPER_CASE convention"
                    )
            # Otherwise it should be a regular variable
            elif not self.variable_pattern.match(variable_name):
                issues.append(
                    f"Variable '{variable_name}' in {file_path} does not follow snake_case convention"
                )

        return issues
