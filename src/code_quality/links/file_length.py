"""
File Length Check implementation for Python code.

This module provides a check that verifies Python files do not exceed a maximum length.
"""

import logging
import os
from typing import Any, Dict, List, Tuple, Union

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class FileLengthCheck(CheckLink):
    """
    Check that Python files do not exceed a maximum length.

    This helps maintain code readability and modularity by encouraging
    breaking down large files into smaller, more focused modules.
    """

    def __init__(self, max_lines: int = 300):
        """
        Initialize the file length check.

        Args:
            max_lines: The maximum number of lines allowed per file.
        """
        super().__init__("File Length")
        self.max_lines = max_lines

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute the file length check.

        Args:
            context: A dictionary containing the execution context, including:
                - project_path: Path to the project to check
                - source_dirs: List of directories to check (relative to project_path)

        Returns:
            A list containing one CheckResult with the check outcome.
        """
        project_path = context.get("project_path", "")
        source_dirs = context.get("source_dirs", ["src"])

        if not project_path:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.FAILED,
                    details="No project path provided",
                )
            ]

        # List to store files exceeding the max length
        # Tuple contains (file_path, line_count) where line_count can be int or str (for errors)
        long_files: List[Tuple[str, Union[int, str]]] = []

        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            line_count = len(lines)
                            if line_count > self.max_lines:
                                long_files.append((file_path, line_count))
                    except Exception as e:
                        # Use a string message with 'Error:' to maintain backward compatibility with tests
                        long_files.append((file_path, f"Error: {str(e)}"))
                        logging.error(f"Error reading {file_path}: {str(e)}")

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

        return [CheckResult(name=self.name, status=status, details=details)]
