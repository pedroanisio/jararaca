"""
Check link for import sorting with isort.

This module contains the ImportsCheck class which verifies that Python imports
are properly sorted according to isort's standards.
"""

from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class ImportsCheck(CheckLink):
    """
    Check link for import sorting with isort.
    """

    def __init__(self) -> None:
        """Initialize an imports check link."""
        super().__init__("Import Sorting (isort)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check import sorting using isort.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the imports check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Build the command to run isort in check mode
        command = ["isort", "--check-only", "--diff"]
        command.extend(source_dirs)

        # Run isort in check mode
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All imports are properly sorted."
        else:
            status = CheckStatus.FAILED
            details = f"Imports need sorting:\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
