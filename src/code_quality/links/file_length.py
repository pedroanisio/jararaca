"""
File Length Check implementation for Python code.

This module provides a check that verifies Python files do not exceed a maximum length.
"""

import os
from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class FileLengthCheck(CheckLink):
    """
    Check that Python files do not exceed a maximum length.

    This helps maintain code readability and modularity by encouraging
    breaking down large files into smaller, more focused modules.
    """

    def __init__(self, max_lines: int = 500):
        """
        Initialize the file length check.

        Args:
            max_lines: The maximum number of lines allowed per file.
        """
        super().__init__("File Length")
        self.max_lines = max_lines

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check file lengths in Python files.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the file length check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        long_files = []

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

                    # Count the number of lines in the file
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            line_count = sum(1 for _ in f)

                        if line_count > self.max_lines:
                            long_files.append((file_path, line_count))
                    except Exception as e:
                        # If we can't read the file, we'll consider it a failure
                        long_files.append((file_path, f"Error: {str(e)}"))

        # Determine the status based on long files found
        if long_files:
            status = CheckStatus.FAILED
            details = f"Files exceeding the maximum length of {self.max_lines} lines:\n"
            for file_path, line_count in long_files:
                details += f"- {file_path}: {line_count} lines\n"
        else:
            status = CheckStatus.PASSED
            details = (
                f"All files are under the maximum length of {self.max_lines} lines."
            )

        return [CheckResult(self.name, status, details)]
