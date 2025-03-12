"""
Check link for code linting with Pylint.

This module contains the LintingCheck class which verifies that Python code
passes Pylint's code quality checks.
"""

from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class LintingCheck(CheckLink):
    """
    Check link for code linting with Pylint.
    """

    def __init__(self) -> None:
        """Initialize a linting check link."""
        super().__init__("Code Linting (Pylint)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check code quality using Pylint.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the linting check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Skip the check if no source directories exist
        if not source_dirs:
            return [
                CheckResult(
                    self.name,
                    CheckStatus.SKIPPED,
                    "No source directories found to check.",
                )
            ]

        # Build the command to run pylint
        command = ["pylint"]
        command.extend(source_dirs)

        # Run pylint
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All code passes linting checks."
        else:
            # Check if pylint command was not found
            if "No such file or directory" in result.stderr:
                status = CheckStatus.FAILED
                details = f"Linting failed: pylint command not found. Is it installed?\n{result.stderr}"
            # Pylint returns different exit codes based on the type of issues found
            # 0 means no errors, 1-15 means various types of issues
            elif result.returncode >= 16:
                status = CheckStatus.FAILED
                details = f"Linting failed with an error:\n{result.stderr}"
            else:
                status = CheckStatus.FAILED
                details = f"Linting issues found:\n{result.stdout}"
                if result.stderr:
                    details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
