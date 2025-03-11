"""
Check link for code linting with Ruff.

This module contains the RuffCheck class which verifies that Python code
passes Ruff's code quality checks.
"""

from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class RuffCheck(CheckLink):
    """
    Check link for code linting with Ruff.
    """

    def __init__(self):
        """Initialize a Ruff check link."""
        super().__init__("Code Linting (Ruff)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check code quality using Ruff.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the Ruff check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Build the command to run ruff
        command = ["ruff", "check"]
        command.extend(source_dirs)

        # Run ruff
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All code passes Ruff checks."
        else:
            status = CheckStatus.FAILED
            details = f"Ruff issues found:\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
