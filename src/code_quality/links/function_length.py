"""
Function Length Check implementation for Python code.

This module provides a check that verifies Python functions do not exceed a maximum length.
"""

import ast
import os
from typing import Any, Dict, List, Tuple

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class FunctionVisitor(ast.NodeVisitor):
    """AST visitor that collects function definitions and their line lengths."""

    def __init__(self) -> None:
        """Initialize the function visitor."""
        self.functions: List[Tuple[str, int, int, int]] = (
            []
        )  # [(name, start_line, end_line, length)]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a function definition and record its length.

        Args:
            node: AST function definition node
        """
        start_line = node.lineno
        end_line = self._get_last_line(node)
        length = end_line - start_line + 1
        self.functions.append((node.name, start_line, end_line, length))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visit an async function definition and record its length.

        Args:
            node: AST async function definition node
        """
        start_line = node.lineno
        end_line = self._get_last_line(node)
        length = end_line - start_line + 1
        self.functions.append((node.name, start_line, end_line, length))
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a class definition and record method lengths.

        Args:
            node: AST class definition node
        """
        self.generic_visit(node)

    def _get_last_line(self, node: Any) -> int:
        """
        Get the last line of a node.

        Args:
            node: An AST node

        Returns:
            The last line number of the node
        """
        # Check if node has a lineno attribute
        if not hasattr(node, "lineno"):
            return 0

        max_line: int = node.lineno
        for child in ast.iter_child_nodes(node):
            if hasattr(child, "lineno"):
                max_line = max(max_line, child.lineno)
                if hasattr(child, "end_lineno") and child.end_lineno is not None:
                    max_line = max(max_line, child.end_lineno)
                child_last_line = self._get_last_line(child)
                max_line = max(max_line, child_last_line)
        return max_line


class FunctionLengthCheck(CheckLink):
    """
    Check that Python functions do not exceed a maximum length.

    This helps maintain code readability and maintainability by encouraging
    breaking down large functions into smaller, more focused functions.
    """

    def __init__(self, max_lines: int = 50):
        """
        Initialize the function length check.

        Args:
            max_lines: The maximum number of lines allowed per function.
        """
        super().__init__("Function Length")
        self.max_lines = max_lines

    def _process_file(self, file_path: str) -> List[Tuple[str, str, int]]:
        """
        Process a single file to find functions that exceed the maximum length.

        Args:
            file_path: Path to the file to process

        Returns:
            A list of tuples containing (file_path, function_name, line_count)
        """
        long_functions = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            try:
                tree = ast.parse(code)
                visitor = FunctionVisitor()
                visitor.visit(tree)

                for name, start_line, end_line, length in visitor.functions:
                    if length > self.max_lines:
                        long_functions.append((file_path, name, length))
            except SyntaxError as e:
                long_functions.append((file_path, f"Syntax error: {str(e)}", 0))
        except Exception as e:
            long_functions.append((file_path, f"Error: {str(e)}", 0))

        return long_functions

    def _format_result(
        self, long_functions: List[Tuple[str, str, int]]
    ) -> Tuple[CheckStatus, str]:
        """
        Format the result of the function length check.

        Args:
            long_functions: List of tuples containing (file_path, function_name, line_count)

        Returns:
            A tuple containing (status, details)
        """
        if long_functions:
            status = CheckStatus.FAILED
            details = (
                f"Functions exceeding the maximum length of {self.max_lines} lines:\n"
            )
            for file_path, func_name, line_count in long_functions:
                if line_count > 0:
                    details += f"- {file_path}: {func_name} ({line_count} lines)\n"
                else:
                    details += f"- {file_path}: {func_name}\n"
        else:
            status = CheckStatus.PASSED
            details = f"All functions are under {self.max_lines} lines"

        return status, details

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute the function length check.

        Args:
            context: A dictionary containing the context for the check, including project_path and source_dirs.

        Returns:
            A list of CheckResult objects indicating the result of the check.
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

        long_functions = []

        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    long_functions.extend(self._process_file(file_path))

        status, details = self._format_result(long_functions)
        return [CheckResult(self.name, status, details)]
