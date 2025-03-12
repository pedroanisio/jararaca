"""
Check link for type checking with mypy.

This module contains the TypeCheckingLink class which verifies that Python code
passes mypy's type checking.
"""

from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class TypeCheckingLink(CheckLink):
    """
    Check link for type checking with mypy.
    """

    def __init__(self) -> None:
        """Initialize a type checking link."""
        super().__init__("Type Checking (mypy)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check type annotations using mypy.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the type checking.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Build the command to run mypy
        command = ["mypy"]
        command.extend(source_dirs)

        # Run mypy
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All code passes type checking."
        else:
            status = CheckStatus.FAILED
            details = f"Type checking issues found:\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
