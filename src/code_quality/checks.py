"""
Concrete implementations of code quality check links.

This module contains implementations of the CheckLink abstract base class
for specific code quality checks that can be chained together.
"""

import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from .chain import CheckLink
from .utils import CheckResult, CheckStatus, print_rich_result, run_command


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

        Returns:
            A list containing the result of the formatting check.
        """
        project_path = context.get("project_path", ".")

        # Run black in check mode
        command = ["black", "--check", "."]
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

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]


class ImportsCheck(CheckLink):
    """
    Check link for import sorting with isort.
    """

    def __init__(self):
        """Initialize an imports check link."""
        super().__init__("Import Sorting (isort)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check import sorting using isort.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the import sorting check.
        """
        project_path = context.get("project_path", ".")

        # Run isort in check mode
        command = ["isort", "--check", "--profile", "black", "."]
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "All imports are properly sorted."
        else:
            status = CheckStatus.FAILED
            details = f"Import sorting issues found:\n{result.stdout}"
            if result.stderr:
                details += f"\nErrors:\n{result.stderr}"

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]


class LintingCheck(CheckLink):
    """
    Check link for code linting with Flake8.
    """

    def __init__(self):
        """Initialize a linting check link."""
        super().__init__("Code Linting (Flake8)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check code linting using Flake8.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the linting check.
        """
        project_path = context.get("project_path", ".")

        # Run flake8
        command = [
            "flake8",
            "--exclude=venv,env,.venv,.env,.git,__pycache__,build,dist,*.egg-info",
        ]
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "No linting issues found."
        else:
            status = CheckStatus.FAILED
            output = result.stdout or result.stderr

            # Add a helpful explanation for fixing common issues
            details = (
                f"Flake8 linting issues found\n\n{output}\n\n"
                "How to fix:\n"
                "- Run 'flake8 --fix' to automatically fix some issues\n"
                "- E*** errors are style issues (indentation, whitespace)\n"
                "- F*** errors are logical issues (unused imports, variables)\n"
                "- W*** errors are warnings (deprecated features, etc.)"
            )

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]


class TestCoverageCheck(CheckLink):
    """
    Check link for test coverage.
    """

    def __init__(self, min_coverage: int = 80):
        """
        Initialize a test coverage check link.

        Args:
            min_coverage: The minimum required coverage percentage (default: 80).
        """
        super().__init__("Test Coverage")
        self.min_coverage = min_coverage

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check test coverage using coverage.py.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the coverage check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        # Run coverage
        coverage_cmd = [
            "coverage",
            "run",
            "--source",
            ",".join(source_dirs),
            "-m",
            "pytest",
        ]
        coverage_result = run_command(coverage_cmd, cwd=project_path)

        if coverage_result.returncode != 0:
            status = CheckStatus.FAILED
            details = (
                f"Test run failed:\n{coverage_result.stdout}\n{coverage_result.stderr}"
            )
            check_result = CheckResult(name=self.name, status=status, details=details)
            print_rich_result(check_result)
            return [check_result]

        # Generate coverage report
        report_cmd = ["coverage", "report", "-m"]
        report_result = run_command(report_cmd, cwd=project_path)

        if report_result.returncode != 0:
            status = CheckStatus.FAILED
            details = f"Coverage report generation failed:\n{report_result.stdout}\n{report_result.stderr}"
            check_result = CheckResult(name=self.name, status=status, details=details)
            print_rich_result(check_result)
            return [check_result]

        # Parse coverage output
        try:
            coverage_output = report_result.stdout
            # Extract the total coverage percentage
            total_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", coverage_output)

            if not total_match:
                status = CheckStatus.FAILED
                details = f"Could not parse coverage output:\n{coverage_output}"
            else:
                coverage_percentage = int(total_match.group(1))

                if coverage_percentage >= self.min_coverage:
                    status = CheckStatus.PASSED
                    details = f"Coverage: {coverage_percentage}% (meets minimum {self.min_coverage}%)\n\n{coverage_output}"
                else:
                    status = CheckStatus.FAILED

                    # Find files with low coverage
                    low_coverage_files = []
                    for line in coverage_output.splitlines():
                        if "%" in line and "TOTAL" not in line:
                            parts = line.split()
                            if len(parts) >= 4:
                                file_path = parts[0]
                                file_coverage = int(parts[-1].strip("%"))
                                if file_coverage < self.min_coverage:
                                    low_coverage_files.append(
                                        f"{file_path}: {file_coverage}% coverage"
                                    )

                    details = (
                        f"Coverage: {coverage_percentage}% below minimum {self.min_coverage}%\n\n"
                        "Files needing more test coverage:\n"
                    )

                    if low_coverage_files:
                        details += "\n".join(low_coverage_files) + "\n\n"

                    details += "How to fix: Add more unit tests for the files listed above, focusing on the missing lines."

        except Exception as e:
            status = CheckStatus.FAILED
            details = f"Error processing coverage report: {str(e)}\n\n{coverage_output}"

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]
