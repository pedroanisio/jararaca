"""
Check link for security issues with Bandit.

This module contains the SecurityCheckLink class which verifies that Python code
is free from common security issues using Bandit.
"""

from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class SecurityCheckLink(CheckLink):
    """
    Check link for security issues with Bandit.
    """

    def __init__(self):
        """Initialize a security check link."""
        super().__init__("Security Check (Bandit)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check for security issues using Bandit.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the security check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Build the command to run bandit
        command = ["bandit", "-r"]
        command.extend(source_dirs)

        # Run bandit
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "No security issues found."
        else:
            status = CheckStatus.FAILED
            details = f"Security issues found:\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]
