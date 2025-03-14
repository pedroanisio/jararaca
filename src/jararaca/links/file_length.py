"""
File Length Check implementation for Python code.

This module provides a check that verifies Python files do not exceed a maximum length.
"""

import logging
import os
from typing import Any, Dict, List, Tuple, Union

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus

# Define a type alias for the file and line count tuple
file_length_entry = Tuple[str, Union[int, str]]


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

    def _process_file(self, file_path: str) -> Tuple[bool, Union[int, str]]:
        """
        Process a single file to check its length.

        Args:
            file_path: Path to the file to check

        Returns:
            A tuple containing (is_too_long, line_count_or_error)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                line_count: int = len(lines)
                return line_count > self.max_lines, line_count
        except Exception as e:
            # Use a string for error messages
            error_msg: str = f"Error: {str(e)}"
            logging.error(f"Error reading {file_path}: {str(e)}")
            return True, error_msg

    def _format_result(
        self, long_files: List[file_length_entry]
    ) -> Tuple[CheckStatus, str]:
        """
        Format the result of the file length check.

        Args:
            long_files: List of tuples containing (file_path, line_count)

        Returns:
            A tuple containing (status, details)
        """
        if long_files:
            status = CheckStatus.FAILED
            details = f"Files exceeding the maximum length of {self.max_lines} lines:\n"

            # Access tuple elements safely
            for entry in long_files:
                # Use our specific type annotation
                entry_file_path: str = entry[0]
                # line_count can be int or str, and that's handled by our type alias
                entry_line_val = entry[1]
                details += f"- {entry_file_path}: {entry_line_val} lines\n"
        else:
            status = CheckStatus.PASSED
            details = (
                f"All files are under the maximum length of {self.max_lines} lines."
            )

        return status, details

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
        # Each entry is (file_path, line_count) where line_count can be int or str
        long_files: List[file_length_entry] = []

        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    is_too_long, line_count = self._process_file(file_path)
                    if is_too_long:
                        long_files.append((file_path, line_count))

        # Determine the status based on long files found
        status, details = self._format_result(long_files)
        return [CheckResult(name=self.name, status=status, details=details)]
