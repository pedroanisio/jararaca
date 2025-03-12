"""
Check link for test coverage with pytest-cov.

This module contains the TestCoverageCheck class which verifies that Python code
has adequate test coverage.
"""

import re
from typing import Any, Dict, List, Optional

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class TestCoverageCheck(CheckLink):
    """
    Check link for test coverage with pytest-cov.
    """

    def __init__(self, min_coverage: int = 80):
        """
        Initialize a test coverage check link.

        Args:
            min_coverage: Minimum required coverage percentage (default: 80)
        """
        super().__init__("Test Coverage")
        self.min_coverage = min_coverage

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check test coverage using pytest-cov.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the coverage check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Join source dirs with commas for the --cov argument
        source_dirs_str = ",".join(source_dirs)

        # Build the command to run pytest with coverage
        command = [
            "pytest",
            f"--cov={source_dirs_str}",
            "--cov-report=term",
            "--cov-fail-under",
            str(self.min_coverage),
        ]

        # Run pytest with coverage
        result = run_command(command, cwd=project_path)

        # Parse the result to extract coverage percentage
        coverage_percentage = self._extract_coverage(result.stdout)

        if coverage_percentage is not None:
            if coverage_percentage >= self.min_coverage:
                status = CheckStatus.PASSED
                details = f"Test coverage is {coverage_percentage}%, which meets the minimum requirement of {self.min_coverage}%."
            else:
                status = CheckStatus.FAILED
                details = f"Test coverage is {coverage_percentage}%, which is below the minimum requirement of {self.min_coverage}%.\n{result.stdout}"
        else:
            status = CheckStatus.FAILED
            details = f"Failed to determine test coverage.\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        return [CheckResult(self.name, status, details)]

    def _extract_coverage(self, output: str) -> Optional[int]:
        """
        Extract the coverage percentage from the pytest-cov output.

        Args:
            output: The output from pytest-cov

        Returns:
            The coverage percentage as an integer, or None if it couldn't be extracted
        """
        # Look for a line like "TOTAL                             123     23    81%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return int(match.group(1))
        return None
