"""
Docstring Check implementation for Python code.

This module provides a check that verifies Python modules, classes, and functions have proper docstrings.
"""

import ast
import os
from typing import Any, Dict, List, Tuple

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class DocstringVisitor(ast.NodeVisitor):
    """AST visitor that checks for missing docstrings in modules, classes, and functions."""

    def __init__(self, skip_private: bool = True) -> None:
        """
        Initialize the docstring visitor.

        Args:
            skip_private: Whether to skip checking private methods/functions
        """
        self.missing_docstrings: List[Tuple[str, str, int]] = (
            []
        )  # (type, name, line_number)
        self.skip_private = skip_private
        self.has_module_docstring = False

    def visit_Module(self, node: ast.Module) -> None:
        """
        Visit a module node and check if it has a docstring.

        Args:
            node: AST module node
        """
        if ast.get_docstring(node):
            self.has_module_docstring = True
        else:
            # Modules don't have line numbers in AST, use 1 as default
            self.missing_docstrings.append(("module", "__init__", 1))
        # Continue visiting the rest of the module
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit a class definition and check if it has a docstring.

        Args:
            node: AST class definition node
        """
        if not ast.get_docstring(node) and not (
            self.skip_private and node.name.startswith("_")
        ):
            self.missing_docstrings.append(("class", node.name, node.lineno))
        # Continue visiting the class contents
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Visit a function definition and check if it has a docstring.

        Args:
            node: AST function definition node
        """
        # Skip checking "private" functions starting with underscore if configured to do so
        if (
            self.skip_private
            and node.name.startswith("_")
            and not (node.name.startswith("__") and node.name.endswith("__"))
        ):
            self.generic_visit(node)
            return

        if not ast.get_docstring(node) and not (
            self.skip_private and node.name.startswith("_")
        ):
            self.missing_docstrings.append(("function", node.name, node.lineno))

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """
        Visit an async function definition and check if it has a docstring.

        Args:
            node: AST async function definition node
        """
        # Skip checking "private" functions starting with underscore if configured to do so
        if (
            self.skip_private
            and node.name.startswith("_")
            and not (node.name.startswith("__") and node.name.endswith("__"))
        ):
            self.generic_visit(node)
            return

        if not ast.get_docstring(node) and not (
            self.skip_private and node.name.startswith("_")
        ):
            self.missing_docstrings.append(("async function", node.name, node.lineno))

        self.generic_visit(node)


class DocstringCheck(CheckLink):
    """
    Check that Python modules, classes, and functions have proper docstrings.

    This helps maintain code documentation and makes the codebase more maintainable.
    """

    def __init__(self, skip_private: bool = True, skip_test_files: bool = True):
        """
        Initialize the docstring check.

        Args:
            skip_private: Whether to skip checking private functions and methods.
            skip_test_files: Whether to skip checking test files.
        """
        super().__init__("Docstring Check")
        self.skip_private = skip_private
        self.skip_test_files = skip_test_files

    def _process_python_file(self, file_path: str) -> List[Tuple[str, str, int]]:
        """
        Process a Python file to find missing docstrings.

        Args:
            file_path: Path to the Python file to process

        Returns:
            List of tuples containing (file_path, element_description, line_number)
        """
        missing_docstrings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)
            visitor = DocstringVisitor(skip_private=self.skip_private)
            visitor.visit(tree)

            for element_type, name, line_no in visitor.missing_docstrings:
                if element_type == "module":
                    missing_docstrings.append((file_path, "module", line_no))
                else:
                    missing_docstrings.append(
                        (file_path, f"{element_type} '{name}'", line_no)
                    )
        except SyntaxError as e:
            missing_docstrings.append((file_path, f"Syntax error: {str(e)}", 0))
        except Exception as e:
            missing_docstrings.append((file_path, f"Error: {str(e)}", 0))

        return missing_docstrings

    def _format_result(
        self, missing_docstrings: List[Tuple[str, str, int]]
    ) -> Tuple[CheckStatus, str]:
        """
        Format the result of the docstring check.

        Args:
            missing_docstrings: List of tuples containing (file_path, element_description, line_number)

        Returns:
            A tuple containing (status, details)
        """
        if missing_docstrings:
            status = CheckStatus.FAILED
            details = "Missing docstrings found:\n"
            for file_path, element, line_no in missing_docstrings:
                if line_no > 0:
                    details += f"- {file_path}:{line_no} - {element}\n"
                else:
                    details += f"- {file_path}: {element}\n"
        else:
            status = CheckStatus.PASSED
            details = "All modules, classes, and functions have docstrings."

        return status, details

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check for missing docstrings in Python files.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the docstring check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        missing_docstrings = []

        # Process each source directory
        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            # Walk through directory and process each Python file
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    if self.skip_test_files and (
                        "test_" in file or file.startswith("test")
                    ):
                        continue

                    file_path = os.path.join(root, file)
                    missing_docstrings.extend(self._process_python_file(file_path))

        # Generate result based on findings
        status, details = self._format_result(missing_docstrings)
        return [CheckResult(self.name, status, details)]
