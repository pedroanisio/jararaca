"""
Check link for code formatting with Black.

This module contains the FormattingCheck class which verifies that Python code
is properly formatted according to Black's standards.
"""

import os
from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class FormattingCheck(CheckLink):
    """
    Check link for code formatting with Black.
    """

    def __init__(self):
        """Initialize a formatting check link."""
        super().__init__("Code Formatting (Black)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check code formatting using Black.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the formatting check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Build the command to run black in check mode
        command = ["black", "--check"]
        command.extend(source_dirs)

        # Run black in check mode
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All code is properly formatted."
        else:
            status = CheckStatus.FAILED
            details = f"Files need formatting:\n{result.stdout}"
            if "error" in result.stderr.lower():
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
