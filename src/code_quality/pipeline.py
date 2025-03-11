"""
Python Code Quality Pipeline

A comprehensive validation tool that checks Python code against established
development standards and guidelines. Validates code structure, style, quality,
and testing before automating branch management and commits.
"""

import argparse
import configparser
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .utils import Colors, format_result_output, run_command

# Configure logging
logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Status of a quality check."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class CheckResult:
    """Result of a single quality check."""

    name: str
    status: CheckStatus
    details: str = ""


class CodeQualityPipeline:
    """
    Code Quality Pipeline for Python projects.

    Runs a series of checks to ensure code quality and adherence to
    development standards and guidelines.
    """

    def __init__(self, project_path: str, config_file: Optional[str] = None):
        """
        Initialize the code quality pipeline.

        Args:
            project_path: Path to the Python project
            config_file: Optional path to configuration file
        """
        self.project_path = os.path.abspath(project_path)
        self.results: List[CheckResult] = []
        self.load_config(config_file)
        self._check_prerequisites()

    def load_config(self, config_file: Optional[str]) -> None:
        """
        Load configuration from file or use defaults.

        Args:
            config_file: Path to the configuration file
        """
        logger.info("Loading configuration.")
        self.config = configparser.ConfigParser()
        # Default configuration
        self.config["general"] = {
            "min_test_coverage": "80",
            "max_file_length": "300",
            "max_function_length": "50",
            "check_bandit": "true",
            "check_mypy": "true",
            "check_ruff": "true",
            "main_branch": "main",
            "enable_auto_commit": "false",
        }
        self.config["paths"] = {
            "src_dirs": "src,app",
            "test_dir": "tests",
            "exclude_dirs": "venv,.venv,__pycache__,build,dist",
        }
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
            logger.info(f"Configuration loaded from {config_file}.")
        else:
            logger.info("Using default configuration.")

    def _run_command(self, command: List[str]) -> subprocess.CompletedProcess:
        """
        Helper to run shell commands in the project path.

        Args:
            command: Command to run as a list of strings

        Returns:
            CompletedProcess instance with command output
        """
        return run_command(command, self.project_path)

    def _check_prerequisites(self) -> None:
        """Check that all required tools are installed."""
        logger.info("Checking required tools.")
        required_tools = [
            "pytest",
            "black",
            "isort",
            "flake8",
            "mypy",
            "coverage",
            "git",
        ]
        for tool in required_tools:
            try:
                subprocess.run(["which", tool], check=True, capture_output=True)
                logger.info(f"Tool found: {tool}")
            except subprocess.CalledProcessError:
                logger.error(f"Required tool '{tool}' not found. Please install it.")
                print(
                    f"{Colors.FAIL}Required tool '{tool}' not found. Please install it.{Colors.ENDC}"
                )
                sys.exit(1)
        logger.info(f"{Colors.GREEN}✓ All required tools are installed.{Colors.ENDC}")

    def run_all_checks(self) -> bool:
        """
        Run all checks and return True if all (non-skipped) tests passed.

        Returns:
            True if all checks passed, False otherwise
        """
        self.results = []
        logger.info("Starting Python Code Quality Pipeline.")
        print(
            f"\n{Colors.HEADER}{Colors.BOLD}Running Python Code Quality Pipeline{Colors.ENDC}"
        )
        print(f"{Colors.BLUE}Project path: {self.project_path}{Colors.ENDC}\n")

        self._check_formatting()
        self._check_imports()
        self._check_linting()
        self._check_typing()
        self._check_security()
        self._check_tests()
        self._check_naming_conventions()
        self._check_file_lengths()
        self._check_function_lengths()
        self._check_docstrings()
        self._check_dependencies()

        self._print_summary()
        overall_status = all(
            result.status == CheckStatus.PASSED
            for result in self.results
            if result.status != CheckStatus.SKIPPED
        )
        logger.info(
            f"Overall quality check status: {'PASSED' if overall_status else 'FAILED'}"
        )
        return overall_status

    def _print_summary(self) -> None:
        """Print a summary of all check results."""
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == CheckStatus.SKIPPED)
        summary = (
            f"\n{Colors.HEADER}{Colors.BOLD}Pipeline Summary:{Colors.ENDC}\n"
            f"{Colors.GREEN}Passed: {passed}{Colors.ENDC}\n"
            f"{Colors.FAIL}Failed: {failed}{Colors.ENDC}\n"
            f"{Colors.BLUE}Skipped: {skipped}{Colors.ENDC}\n"
        )
        print(summary)
        logger.info(
            f"Pipeline Summary - Passed: {passed}, Failed: {failed}, Skipped: {skipped}"
        )
        if failed == 0:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✓ All quality checks passed!{Colors.ENDC}"
            )
            logger.info("All quality checks passed!")
        else:
            print(
                f"\n{Colors.FAIL}{Colors.BOLD}✗ Some quality checks failed. See details above.{Colors.ENDC}"
            )
            logger.warning("Some quality checks failed.")

    def _check_formatting(self) -> None:
        """Check code formatting with Black."""
        try:
            result = self._run_command(["black", "--check", "."])
            if result.returncode == 0:
                self.results.append(
                    CheckResult(
                        "Code Formatting (Black)",
                        CheckStatus.PASSED,
                        "All files are properly formatted.",
                    )
                )
                logger.info("Black formatting check passed.")
            else:
                self.results.append(
                    CheckResult(
                        "Code Formatting (Black)",
                        CheckStatus.FAILED,
                        f"Files need formatting:\n{result.stderr}",
                    )
                )
                logger.error("Black formatting check failed.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Code Formatting (Black)",
                    CheckStatus.FAILED,
                    f"Error running Black: {str(e)}",
                )
            )
            logger.exception("Error running Black.")

    def _check_imports(self) -> None:
        """Check import ordering with isort."""
        try:
            result = self._run_command(["isort", "--check", "."])
            if result.returncode == 0:
                self.results.append(
                    CheckResult(
                        "Import Ordering (isort)",
                        CheckStatus.PASSED,
                        "All imports are properly ordered.",
                    )
                )
                logger.info("isort check passed.")
            else:
                self.results.append(
                    CheckResult(
                        "Import Ordering (isort)",
                        CheckStatus.FAILED,
                        f"Improperly ordered imports:\n{result.stdout}",
                    )
                )
                logger.error("isort check failed.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Import Ordering (isort)",
                    CheckStatus.FAILED,
                    f"Error running isort: {str(e)}",
                )
            )
            logger.exception("Error running isort.")

    def _check_linting(self) -> None:
        """Check code linting with Flake8 and Ruff (if enabled)."""
        try:
            result = self._run_command(["flake8"])
            if result.returncode == 0:
                self.results.append(
                    CheckResult(
                        "Code Linting (Flake8)",
                        CheckStatus.PASSED,
                        "No linting issues found.",
                    )
                )
                logger.info("Flake8 linting passed.")
            else:
                self.results.append(
                    CheckResult(
                        "Code Linting (Flake8)",
                        CheckStatus.FAILED,
                        f"Linting issues found:\n{result.stdout}",
                    )
                )
                logger.error("Flake8 linting failed.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Code Linting (Flake8)",
                    CheckStatus.FAILED,
                    f"Error running Flake8: {str(e)}",
                )
            )
            logger.exception("Error running Flake8.")

        # Ruff check if enabled
        if self.config.getboolean("general", "check_ruff"):
            try:
                result = self._run_command(["ruff", "check", "."])
                if result.returncode == 0:
                    self.results.append(
                        CheckResult(
                            "Code Linting (Ruff)",
                            CheckStatus.PASSED,
                            "No linting issues found with Ruff.",
                        )
                    )
                    logger.info("Ruff linting passed.")
                else:
                    self.results.append(
                        CheckResult(
                            "Code Linting (Ruff)",
                            CheckStatus.FAILED,
                            f"Ruff found issues:\n{result.stdout}",
                        )
                    )
                    logger.error("Ruff linting failed.")
            except FileNotFoundError:
                self.results.append(
                    CheckResult(
                        "Code Linting (Ruff)",
                        CheckStatus.SKIPPED,
                        "Ruff not installed or not found.",
                    )
                )
                logger.warning("Ruff not installed; skipping Ruff linting.")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Code Linting (Ruff)",
                        CheckStatus.FAILED,
                        f"Error running Ruff: {str(e)}",
                    )
                )
                logger.exception("Error running Ruff.")

    def _check_typing(self) -> None:
        """Check static typing with mypy."""
        if not self.config.getboolean("general", "check_mypy"):
            self.results.append(
                CheckResult(
                    "Static Type Checking (mypy)",
                    CheckStatus.SKIPPED,
                    "Mypy check disabled in configuration.",
                )
            )
            logger.info("Mypy check disabled by configuration.")
            return

        src_dirs = [d.strip() for d in self.config["paths"]["src_dirs"].split(",")]
        for src_dir in src_dirs:
            full_path = os.path.join(self.project_path, src_dir)
            if not os.path.exists(full_path):
                logger.info(f"Source directory not found: {src_dir}")
                continue
            try:
                result = subprocess.run(
                    ["mypy", src_dir],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    self.results.append(
                        CheckResult(
                            f"Static Type Checking (mypy: {src_dir})",
                            CheckStatus.PASSED,
                            f"No type issues in {src_dir}.",
                        )
                    )
                    logger.info(f"Mypy check passed for {src_dir}.")
                else:
                    self.results.append(
                        CheckResult(
                            f"Static Type Checking (mypy: {src_dir})",
                            CheckStatus.FAILED,
                            f"Type issues in {src_dir}:\n{result.stdout}",
                        )
                    )
                    logger.error(f"Mypy check failed for {src_dir}.")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Static Type Checking (mypy)",
                        CheckStatus.FAILED,
                        f"Error running mypy: {str(e)}",
                    )
                )
                logger.exception("Error running mypy.")

    def _check_security(self) -> None:
        """Check security issues with Bandit."""
        if not self.config.getboolean("general", "check_bandit"):
            self.results.append(
                CheckResult(
                    "Security Scanning (Bandit)",
                    CheckStatus.SKIPPED,
                    "Bandit check disabled in configuration.",
                )
            )
            logger.info("Bandit check disabled by configuration.")
            return

        src_dirs = [d.strip() for d in self.config["paths"]["src_dirs"].split(",")]
        for src_dir in src_dirs:
            full_path = os.path.join(self.project_path, src_dir)
            if not os.path.exists(full_path):
                logger.info(f"Source directory not found for Bandit: {src_dir}")
                continue
            try:
                result = subprocess.run(
                    ["bandit", "-r", src_dir],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    self.results.append(
                        CheckResult(
                            f"Security Scanning (Bandit: {src_dir})",
                            CheckStatus.PASSED,
                            f"No security issues in {src_dir}.",
                        )
                    )
                    logger.info(f"Bandit check passed for {src_dir}.")
                else:
                    self.results.append(
                        CheckResult(
                            f"Security Scanning (Bandit: {src_dir})",
                            CheckStatus.FAILED,
                            f"Security issues in {src_dir}:\n{result.stdout}",
                        )
                    )
                    logger.error(f"Bandit check failed for {src_dir}.")
            except FileNotFoundError:
                self.results.append(
                    CheckResult(
                        "Security Scanning (Bandit)",
                        CheckStatus.SKIPPED,
                        "Bandit not installed or not found.",
                    )
                )
                logger.warning("Bandit not installed; skipping Bandit check.")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Security Scanning (Bandit)",
                        CheckStatus.FAILED,
                        f"Error running Bandit: {str(e)}",
                    )
                )
                logger.exception("Error running Bandit.")

    def _check_tests(self) -> None:
        """Run unit tests and check coverage."""
        test_dir = self.config["paths"]["test_dir"]
        if not os.path.exists(os.path.join(self.project_path, test_dir)):
            self.results.append(
                CheckResult(
                    "Unit Tests",
                    CheckStatus.FAILED,
                    f"Test directory '{test_dir}' not found.",
                )
            )
            logger.error(f"Test directory not found: {test_dir}")
            return

        try:
            result = self._run_command(["pytest", "-v"])
            if result.returncode == 0:
                self.results.append(
                    CheckResult("Unit Tests", CheckStatus.PASSED, "All tests passed.")
                )
                logger.info("Unit tests passed.")
            else:
                self.results.append(
                    CheckResult(
                        "Unit Tests",
                        CheckStatus.FAILED,
                        f"Some tests failed:\n{result.stdout}",
                    )
                )
                logger.error("Some unit tests failed.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Unit Tests", CheckStatus.FAILED, f"Error running pytest: {str(e)}"
                )
            )
            logger.exception("Error running pytest.")

        # Coverage check
        min_coverage = self.config.getint("general", "min_test_coverage")
        src_dirs = [d.strip() for d in self.config["paths"]["src_dirs"].split(",")]
        valid_src_dirs = [
            d for d in src_dirs if os.path.exists(os.path.join(self.project_path, d))
        ]
        if not valid_src_dirs:
            self.results.append(
                CheckResult(
                    "Test Coverage",
                    CheckStatus.SKIPPED,
                    f"No valid source directories found among: {', '.join(src_dirs)}",
                )
            )
            logger.warning("No valid source directories found for coverage check.")
            return

        src_dir = valid_src_dirs[0]
        try:
            self._run_command(["coverage", "run", "--source", src_dir, "-m", "pytest"])
            cov_result = self._run_command(["coverage", "report", "-m"])
            match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", cov_result.stdout)
            if match:
                coverage_pct = int(match.group(1))
                if coverage_pct >= min_coverage:
                    self.results.append(
                        CheckResult(
                            "Test Coverage",
                            CheckStatus.PASSED,
                            f"Coverage: {coverage_pct}% (min: {min_coverage}%)",
                        )
                    )
                    logger.info(f"Coverage check passed: {coverage_pct}%")
                else:
                    self.results.append(
                        CheckResult(
                            "Test Coverage",
                            CheckStatus.FAILED,
                            f"Coverage: {coverage_pct}% below minimum {min_coverage}%\n{cov_result.stdout}",
                        )
                    )
                    logger.error(
                        f"Coverage check failed: {coverage_pct}% < {min_coverage}%"
                    )
            else:
                self.results.append(
                    CheckResult(
                        "Test Coverage",
                        CheckStatus.FAILED,
                        f"Failed to parse coverage:\n{cov_result.stdout}",
                    )
                )
                logger.error("Failed to parse coverage percentage.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Test Coverage",
                    CheckStatus.FAILED,
                    f"Error checking coverage: {str(e)}",
                )
            )
            logger.exception("Error checking test coverage.")

    def _get_python_files(self) -> List[str]:
        """
        Helper to get all Python files from configured source directories.

        Returns:
            List of paths to Python files
        """
        python_files = []
        src_dirs = [d.strip() for d in self.config["paths"]["src_dirs"].split(",")]
        for src_dir in src_dirs:
            full_path = os.path.join(self.project_path, src_dir)
            if os.path.exists(full_path):
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))
        logger.info(f"Found {len(python_files)} Python files in source directories.")
        return python_files

    def _check_naming_conventions(self) -> None:
        """Check naming conventions for files, classes, and functions."""
        violations = []
        for file_path in self._get_python_files():
            file_name = os.path.basename(file_path)
            if not re.match(r"^[a-z][a-z0-9_]*\.py$", file_name):
                violations.append(f"File '{file_path}' should be in snake_case.")
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    for cls in re.findall(r"class\s+([A-Za-z0-9_]+)", content):
                        if not re.match(r"^[A-Z][A-Za-z0-9]*$", cls):
                            violations.append(
                                f"Class '{cls}' in '{file_path}' should be in PascalCase."
                            )
                    for func in re.findall(r"def\s+([A-Za-z0-9_]+)", content):
                        if not re.match(r"^[a-z][a-z0-9_]*$", func):
                            violations.append(
                                f"Function '{func}' in '{file_path}' should be in snake_case."
                            )
            except Exception as e:
                violations.append(f"Error checking naming in '{file_path}': {str(e)}")
                logger.exception(f"Error checking naming conventions in {file_path}")
        if violations:
            self.results.append(
                CheckResult(
                    "Naming Conventions", CheckStatus.FAILED, "\n".join(violations)
                )
            )
            logger.error("Naming convention violations found.")
        else:
            self.results.append(
                CheckResult(
                    "Naming Conventions",
                    CheckStatus.PASSED,
                    "All naming conventions are followed.",
                )
            )
            logger.info("Naming conventions check passed.")

    def _check_file_lengths(self) -> None:
        """Ensure no file exceeds the maximum allowed length."""
        max_length = self.config.getint("general", "max_file_length")
        violations = []
        for file_path in self._get_python_files():
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if len(lines) > max_length:
                        violations.append(
                            f"File '{file_path}' has {len(lines)} lines (max {max_length})."
                        )
            except Exception as e:
                violations.append(f"Error checking length of '{file_path}': {str(e)}")
                logger.exception(f"Error checking file length for {file_path}")
        if violations:
            self.results.append(
                CheckResult("File Lengths", CheckStatus.FAILED, "\n".join(violations))
            )
            logger.error("File length violations found.")
        else:
            self.results.append(
                CheckResult(
                    "File Lengths",
                    CheckStatus.PASSED,
                    f"All files within {max_length} lines.",
                )
            )
            logger.info("File length check passed.")

    def _check_function_lengths(self) -> None:
        """Ensure no function exceeds the maximum allowed length."""
        max_length = self.config.getint("general", "max_function_length")
        violations = []
        for file_path in self._get_python_files():
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                lines = content.split("\n")
                in_function = False
                current_function = ""
                current_indent = 0
                function_lines = 0
                for line in lines:
                    if not in_function:
                        if re.match(r"\s*def\s+([A-Za-z0-9_]+)\s*\(", line):
                            current_function = re.search(
                                r"def\s+([A-Za-z0-9_]+)", line
                            ).group(1)
                            in_function = True
                            current_indent = len(line) - len(line.lstrip())
                            function_lines = 1
                    else:
                        if (
                            line.strip() == ""
                            or (len(line) - len(line.lstrip())) > current_indent
                        ):
                            function_lines += 1
                        else:
                            if function_lines > max_length:
                                violations.append(
                                    f"Function '{current_function}' in '{file_path}' has {function_lines} lines (max {max_length})."
                                )
                            in_function = False
                if in_function and function_lines > max_length:
                    violations.append(
                        f"Function '{current_function}' in '{file_path}' has {function_lines} lines (max {max_length})."
                    )
            except Exception as e:
                violations.append(
                    f"Error checking function lengths in '{file_path}': {str(e)}"
                )
                logger.exception(f"Error checking function length for {file_path}")
        if violations:
            self.results.append(
                CheckResult(
                    "Function Lengths", CheckStatus.FAILED, "\n".join(violations)
                )
            )
            logger.error("Function length violations found.")
        else:
            self.results.append(
                CheckResult(
                    "Function Lengths",
                    CheckStatus.PASSED,
                    f"All functions within {max_length} lines.",
                )
            )
            logger.info("Function length check passed.")

    def _check_docstrings(self) -> None:
        """Check that classes and functions have docstrings."""
        violations = []
        for file_path in self._get_python_files():
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                for match in re.finditer(r"class\s+([A-Za-z0-9_]+)[^\n]*:", content):
                    pos = match.end()
                    snippet = content[pos : pos + 100].strip()
                    if not (snippet.startswith('"""') or snippet.startswith("'''")):
                        violations.append(
                            f"Class '{match.group(1)}' in '{file_path}' is missing a docstring."
                        )
                for match in re.finditer(r"def\s+([A-Za-z0-9_]+)[^\n]*:", content):
                    pos = match.end()
                    snippet = content[pos : pos + 100].strip()
                    func_name = match.group(1)
                    if not (snippet.startswith('"""') or snippet.startswith("'''")):
                        if not (
                            func_name.startswith("__") and func_name.endswith("__")
                        ):
                            violations.append(
                                f"Function '{func_name}' in '{file_path}' is missing a docstring."
                            )
            except Exception as e:
                violations.append(
                    f"Error checking docstrings in '{file_path}': {str(e)}"
                )
                logger.exception(f"Error checking docstrings in {file_path}")
        if violations:
            self.results.append(
                CheckResult("Docstrings", CheckStatus.FAILED, "\n".join(violations))
            )
            logger.error("Docstring violations found.")
        else:
            self.results.append(
                CheckResult(
                    "Docstrings",
                    CheckStatus.PASSED,
                    "All classes and functions have proper docstrings.",
                )
            )
            logger.info("Docstring check passed.")

    def _check_dependencies(self) -> None:
        """Check dependency management and security."""
        has_requirements = os.path.exists(
            os.path.join(self.project_path, "requirements.txt")
        )
        has_pipfile = os.path.exists(os.path.join(self.project_path, "Pipfile"))
        has_poetry = os.path.exists(os.path.join(self.project_path, "pyproject.toml"))

        dep_files = [
            fname
            for fname, exists in (
                ("requirements.txt", has_requirements),
                ("Pipfile", has_pipfile),
                ("pyproject.toml", has_poetry),
            )
            if exists
        ]
        if not dep_files:
            self.results.append(
                CheckResult(
                    "Dependency Management",
                    CheckStatus.FAILED,
                    "No dependency management files found.",
                )
            )
            logger.error("No dependency management files found.")
        else:
            self.results.append(
                CheckResult(
                    "Dependency Management",
                    CheckStatus.PASSED,
                    f"Found: {', '.join(dep_files)}",
                )
            )
            logger.info(f"Dependency management files found: {', '.join(dep_files)}")
            try:
                if has_requirements:
                    result = self._run_command(["pip-audit", "-r", "requirements.txt"])
                    if "No known vulnerabilities found" in result.stdout:
                        self.results.append(
                            CheckResult(
                                "Dependency Security",
                                CheckStatus.PASSED,
                                "No known vulnerabilities found.",
                            )
                        )
                        logger.info("Dependency security check passed.")
                    else:
                        self.results.append(
                            CheckResult(
                                "Dependency Security",
                                CheckStatus.FAILED,
                                f"Vulnerabilities found:\n{result.stdout}",
                            )
                        )
                        logger.error("Dependency security issues found.")
                else:
                    self.results.append(
                        CheckResult(
                            "Dependency Security",
                            CheckStatus.SKIPPED,
                            "Dependency security check only supports requirements.txt.",
                        )
                    )
                    logger.info(
                        "Skipping dependency security check (requirements.txt not found)."
                    )
            except FileNotFoundError:
                self.results.append(
                    CheckResult(
                        "Dependency Security",
                        CheckStatus.SKIPPED,
                        "pip-audit not installed or not found.",
                    )
                )
                logger.warning(
                    "pip-audit not installed; skipping dependency security check."
                )
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Dependency Security",
                        CheckStatus.FAILED,
                        f"Error checking dependency security: {str(e)}",
                    )
                )
                logger.exception("Error checking dependency security.")

    def process_branch_and_commit(self) -> bool:
        """
        If all quality checks passed and auto-commit is enabled, process branch merging and commit.

        Returns:
            True if processing was successful, False otherwise
        """
        if not all(
            r.status == CheckStatus.PASSED
            for r in self.results
            if r.status != CheckStatus.SKIPPED
        ):
            logger.error("Quality checks did not pass. Aborting branch processing.")
            print(
                f"\n{Colors.FAIL}Cannot process branch - some quality checks failed.{Colors.ENDC}"
            )
            return False

        if not self.config.getboolean("general", "enable_auto_commit"):
            logger.info("Auto-commit disabled in configuration.")
            print(
                f"\n{Colors.BLUE}Auto-commit is disabled in configuration.{Colors.ENDC}"
            )
            return True

        try:
            logger.info("Starting branch and commit processing.")
            print(
                f"\n{Colors.HEADER}Starting branch and commit processing...{Colors.ENDC}"
            )
            branch_result = self._run_command(["git", "branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            main_branch = self.config["general"]["main_branch"]
            logger.info(f"Current branch: {current_branch}")
            print(f"{Colors.BLUE}Current branch: {current_branch}{Colors.ENDC}")

            if current_branch == main_branch:
                logger.info(f"Already on {main_branch} branch; no processing needed.")
                print(
                    f"{Colors.WARNING}Already on {main_branch} branch. No branch processing needed.{Colors.ENDC}"
                )
                return True

            status_result = self._run_command(["git", "status", "--porcelain"])
            if status_result.stdout.strip():
                logger.info("Uncommitted changes detected; committing changes.")
                print(f"{Colors.BLUE}Committing changes...{Colors.ENDC}")
                commit_msg = f"Quality checks passed for branch {current_branch}"
                self._run_command(["git", "add", "."])
                commit_result = self._run_command(["git", "commit", "-m", commit_msg])
                if commit_result.returncode != 0:
                    logger.error("Failed to commit changes.")
                    print(
                        f"{Colors.FAIL}Failed to commit changes: {commit_result.stderr}{Colors.ENDC}"
                    )
                    return False
                logger.info("Changes committed successfully.")
                print(f"{Colors.GREEN}Changes committed successfully.{Colors.ENDC}")
            else:
                logger.info("No changes to commit.")
                print(f"{Colors.BLUE}No changes to commit.{Colors.ENDC}")

            logger.info(f"Checking out main branch: {main_branch}")
            print(f"{Colors.BLUE}Checking out {main_branch} branch...{Colors.ENDC}")
            checkout_result = self._run_command(["git", "checkout", main_branch])
            if checkout_result.returncode != 0:
                logger.error(f"Failed to checkout {main_branch}.")
                print(
                    f"{Colors.FAIL}Failed to checkout {main_branch}: {checkout_result.stderr}{Colors.ENDC}"
                )
                return False

            logger.info(f"Merging {current_branch} into {main_branch}.")
            print(
                f"{Colors.BLUE}Merging {current_branch} into {main_branch}...{Colors.ENDC}"
            )
            merge_result = self._run_command(["git", "merge", current_branch])
            if merge_result.returncode != 0:
                logger.error(f"Merge of {current_branch} failed.")
                print(
                    f"{Colors.FAIL}Failed to merge {current_branch}: {merge_result.stderr}{Colors.ENDC}"
                )
                print(
                    f"{Colors.BLUE}Aborting merge and returning to {current_branch}...{Colors.ENDC}"
                )
                self._run_command(["git", "merge", "--abort"])
                self._run_command(["git", "checkout", current_branch])
                return False

            logger.info(f"Merge successful: {current_branch} into {main_branch}.")
            print(
                f"{Colors.GREEN}Successfully merged {current_branch} into {main_branch}.{Colors.ENDC}"
            )
            logger.info(f"Deleting branch {current_branch}.")
            print(f"{Colors.BLUE}Deleting branch {current_branch}...{Colors.ENDC}")
            delete_result = self._run_command(["git", "branch", "-d", current_branch])
            if delete_result.returncode != 0:
                logger.warning(f"Could not delete branch {current_branch}.")
                print(
                    f"{Colors.WARNING}Could not delete branch {current_branch}: {delete_result.stderr}{Colors.ENDC}"
                )
            else:
                logger.info(f"Branch {current_branch} deleted.")
                print(f"{Colors.GREEN}Branch {current_branch} deleted.{Colors.ENDC}")
            return True
        except Exception as e:
            logger.exception("Error during branch processing.")
            print(f"{Colors.FAIL}Error during branch processing: {str(e)}{Colors.ENDC}")
            return False


def main():
    """Command-line entry point for the code quality pipeline."""
    parser = argparse.ArgumentParser(
        description="Python Code Quality Pipeline - Ensures code follows development guidelines"
    )
    parser.add_argument("project_path", help="Path to the Python project")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Enable automatic commit and branch processing",
    )
    args = parser.parse_args()

    logger.info(f"Starting pipeline for project: {args.project_path}")
    pipeline = CodeQualityPipeline(args.project_path, args.config)
    if args.auto_commit:
        pipeline.config.set("general", "enable_auto_commit", "true")
        logger.info("Auto-commit enabled via command line argument.")
    all_checks_passed = pipeline.run_all_checks()
    if all_checks_passed:
        pipeline.process_branch_and_commit()
    logger.info("Pipeline finished.")
    sys.exit(0 if all_checks_passed else 1)


if __name__ == "__main__":
    main()
