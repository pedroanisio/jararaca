"""
Concrete implementations of code quality check links.

This module contains implementations of the CheckLink abstract base class
for specific code quality checks that can be chained together.
"""

import ast
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


class RuffCheck(CheckLink):
    """
    Check link for code linting with Ruff.
    """

    def __init__(self):
        """Initialize a Ruff linting check link."""
        super().__init__("Code Linting (Ruff)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check code linting using Ruff.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the Ruff linting check.
        """
        project_path = context.get("project_path", ".")

        # Check if the config setting has Ruff enabled
        config = context.get("config", {})
        check_ruff = config.get("check_ruff", "true").lower() == "true"

        if not check_ruff:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="Ruff linting check is disabled in configuration.",
                )
            ]

        # Run ruff
        command = [
            "ruff",
            "check",
            ".",
            "--exclude=venv,env,.venv,.env,.git,__pycache__,build,dist,*.egg-info",
        ]
        result = run_command(command, cwd=project_path)

        # Parse the result
        if result.returncode == 0:
            status = CheckStatus.PASSED
            details = "No Ruff linting issues found."
        else:
            status = CheckStatus.FAILED
            output = result.stdout or result.stderr

            # Add a helpful explanation for fixing common issues
            details = (
                f"Ruff linting issues found\n\n{output}\n\n"
                "How to fix:\n"
                "- Run 'ruff check --fix .' to automatically fix many issues\n"
                "- Ruff is a fast linter that can replace Flake8 and others\n"
                "- See https://docs.astral.sh/ruff/ for more details"
            )

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]


class TypeCheckingLink(CheckLink):
    """
    Check link for static type checking with mypy.
    """

    def __init__(self):
        """Initialize a static type checking link."""
        super().__init__("Static Type Checking (mypy)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check static types using mypy.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the results of static type checking for each source directory.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])
        config = context.get("config", {})

        # Check if mypy checking is enabled in config
        check_mypy = config.get("check_mypy", "true").lower() == "true"

        if not check_mypy:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="Static type checking is disabled in configuration.",
                )
            ]

        results = []
        for src_dir in source_dirs:
            src_path = os.path.join(project_path, src_dir)

            # Skip if the directory doesn't exist
            if not os.path.exists(src_path):
                results.append(
                    CheckResult(
                        name=f"{self.name} ({src_dir})",
                        status=CheckStatus.SKIPPED,
                        details=f"Source directory not found: {src_dir}",
                    )
                )
                continue

            # Run mypy
            command = ["mypy", src_dir]
            result = run_command(command, cwd=project_path)

            # Parse the result
            if result.returncode == 0:
                status = CheckStatus.PASSED
                details = f"No type errors found in {src_dir}"
            else:
                status = CheckStatus.FAILED
                output = result.stdout or result.stderr

                # Add a helpful explanation for fixing common type issues
                details = (
                    f"Type errors found in {src_dir}\n\n{output}\n\n"
                    "How to fix:\n"
                    "- Add proper type annotations to your functions and variables\n"
                    "- Use Optional[] for variables that can be None\n"
                    "- Add # type: ignore comments for legitimate exceptions\n"
                    "- See https://mypy.readthedocs.io/ for more information"
                )

            # Create the check result
            check_result = CheckResult(
                name=f"{self.name} ({src_dir})", status=status, details=details
            )
            print_rich_result(check_result)
            results.append(check_result)

        return results


class SecurityCheckLink(CheckLink):
    """
    Check link for security scanning with Bandit.
    """

    def __init__(self):
        """Initialize a security check link."""
        super().__init__("Security Check (Bandit)")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Perform security checks using Bandit.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the results of security checks for each source directory.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])
        config = context.get("config", {})

        # Check if bandit checking is enabled in config
        check_bandit = config.get("check_bandit", "true").lower() == "true"

        if not check_bandit:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="Security checking is disabled in configuration.",
                )
            ]

        results = []
        for src_dir in source_dirs:
            src_path = os.path.join(project_path, src_dir)

            # Skip if the directory doesn't exist
            if not os.path.exists(src_path):
                results.append(
                    CheckResult(
                        name=f"{self.name} ({src_dir})",
                        status=CheckStatus.SKIPPED,
                        details=f"Source directory not found for Bandit: {src_dir}",
                    )
                )
                continue

            # Run bandit
            command = ["bandit", "-r", src_dir]
            result = run_command(command, cwd=project_path)

            # Parse the result
            if result.returncode == 0:
                status = CheckStatus.PASSED
                details = f"No security issues found in {src_dir}"
            else:
                status = CheckStatus.FAILED
                output = result.stdout or result.stderr

                # Add a helpful explanation for fixing common security issues
                details = (
                    f"Security issues found in {src_dir}\n\n{output}\n\n"
                    "How to fix:\n"
                    "- Review the security issues identified and fix them\n"
                    "- Issues are categorized by severity (Low/Medium/High)\n"
                    "- See https://bandit.readthedocs.io/ for more details"
                )

            # Create the check result
            check_result = CheckResult(
                name=f"{self.name} ({src_dir})", status=status, details=details
            )
            print_rich_result(check_result)
            results.append(check_result)

        return results


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


class NamingConventionsCheck(CheckLink):
    """
    Check link for naming conventions.
    """

    def __init__(self):
        """Initialize a naming conventions check link."""
        super().__init__("Naming Conventions")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check naming conventions for files, classes, functions, and variables.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the naming conventions check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])

        python_files = self._get_python_files(project_path, source_dirs)

        if not python_files:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="No Python files found in source directories.",
                )
            ]

        # Python keywords that shouldn't be considered violations
        python_keywords = {
            "and",
            "as",
            "assert",
            "async",
            "await",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "nonlocal",
            "not",
            "or",
            "pass",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
            "False",
            "None",
            "True",
        }

        violations = []
        file_violations = []
        class_violations = []
        function_violations = []
        variable_violations = []

        for file_path in python_files:
            relative_path = os.path.relpath(file_path, project_path)
            file_name = os.path.basename(file_path)

            # Skip checking special files like __init__.py and __main__.py
            if not file_name.startswith("__") and not re.match(
                r"^[a-z][a-z0-9_]*\.py$", file_name
            ):
                file_violations.append(
                    f"[yellow]{relative_path}[/yellow]: File should be in snake_case"
                )

            # Parse the Python file to check names inside it
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    tree = ast.parse(content)

                    # Check class names
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = node.name
                            if class_name not in python_keywords and not re.match(
                                r"^[A-Z][A-Za-z0-9]*$", class_name
                            ):
                                class_violations.append(
                                    f"[yellow]{relative_path}[/yellow]: Class [red]{class_name}[/red] should be in PascalCase"
                                )

                        # Check function names
                        elif isinstance(node, ast.FunctionDef):
                            func_name = node.name
                            # Skip magic methods and private methods
                            if not func_name.startswith("__") and not re.match(
                                r"^[a-z][a-z0-9_]*$", func_name
                            ):
                                function_violations.append(
                                    f"[yellow]{relative_path}[/yellow]: Function [red]{func_name}[/red] should be in snake_case"
                                )

                        # Check variable assignments at module level (constants)
                        elif (
                            isinstance(node, ast.Assign)
                            and isinstance(node.targets[0], ast.Name)
                            and isinstance(node.parent, ast.Module)
                        ):
                            var_name = node.targets[0].id
                            # Check if the variable is all caps (should be a constant)
                            if re.match(r"^[A-Z][A-Z0-9_]*$", var_name):
                                # This is fine - constants should be UPPER_CASE
                                pass
                            # Check if the variable is not snake_case
                            elif not re.match(
                                r"^[a-z][a-z0-9_]*$", var_name
                            ) and not var_name.startswith("_"):
                                variable_violations.append(
                                    f"[yellow]{relative_path}[/yellow]: Variable [red]{var_name}[/red] should be in snake_case"
                                )
            except Exception as e:
                violations.append(
                    f"Error checking naming conventions in {relative_path}: {str(e)}"
                )

        # Determine overall status
        if (
            file_violations
            or class_violations
            or function_violations
            or variable_violations
        ):
            status = CheckStatus.FAILED
            details = "Naming convention violations found:\n\n"

            if file_violations:
                details += (
                    "File naming violations:\n" + "\n".join(file_violations) + "\n\n"
                )
            if class_violations:
                details += (
                    "Class naming violations:\n" + "\n".join(class_violations) + "\n\n"
                )
            if function_violations:
                details += (
                    "Function naming violations:\n"
                    + "\n".join(function_violations)
                    + "\n\n"
                )
            if variable_violations:
                details += (
                    "Variable naming violations:\n"
                    + "\n".join(variable_violations)
                    + "\n\n"
                )

            details += (
                "Naming conventions:\n"
                "- Files: snake_case.py\n"
                "- Classes: PascalCase\n"
                "- Functions: snake_case\n"
                "- Variables: snake_case\n"
                "- Constants: UPPER_CASE"
            )
        else:
            status = CheckStatus.PASSED
            details = "All naming conventions are followed."

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]

    def _get_python_files(self, project_path: str, source_dirs: List[str]) -> List[str]:
        """
        Get all Python files from the source directories.

        Args:
            project_path: The path to the project
            source_dirs: List of source directories to check

        Returns:
            List of paths to Python files
        """
        python_files = []
        for src_dir in source_dirs:
            full_path = os.path.join(project_path, src_dir)
            if os.path.exists(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))

        return python_files


class FileLengthCheck(CheckLink):
    """
    Check link for file length limits.
    """

    def __init__(self, max_length: int = 300):
        """
        Initialize a file length check link.

        Args:
            max_length: Maximum allowed lines per file (default: 300).
        """
        super().__init__("File Lengths")
        self.max_length = max_length

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check file lengths against the maximum allowed lines.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the file length check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])
        config = context.get("config", {})

        # Get max file length from config, if provided
        max_length = int(config.get("max_file_length", str(self.max_length)))

        python_files = self._get_python_files(project_path, source_dirs)

        if not python_files:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="No Python files found in source directories.",
                )
            ]

        violations = []
        for file_path in python_files:
            relative_path = os.path.relpath(file_path, project_path)

            with open(file_path, "r") as f:
                lines = f.readlines()
                line_count = len(lines)

                if line_count > max_length:
                    percent_over = (line_count - max_length) / max_length * 100
                    violations.append(
                        f"{relative_path}: {line_count} lines (exceeds max of {max_length} by {percent_over:.1f}%)"
                    )

        if violations:
            status = CheckStatus.FAILED
            details = (
                "File length violations found\n\n"
                "Files exceeding maximum length ({max_length} lines):\n"
                f"{os.path.join(project_path, violations[0] if violations else '')}\n\n"
                "How to fix:\n"
                "- Consider breaking large files into smaller, focused modules\n"
                "- Move related helper functions to a separate utility file\n"
                "- Review and refactor long files to improve code organization"
            ).format(max_length=max_length)
        else:
            status = CheckStatus.PASSED
            details = f"All files are within the maximum length of {max_length} lines."

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]

    def _get_python_files(self, project_path: str, source_dirs: List[str]) -> List[str]:
        """
        Get all Python files from the source directories.

        Args:
            project_path: The path to the project
            source_dirs: List of source directories to check

        Returns:
            List of paths to Python files
        """
        python_files = []
        for src_dir in source_dirs:
            full_path = os.path.join(project_path, src_dir)
            if os.path.exists(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))

        return python_files


class FunctionLengthCheck(CheckLink):
    """
    Check link for function length limits.
    """

    def __init__(self, max_length: int = 50):
        """
        Initialize a function length check link.

        Args:
            max_length: Maximum allowed lines per function (default: 50).
        """
        super().__init__("Function Lengths")
        self.max_length = max_length

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check function lengths against the maximum allowed lines.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the function length check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])
        config = context.get("config", {})

        # Get max function length from config, if provided
        max_length = int(config.get("max_function_length", str(self.max_length)))

        python_files = self._get_python_files(project_path, source_dirs)

        if not python_files:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="No Python files found in source directories.",
                )
            ]

        class FunctionVisitor(ast.NodeVisitor):
            """AST visitor to extract function definitions and their lengths."""

            def __init__(self):
                self.functions = []

            def visit_FunctionDef(self, node):
                """Visit function definitions and record their lengths."""
                # Get function name
                function_name = node.name

                # Get function line range
                start_line = node.lineno
                end_line = (
                    node.end_lineno
                    if hasattr(node, "end_lineno")
                    else self._find_last_line(node)
                )

                # Calculate function length
                function_length = end_line - start_line + 1

                self.functions.append((function_name, function_length))

                # Continue visiting child nodes
                self.generic_visit(node)

            def _find_last_line(self, node):
                """Find the last line of a node by traversing its children."""
                max_line = node.lineno
                for child in ast.iter_child_nodes(node):
                    if hasattr(child, "lineno"):
                        max_line = max(max_line, child.lineno)
                        if hasattr(child, "end_lineno"):
                            max_line = max(max_line, child.end_lineno)
                        else:
                            max_line = max(max_line, self._find_last_line(child))
                return max_line

        violations_by_file = {}

        for file_path in python_files:
            relative_path = os.path.relpath(file_path, project_path)

            try:
                with open(file_path, "r") as f:
                    code = f.read()

                tree = ast.parse(code)
                visitor = FunctionVisitor()
                visitor.visit(tree)

                file_violations = []
                for func_name, func_length in visitor.functions:
                    if func_length > max_length:
                        percent_over = (func_length - max_length) / max_length * 100
                        file_violations.append(
                            f"  • {func_name}: {func_length} lines (exceeds max by {percent_over:.1f}%)"
                        )

                if file_violations:
                    violations_by_file[relative_path] = file_violations

            except Exception as e:
                violations_by_file[relative_path] = [
                    f"  • Error parsing file: {str(e)}"
                ]

        if violations_by_file:
            status = CheckStatus.FAILED
            details = "Function length violations found\n\n"

            for file_path, violations in violations_by_file.items():
                details += f"{file_path} ({os.path.join(project_path, file_path)}):\n"
                details += "\n".join(violations) + "\n\n"

            details += (
                "How to fix:\n"
                "- Break large functions into smaller, focused helper functions\n"
                "- Extract repeated code patterns into reusable functions\n"
                "- Consider using class methods to organize related functionality\n"
                f"- Functions should ideally be less than {max_length} lines for better readability"
            )
        else:
            status = CheckStatus.PASSED
            details = (
                f"All functions are within the maximum length of {max_length} lines."
            )

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]

    def _get_python_files(self, project_path: str, source_dirs: List[str]) -> List[str]:
        """
        Get all Python files from the source directories.

        Args:
            project_path: The path to the project
            source_dirs: List of source directories to check

        Returns:
            List of paths to Python files
        """
        python_files = []
        for src_dir in source_dirs:
            full_path = os.path.join(project_path, src_dir)
            if os.path.exists(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))

        return python_files


class DocstringCheck(CheckLink):
    """
    Check link for docstring completeness.
    """

    def __init__(self):
        """Initialize a docstring check link."""
        super().__init__("Docstrings")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check for proper docstrings in classes and functions.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the result of the docstring check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src", "app"])

        python_files = self._get_python_files(project_path, source_dirs)

        if not python_files:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.SKIPPED,
                    details="No Python files found in source directories.",
                )
            ]

        class DocstringVisitor(ast.NodeVisitor):
            """AST visitor to check for docstrings in classes and functions."""

            def __init__(self):
                self.missing_docstrings = []
                self.current_file = ""

            def set_file(self, file_path: str) -> None:
                """Set the current file being processed."""
                self.current_file = file_path

            def visit_ClassDef(self, node):
                """Visit class definitions and check for docstrings."""
                if not ast.get_docstring(node):
                    self.missing_docstrings.append(
                        f"Class '{node.name}' in {self.current_file} (line {node.lineno})"
                    )
                self.generic_visit(node)

            def visit_FunctionDef(self, node):
                """Visit function definitions and check for docstrings."""
                # Skip private methods and functions
                if node.name.startswith("_") and not node.name.startswith("__"):
                    self.generic_visit(node)
                    return

                if not ast.get_docstring(node):
                    # Determine if this is a method or a function
                    is_method = False
                    for parent in ast.walk(ast.parse(open(self.current_file).read())):
                        if isinstance(parent, ast.ClassDef) and node in parent.body:
                            is_method = True
                            self.missing_docstrings.append(
                                f"Method '{parent.name}.{node.name}' in {self.current_file} (line {node.lineno})"
                            )
                            break

                    if not is_method:
                        self.missing_docstrings.append(
                            f"Function '{node.name}' in {self.current_file} (line {node.lineno})"
                        )

                self.generic_visit(node)

        visitor = DocstringVisitor()

        for file_path in python_files:
            relative_path = os.path.relpath(file_path, project_path)

            try:
                with open(file_path, "r") as f:
                    code = f.read()

                visitor.set_file(relative_path)
                tree = ast.parse(code)
                visitor.visit(tree)

            except Exception as e:
                visitor.missing_docstrings.append(
                    f"Error parsing {relative_path}: {str(e)}"
                )

        if visitor.missing_docstrings:
            status = CheckStatus.FAILED
            details = (
                "Missing docstrings found:\n\n"
                f"{os.linesep.join('• ' + d for d in visitor.missing_docstrings)}\n\n"
                "How to fix:\n"
                "- Add docstrings to all public classes and functions\n"
                "- Follow PEP 257 for docstring conventions\n"
                "- Include description, args, returns, and raises sections in function docstrings\n"
                "- Include class purpose and attributes in class docstrings"
            )
        else:
            status = CheckStatus.PASSED
            details = "All classes and functions have proper docstrings."

        # Create and return the check result
        check_result = CheckResult(name=self.name, status=status, details=details)
        print_rich_result(check_result)

        return [check_result]

    def _get_python_files(self, project_path: str, source_dirs: List[str]) -> List[str]:
        """
        Get all Python files from the source directories.

        Args:
            project_path: The path to the project
            source_dirs: List of source directories to check

        Returns:
            List of paths to Python files
        """
        python_files = []
        for src_dir in source_dirs:
            full_path = os.path.join(project_path, src_dir)
            if os.path.exists(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))

        return python_files


class DependencyCheck(CheckLink):
    """
    Check link for dependency management and security.
    """

    def __init__(self):
        """Initialize a dependency check link."""
        super().__init__("Dependency Management")

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check for dependency management files and security issues.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing the results of the dependency checks.
        """
        project_path = context.get("project_path", ".")

        # List of common dependency files
        dependency_files = [
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "poetry.lock",
        ]

        # Check if any dependency files exist
        found_files = []
        for file in dependency_files:
            if os.path.exists(os.path.join(project_path, file)):
                found_files.append(file)

        if not found_files:
            return [
                CheckResult(
                    name=self.name,
                    status=CheckStatus.FAILED,
                    details=(
                        "No dependency management files found.\n\n"
                        "How to fix:\n"
                        "- Create a requirements.txt file listing all dependencies\n"
                        "- Or use modern tools like Poetry or Pipenv for dependency management\n"
                        "- Include all production and development dependencies"
                    ),
                )
            ]

        # Dependency file check passed, now check for security issues
        dependency_result = CheckResult(
            name=self.name,
            status=CheckStatus.PASSED,
            details=f"Found dependency files: {', '.join(found_files)}",
        )
        print_rich_result(dependency_result)

        security_results = self._check_dependency_security(project_path, found_files)

        # Return both results
        return [dependency_result] + security_results

    def _check_dependency_security(
        self, project_path: str, found_files: List[str]
    ) -> List[CheckResult]:
        """
        Check dependencies for security vulnerabilities.

        Args:
            project_path: The path to the project
            found_files: List of dependency management files found

        Returns:
            List of check results for dependency security
        """
        results = []

        # First, check if pip-audit is installed
        try:
            requirements_file = (
                "requirements.txt"
                if "requirements.txt" in found_files
                else found_files[0]
            )
            command = ["pip-audit", "-r", requirements_file]
            result = run_command(command, cwd=project_path)

            if result.returncode == 0:
                status = CheckStatus.PASSED
                details = "No security vulnerabilities found in dependencies."
            else:
                status = CheckStatus.FAILED
                output = result.stdout or result.stderr

                details = (
                    f"Security vulnerabilities found in dependencies\n\n"
                    f"{output}\n\n"
                    "How to fix:\n"
                    "- Update vulnerable dependencies to newer versions\n"
                    "- Run 'pip-audit -r requirements.txt --fix' to automatically fix issues\n"
                    "- Check for security advisories at https://pypi.org/security-advisories/"
                )

            security_result = CheckResult(
                name="Dependency Security", status=status, details=details
            )
            print_rich_result(security_result)
            results.append(security_result)

        except Exception as e:
            # If pip-audit is not installed or fails, provide info but don't fail the check
            security_result = CheckResult(
                name="Dependency Security",
                status=CheckStatus.SKIPPED,
                details=(
                    f"Could not check dependency security: {str(e)}\n\n"
                    "How to fix:\n"
                    "- Install pip-audit: pip install pip-audit\n"
                    "- Or install safety: pip install safety\n"
                    "- Run security checks regularly to identify vulnerabilities"
                ),
            )
            print_rich_result(security_result)
            results.append(security_result)

        return results
