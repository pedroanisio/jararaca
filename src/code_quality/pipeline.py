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

from rich.panel import Panel

from .utils import Colors, console, create_summary_table, print_rich_result, run_command

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
        console.print(Panel("Running Python Code Quality Pipeline", style="header"))
        console.print(f"Project path: [info]{self.project_path}[/info]", style="info")

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

        # Print the summary table
        console.print(create_summary_table(passed, failed, skipped))

        logger.info(
            f"Pipeline Summary - Passed: {passed}, Failed: {failed}, Skipped: {skipped}"
        )

        # Print final result
        if failed == 0:
            console.print("✓ All quality checks passed!", style="success")
            logger.info("All quality checks passed!")
        else:
            console.print(
                "✗ Some quality checks failed. See details above.", style="error"
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
                print_rich_result(
                    "Code Formatting (Black)",
                    CheckStatus.PASSED.value,
                    "All files are properly formatted.",
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
                print_rich_result(
                    "Code Formatting (Black)",
                    CheckStatus.FAILED.value,
                    f"Files need formatting:\n{result.stderr}",
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
            print_rich_result(
                "Code Formatting (Black)",
                CheckStatus.FAILED.value,
                f"Error running Black: {str(e)}",
            )
            logger.exception("Error running Black.")

    def _check_imports(self) -> None:
        """Check import sorting with isort."""
        try:
            result = self._run_command(["isort", "--check", "--profile", "black", "."])
            if result.returncode == 0:
                self.results.append(
                    CheckResult(
                        "Import Sorting (isort)",
                        CheckStatus.PASSED,
                        "All imports are properly sorted.",
                    )
                )
                print_rich_result(
                    "Import Sorting (isort)",
                    CheckStatus.PASSED.value,
                    "All imports are properly sorted.",
                )
                logger.info("isort check passed.")
            else:
                self.results.append(
                    CheckResult(
                        "Import Sorting (isort)",
                        CheckStatus.FAILED,
                        f"Files need import sorting:\n{result.stdout}",
                    )
                )
                print_rich_result(
                    "Import Sorting (isort)",
                    CheckStatus.FAILED.value,
                    f"Files need import sorting:\n{result.stdout}",
                )
                logger.error("isort check failed.")
        except Exception as e:
            self.results.append(
                CheckResult(
                    "Import Sorting (isort)",
                    CheckStatus.FAILED,
                    f"Error running isort: {str(e)}",
                )
            )
            print_rich_result(
                "Import Sorting (isort)",
                CheckStatus.FAILED.value,
                f"Error running isort: {str(e)}",
            )
            logger.exception("Error running isort.")

    def _check_linting(self) -> None:
        """Check code linting with Flake8 and Ruff (if enabled)."""
        try:
            # Add exclusions for common directories and files that should be ignored
            result = self._run_command(
                [
                    "flake8",
                    "--exclude=venv,env,.venv,.env,.git,__pycache__,build,dist,*.egg-info",
                ]
            )
            if result.returncode == 0:
                self.results.append(
                    CheckResult(
                        "Code Linting (Flake8)",
                        CheckStatus.PASSED,
                        "No linting issues found.",
                    )
                )
                print_rich_result(
                    "Code Linting (Flake8)",
                    CheckStatus.PASSED.value,
                    "No linting issues found.",
                )
                logger.info("Flake8 linting passed.")
            else:
                # Parse flake8 output and format it better
                flake8_issues = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            parts = line.split(":", 3)
                            if len(parts) >= 4:
                                file_path, line_num, col, error = parts
                                flake8_issues.append(
                                    f"[yellow]{file_path}[/yellow]:[bold]{line_num}:{col}[/bold] - {error.strip()}"
                                )
                        except Exception:
                            flake8_issues.append(line)

                detailed_msg = "[bold red]Flake8 linting issues found[/bold red]\n\n"
                if flake8_issues:
                    detailed_msg += "\n".join(flake8_issues) + "\n\n"
                else:
                    detailed_msg += result.stdout + "\n\n"

                detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
                detailed_msg += (
                    "- Run 'flake8 --fix' to automatically fix some issues\n"
                )
                detailed_msg += (
                    "- E*** errors are style issues (indentation, whitespace)\n"
                )
                detailed_msg += (
                    "- F*** errors are logical issues (unused imports, variables)\n"
                )
                detailed_msg += "- W*** errors are warnings (deprecated features, etc.)"

                self.results.append(
                    CheckResult(
                        "Code Linting (Flake8)",
                        CheckStatus.FAILED,
                        f"Linting issues found:\n{result.stdout}",
                    )
                )
                print_rich_result(
                    "Code Linting (Flake8)", CheckStatus.FAILED.value, detailed_msg
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
            print_rich_result(
                "Code Linting (Flake8)",
                CheckStatus.FAILED.value,
                f"[bold red]Error running Flake8:[/bold red] {str(e)}\n\n"
                f"[bold cyan]How to fix:[/bold cyan] Make sure Flake8 is installed correctly.",
            )
            logger.exception("Error running Flake8.")

        # Ruff check if enabled
        if self.config.getboolean("general", "check_ruff", fallback=True):
            try:
                # Add exclusions for common directories and files that should be ignored
                result = self._run_command(
                    [
                        "ruff",
                        "check",
                        ".",
                        "--exclude=venv,env,.venv,.env,.git,__pycache__,build,dist,*.egg-info",
                    ]
                )
                if result.returncode == 0:
                    self.results.append(
                        CheckResult(
                            "Code Linting (Ruff)",
                            CheckStatus.PASSED,
                            "No linting issues found with Ruff.",
                        )
                    )
                    print_rich_result(
                        "Code Linting (Ruff)",
                        CheckStatus.PASSED.value,
                        "No linting issues found with Ruff.",
                    )
                    logger.info("Ruff linting passed.")
                else:
                    # Parse and format Ruff output
                    ruff_issues = []
                    for line in result.stdout.strip().split("\n"):
                        if line and not line.startswith("Found") and ":" in line:
                            try:
                                file_info, error_msg = line.split("  ", 1)
                                ruff_issues.append(
                                    f"[yellow]{file_info.strip()}[/yellow] - {error_msg.strip()}"
                                )
                            except Exception:
                                ruff_issues.append(line)

                    detailed_msg = "[bold red]Ruff linting issues found[/bold red]\n\n"
                    if ruff_issues:
                        detailed_msg += "\n".join(ruff_issues) + "\n\n"
                    else:
                        detailed_msg += result.stdout + "\n\n"

                    detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
                    detailed_msg += (
                        "- Run 'ruff check --fix .' to automatically fix many issues\n"
                    )
                    detailed_msg += (
                        "- Ruff is a fast linter that can replace Flake8 and others\n"
                    )
                    detailed_msg += (
                        "- See https://docs.astral.sh/ruff/ for more details"
                    )

                    self.results.append(
                        CheckResult(
                            "Code Linting (Ruff)",
                            CheckStatus.FAILED,
                            f"Ruff found issues:\n{result.stdout}",
                        )
                    )
                    print_rich_result(
                        "Code Linting (Ruff)", CheckStatus.FAILED.value, detailed_msg
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
                print_rich_result(
                    "Code Linting (Ruff)",
                    CheckStatus.SKIPPED.value,
                    "Ruff not installed or not found.",
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
                print_rich_result(
                    "Code Linting (Ruff)",
                    CheckStatus.FAILED.value,
                    f"[bold red]Error running Ruff:[/bold red] {str(e)}\n\n"
                    f"[bold cyan]How to fix:[/bold cyan] Make sure Ruff is installed correctly.",
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
            print_rich_result(
                "Static Type Checking (mypy)",
                CheckStatus.SKIPPED.value,
                "Mypy check disabled in configuration.",
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
                            "Static Type Checking (mypy)",
                            CheckStatus.PASSED,
                            f"No type errors found in {src_dir}.",
                        )
                    )
                    print_rich_result(
                        "Static Type Checking (mypy)",
                        CheckStatus.PASSED.value,
                        f"No type errors found in {src_dir}.",
                    )
                    logger.info(f"Mypy check passed for {src_dir}.")
                else:
                    # Parse mypy output and format it better
                    mypy_issues = []
                    for line in result.stdout.strip().split("\n"):
                        if ":" in line:
                            try:
                                file_info, error_msg = (
                                    line.split(":", 3)[0:2],
                                    line.split(":", 3)[2:],
                                )
                                file_path, line_num = file_info
                                mypy_issues.append(
                                    f"[yellow]{file_path}[/yellow]:[bold]{line_num}[/bold] - {':'.join(error_msg).strip()}"
                                )
                            except Exception:
                                mypy_issues.append(line)

                    detailed_msg = (
                        f"[bold red]Type errors found in {src_dir}[/bold red]\n\n"
                    )
                    if mypy_issues:
                        detailed_msg += "\n".join(mypy_issues) + "\n\n"
                    else:
                        detailed_msg += result.stdout + "\n\n"

                    detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
                    detailed_msg += "- Add proper type annotations to your functions and variables\n"
                    detailed_msg += "- Use Optional[] for variables that can be None\n"
                    detailed_msg += (
                        "- Add # type: ignore comments for legitimate exceptions\n"
                    )
                    detailed_msg += (
                        "- See https://mypy.readthedocs.io/ for more information"
                    )

                    self.results.append(
                        CheckResult(
                            "Static Type Checking (mypy)",
                            CheckStatus.FAILED,
                            f"Type errors found in {src_dir}:\n{result.stdout}",
                        )
                    )
                    print_rich_result(
                        "Static Type Checking (mypy)",
                        CheckStatus.FAILED.value,
                        detailed_msg,
                    )
                    logger.error(f"Mypy check failed for {src_dir}.")
            except FileNotFoundError:
                self.results.append(
                    CheckResult(
                        "Static Type Checking (mypy)",
                        CheckStatus.SKIPPED,
                        "Mypy not installed or not found.",
                    )
                )
                print_rich_result(
                    "Static Type Checking (mypy)",
                    CheckStatus.SKIPPED.value,
                    "Mypy not installed or not found.",
                )
                logger.warning("Mypy not installed; skipping type checking.")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Static Type Checking (mypy)",
                        CheckStatus.FAILED,
                        f"Error running mypy: {str(e)}",
                    )
                )
                print_rich_result(
                    "Static Type Checking (mypy)",
                    CheckStatus.FAILED.value,
                    f"[bold red]Error running mypy:[/bold red] {str(e)}\n\n"
                    f"[bold cyan]How to fix:[/bold cyan] Make sure mypy is installed correctly.",
                )
                logger.exception(f"Error running mypy on {src_dir}.")

    def _check_security(self) -> None:
        """Check code security with Bandit."""
        if not self.config.getboolean("general", "check_bandit"):
            self.results.append(
                CheckResult(
                    "Security Check (Bandit)",
                    CheckStatus.SKIPPED,
                    "Security check disabled in configuration.",
                )
            )
            print_rich_result(
                "Security Check (Bandit)",
                CheckStatus.SKIPPED.value,
                "Security check disabled in configuration.",
            )
            logger.info("Security check disabled by configuration.")
            return

        src_dirs = [d.strip() for d in self.config["paths"]["src_dirs"].split(",")]
        for src_dir in src_dirs:
            full_path = os.path.join(self.project_path, src_dir)
            if not os.path.exists(full_path):
                logger.info(f"Source directory not found for Bandit: {src_dir}")
                continue
            try:
                result = self._run_command(["bandit", "-r", src_dir])
                if result.returncode == 0:
                    self.results.append(
                        CheckResult(
                            "Security Check (Bandit)",
                            CheckStatus.PASSED,
                            f"No security issues found in {src_dir}.",
                        )
                    )
                    print_rich_result(
                        "Security Check (Bandit)",
                        CheckStatus.PASSED.value,
                        f"No security issues found in {src_dir}.",
                    )
                    logger.info(f"Bandit security check passed for {src_dir}.")
                else:
                    # Parse bandit output and format it better
                    bandit_issues = []
                    for line in result.stdout.strip().split("\n"):
                        if line.startswith(">>") and ":" in line:
                            try:
                                bandit_issues.append(f"[yellow]{line.strip()}[/yellow]")
                            except Exception:
                                bandit_issues.append(line)

                    detailed_msg = (
                        f"[bold red]Security issues found in {src_dir}[/bold red]\n\n"
                    )
                    if bandit_issues:
                        detailed_msg += "\n".join(bandit_issues) + "\n\n"
                    else:
                        detailed_msg += result.stdout + "\n\n"

                    detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
                    detailed_msg += (
                        "- Review the security issues identified and fix them\n"
                    )
                    detailed_msg += (
                        "- Issues are categorized by severity (Low/Medium/High)\n"
                    )
                    detailed_msg += (
                        "- See https://bandit.readthedocs.io/ for more details"
                    )

                    self.results.append(
                        CheckResult(
                            "Security Check (Bandit)",
                            CheckStatus.FAILED,
                            f"Security issues found in {src_dir}:\n{result.stdout}",
                        )
                    )
                    print_rich_result(
                        "Security Check (Bandit)",
                        CheckStatus.FAILED.value,
                        detailed_msg,
                    )
                    logger.error(f"Bandit security check failed for {src_dir}.")
            except FileNotFoundError:
                self.results.append(
                    CheckResult(
                        "Security Check (Bandit)",
                        CheckStatus.SKIPPED,
                        "Bandit not installed or not found.",
                    )
                )
                print_rich_result(
                    "Security Check (Bandit)",
                    CheckStatus.SKIPPED.value,
                    "Bandit not installed or not found.",
                )
                logger.warning("Bandit not installed; skipping security check.")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Security Check (Bandit)",
                        CheckStatus.FAILED,
                        f"Error running Bandit: {str(e)}",
                    )
                )
                print_rich_result(
                    "Security Check (Bandit)",
                    CheckStatus.FAILED.value,
                    f"[bold red]Error running Bandit:[/bold red] {str(e)}\n\n"
                    f"[bold cyan]How to fix:[/bold cyan] Make sure Bandit is installed correctly.",
                )
                logger.exception(f"Error running Bandit on {src_dir}.")

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
                    print_rich_result(
                        "Test Coverage",
                        CheckStatus.PASSED.value,
                        f"Coverage: {coverage_pct}% (min: {min_coverage}%)",
                    )
                    logger.info(f"Coverage check passed: {coverage_pct}%")
                else:
                    # Parse the coverage report to extract file-specific information
                    coverage_lines = cov_result.stdout.strip().split("\n")

                    # Create a more detailed message
                    missing_coverage = []
                    for line in coverage_lines:
                        if line.startswith("src/") and not line.startswith("TOTAL"):
                            parts = re.split(r"\s+", line.strip())
                            if len(parts) >= 4:
                                file_path, stmts, miss, cover = parts[:4]
                                if int(miss) > 0:  # If there are missing statements
                                    missing_lines = ""
                                    if len(parts) > 4 and parts[-1].startswith(
                                        "Missing"
                                    ):
                                        missing_lines = f" - Missing lines: {parts[-1].replace('Missing', '').strip()}"
                                    missing_coverage.append(
                                        f"[yellow]{file_path}[/yellow]: {cover} coverage ({miss} statements not covered){missing_lines}"
                                    )

                    detailed_msg = (
                        "[bold red]Coverage: "
                        + str(coverage_pct)
                        + "% below minimum "
                        + str(min_coverage)
                        + "%[/bold red]\n\n"
                        "[bold]Files needing more test coverage:[/bold]\n"
                        + "\n".join(missing_coverage)
                        + "\n\n"
                        "[bold cyan]How to fix:[/bold cyan] Add more unit tests for the files listed above, focusing on the missing lines."
                    )

                    self.results.append(
                        CheckResult(
                            "Test Coverage",
                            CheckStatus.FAILED,
                            f"Coverage: {coverage_pct}% below minimum {min_coverage}%\n{cov_result.stdout}",
                        )
                    )
                    print_rich_result(
                        "Test Coverage", CheckStatus.FAILED.value, detailed_msg
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
                print_rich_result(
                    "Test Coverage",
                    CheckStatus.FAILED.value,
                    f"[bold red]Failed to parse coverage report[/bold red]\n\n{cov_result.stdout}\n\n[bold cyan]How to fix:[/bold cyan] Ensure your tests are running correctly and coverage is being generated.",
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
            print_rich_result(
                "Test Coverage",
                CheckStatus.FAILED.value,
                f"[bold red]Error checking coverage:[/bold red] {str(e)}\n\n[bold cyan]How to fix:[/bold cyan] Ensure coverage and pytest are installed correctly.",
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
        file_violations = []
        class_violations = []
        func_violations = []

        # Python keywords that shouldn't be considered violations
        python_keywords = [
            "as",
            "assert",
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
            "methods",
        ]

        for file_path in self._get_python_files():
            file_name = os.path.basename(file_path)
            # Skip checking special files like __init__.py and __main__.py
            if not file_name.startswith("__") and not re.match(
                r"^[a-z][a-z0-9_]*\.py$", file_name
            ):
                file_violations.append(
                    "[yellow]" + file_path + "[/yellow]: File should be in snake_case"
                )
                violations.append(f"File '{file_path}' should be in snake_case.")
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                    # Find class definitions using more precise regex
                    for match in re.finditer(
                        r"class\s+([A-Za-z0-9_]+)(?:\s*\(|\s*:)", content
                    ):
                        cls = match.group(1)
                        # Skip Python keywords and check if class follows PascalCase
                        if cls not in python_keywords and not re.match(
                            r"^[A-Z][A-Za-z0-9]*$", cls
                        ):
                            class_violations.append(
                                "[yellow]"
                                + file_path
                                + "[/yellow]: Class [red]"
                                + cls
                                + "[/red] should be in PascalCase"
                            )
                            violations.append(
                                f"Class '{cls}' in '{file_path}' should be in PascalCase."
                            )

                    # Find function definitions using more precise regex
                    for match in re.finditer(r"def\s+([A-Za-z0-9_]+)\s*\(", content):
                        func = match.group(1)
                        # Skip Python keywords, special methods (__xxx__), and private methods (_xxx)
                        if (
                            func not in python_keywords
                            and not (func.startswith("__") and func.endswith("__"))
                            and not func.startswith("_")
                            and not re.match(r"^[a-z][a-z0-9_]*$", func)
                        ):
                            func_violations.append(
                                "[yellow]"
                                + file_path
                                + "[/yellow]: Function [red]"
                                + func
                                + "[/red] should be in snake_case"
                            )
                            violations.append(
                                f"Function '{func}' in '{file_path}' should be in snake_case."
                            )
            except Exception as e:
                violations.append(f"Error checking naming in '{file_path}': {str(e)}")
                logger.exception(f"Error checking naming conventions in {file_path}")

        if violations:
            # Build detailed message with sections - Avoiding f-strings with markup
            detailed_msg = "[bold red]Naming convention violations found[/bold red]\n\n"

            if file_violations:
                detailed_msg += "[bold]File naming violations:[/bold]\n"
                detailed_msg += "\n".join(file_violations) + "\n\n"

            if class_violations:
                detailed_msg += "[bold]Class naming violations:[/bold]\n"
                detailed_msg += "\n".join(class_violations) + "\n\n"

            if func_violations:
                detailed_msg += "[bold]Function naming violations:[/bold]\n"
                detailed_msg += "\n".join(func_violations) + "\n\n"

            detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
            detailed_msg += (
                "- Files should be in snake_case (lowercase with underscores)\n"
            )
            detailed_msg += "- Classes should be in PascalCase (capitalized words without underscores)\n"
            detailed_msg += (
                "- Functions should be in snake_case (lowercase with underscores)\n"
            )
            detailed_msg += "[italic]Note: Special method names (__init__), private methods (_method), "
            detailed_msg += "and special files (__init__.py) follow Python conventions and are exempted.[/italic]"

            self.results.append(
                CheckResult(
                    "Naming Conventions", CheckStatus.FAILED, "\n".join(violations)
                )
            )
            print_rich_result(
                "Naming Conventions", CheckStatus.FAILED.value, detailed_msg
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
            print_rich_result(
                "Naming Conventions",
                CheckStatus.PASSED.value,
                "All naming conventions are followed.",
            )
            logger.info("Naming conventions check passed.")

    def _check_file_lengths(self) -> None:
        """Ensure no file exceeds the maximum allowed length."""
        max_length = self.config.getint("general", "max_file_length")
        violations = []
        detailed_violations = []

        for file_path in self._get_python_files():
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    num_lines = len(lines)
                    if num_lines > max_length:
                        percent_over = ((num_lines - max_length) / max_length) * 100
                        violations.append(
                            f"File '{file_path}' has {num_lines} lines (max {max_length})."
                        )
                        detailed_violations.append(
                            "[yellow]"
                            + file_path
                            + "[/yellow]: [red]"
                            + str(num_lines)
                            + "[/red] lines (exceeds max of "
                            + str(max_length)
                            + " by "
                            + f"{percent_over:.1f}%)"
                        )
            except Exception as e:
                violations.append(f"Error checking length of '{file_path}': {str(e)}")
                logger.exception(f"Error checking file length for {file_path}")

        if violations:
            detailed_msg = (
                "[bold red]File length violations found[/bold red]\n\n"
                + "[bold]Files exceeding maximum length ("
                + str(max_length)
                + " lines):[/bold]\n"
                + "\n".join(detailed_violations)
                + "\n\n"
                + "[bold cyan]How to fix:[/bold cyan]\n"
                + "- Consider breaking large files into smaller, focused modules\n"
                + "- Move related helper functions to a separate utility file\n"
                + "- Review and refactor long files to improve code organization"
            )

            self.results.append(
                CheckResult("File Lengths", CheckStatus.FAILED, "\n".join(violations))
            )
            print_rich_result("File Lengths", CheckStatus.FAILED.value, detailed_msg)
            logger.error("File length violations found.")
        else:
            self.results.append(
                CheckResult(
                    "File Lengths",
                    CheckStatus.PASSED,
                    f"All files within {max_length} lines.",
                )
            )
            print_rich_result(
                "File Lengths",
                CheckStatus.PASSED.value,
                f"All files within {max_length} lines.",
            )
            logger.info("File length check passed.")

    def _check_function_lengths(self) -> None:
        """Ensure no function exceeds the maximum allowed length."""
        max_length = self.config.getint("general", "max_function_length")
        violations = []
        functions_by_file = {}

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

                                percent_over = (
                                    (function_lines - max_length) / max_length
                                ) * 100
                                detailed_violation = (
                                    "[red]"
                                    + current_function
                                    + "[/red]: "
                                    + str(function_lines)
                                    + " lines (exceeds max by "
                                    + f"{percent_over:.1f}%)"
                                )

                                if file_path not in functions_by_file:
                                    functions_by_file[file_path] = []
                                functions_by_file[file_path].append(detailed_violation)

                            in_function = False
                if in_function and function_lines > max_length:
                    violations.append(
                        f"Function '{current_function}' in '{file_path}' has {function_lines} lines (max {max_length})."
                    )

                    percent_over = ((function_lines - max_length) / max_length) * 100
                    detailed_violation = (
                        "[red]"
                        + current_function
                        + "[/red]: "
                        + str(function_lines)
                        + " lines (exceeds max by "
                        + f"{percent_over:.1f}%)"
                    )

                    if file_path not in functions_by_file:
                        functions_by_file[file_path] = []
                    functions_by_file[file_path].append(detailed_violation)

            except Exception as e:
                violations.append(
                    f"Error checking function lengths in '{file_path}': {str(e)}"
                )
                logger.exception(f"Error checking function length for {file_path}")

        if violations:
            # Organize detailed message by file - avoiding f-strings with markup
            detailed_msg = "[bold red]Function length violations found[/bold red]\n\n"

            for file_path, funcs in functions_by_file.items():
                file_name = os.path.basename(file_path)
                detailed_msg += (
                    "[bold yellow]"
                    + file_name
                    + "[/bold yellow] ("
                    + file_path
                    + "):\n"
                )
                for func in funcs:
                    detailed_msg += "  • " + func + "\n"
                detailed_msg += "\n"

            detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
            detailed_msg += (
                "- Break large functions into smaller, focused helper functions\n"
            )
            detailed_msg += "- Extract repeated code patterns into reusable functions\n"
            detailed_msg += (
                "- Consider using class methods to organize related functionality\n"
            )
            detailed_msg += (
                "- Functions should ideally be less than "
                + str(max_length)
                + " lines for better readability"
            )

            self.results.append(
                CheckResult(
                    "Function Lengths", CheckStatus.FAILED, "\n".join(violations)
                )
            )
            print_rich_result(
                "Function Lengths", CheckStatus.FAILED.value, detailed_msg
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
            print_rich_result(
                "Function Lengths",
                CheckStatus.PASSED.value,
                f"All functions within {max_length} lines.",
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

            # Add rich output for failed docstring check
            detailed_msg = (
                "[bold red]Docstring violations found[/bold red]\n\n"
                "[bold]Missing docstrings:[/bold]\n"
                + "\n".join([f"[yellow]{v}[/yellow]" for v in violations])
                + "\n\n"
                "[bold cyan]How to fix:[/bold cyan] Add descriptive docstrings to all classes and functions."
            )
            print_rich_result("Docstrings", CheckStatus.FAILED.value, detailed_msg)
        else:
            self.results.append(
                CheckResult(
                    "Docstrings",
                    CheckStatus.PASSED,
                    "All classes and functions have proper docstrings.",
                )
            )
            print_rich_result(
                "Docstrings",
                CheckStatus.PASSED.value,
                "All classes and functions have proper docstrings.",
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
            print_rich_result(
                "Dependency Management",
                CheckStatus.FAILED.value,
                "[bold red]No dependency management files found[/bold red]\n\n"
                "[bold cyan]How to fix:[/bold cyan]\n"
                "- Create a requirements.txt file listing your dependencies\n"
                "- Or use modern tools like Pipenv (Pipfile) or Poetry (pyproject.toml)",
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
            print_rich_result(
                "Dependency Management",
                CheckStatus.PASSED.value,
                f"Found dependency files: {', '.join(dep_files)}",
            )
            logger.info(f"Dependency management files found: {', '.join(dep_files)}")
            try:
                if has_requirements:
                    # Only scan the requirements.txt file, not the installed packages
                    result = self._run_command(["pip-audit", "-r", "requirements.txt"])
                    if "No known vulnerabilities found" in result.stdout:
                        self.results.append(
                            CheckResult(
                                "Dependency Security",
                                CheckStatus.PASSED,
                                "No known vulnerabilities found.",
                            )
                        )
                        print_rich_result(
                            "Dependency Security",
                            CheckStatus.PASSED.value,
                            "No known vulnerabilities found in dependencies.",
                        )
                        logger.info("Dependency security check passed.")
                    else:
                        # Parse vulnerabilities from the output for better formatting
                        detailed_msg = "[bold red]Security vulnerabilities found in dependencies[/bold red]\n\n"

                        # Extract vulnerabilities from output
                        vulns = []
                        current_pkg = None
                        current_vuln = []

                        for line in result.stdout.strip().split("\n"):
                            if "Found" in line and "vulnerability" in line:
                                detailed_msg += f"[red]{line.strip()}[/red]\n\n"
                            elif line.strip().startswith("→"):
                                if current_pkg:
                                    vulns.append(
                                        f"[yellow]{current_pkg}[/yellow]:\n  "
                                        + "\n  ".join(current_vuln)
                                    )
                                current_pkg = line.replace("→", "").strip()
                                current_vuln = []
                            elif line.strip() and current_pkg is not None:
                                current_vuln.append(line.strip())

                        # Add the last package if there is one
                        if current_pkg and current_vuln:
                            vulns.append(
                                f"[yellow]{current_pkg}[/yellow]:\n  "
                                + "\n  ".join(current_vuln)
                            )

                        if vulns:
                            detailed_msg += "\n".join(vulns) + "\n\n"
                        else:
                            detailed_msg += result.stdout + "\n\n"

                        detailed_msg += "[bold cyan]How to fix:[/bold cyan]\n"
                        detailed_msg += (
                            "- Update vulnerable dependencies to newer versions\n"
                        )
                        detailed_msg += "- Run 'pip-audit -r requirements.txt --fix' to automatically fix issues\n"
                        detailed_msg += "- Check for security advisories at https://pypi.org/security-advisories/"

                        self.results.append(
                            CheckResult(
                                "Dependency Security",
                                CheckStatus.FAILED,
                                f"Found security vulnerabilities in dependencies:\n{result.stdout}",
                            )
                        )
                        print_rich_result(
                            "Dependency Security",
                            CheckStatus.FAILED.value,
                            detailed_msg,
                        )
                        logger.error("Dependency security issues found.")
                elif has_pipfile:
                    # Handle Pipenv (Pipfile) if needed
                    self.results.append(
                        CheckResult(
                            "Dependency Security",
                            CheckStatus.SKIPPED,
                            "Security scan for Pipfile not implemented.",
                        )
                    )
                    print_rich_result(
                        "Dependency Security",
                        CheckStatus.SKIPPED.value,
                        "Security scan for Pipfile not implemented yet.\n"
                        "[bold cyan]Tip:[/bold cyan] Run 'pipenv check' manually to check for vulnerabilities.",
                    )
                    logger.info("Pipfile security check skipped (not implemented).")
                elif has_poetry:
                    # Handle Poetry (pyproject.toml) if needed
                    self.results.append(
                        CheckResult(
                            "Dependency Security",
                            CheckStatus.SKIPPED,
                            "Security scan for Poetry not implemented.",
                        )
                    )
                    print_rich_result(
                        "Dependency Security",
                        CheckStatus.SKIPPED.value,
                        "Security scan for Poetry (pyproject.toml) not implemented yet.\n"
                        "[bold cyan]Tip:[/bold cyan] Run 'poetry check' manually to check for issues.",
                    )
                    logger.info("Poetry security check skipped (not implemented).")
            except Exception as e:
                self.results.append(
                    CheckResult(
                        "Dependency Security",
                        CheckStatus.FAILED,
                        f"Error checking dependency security: {str(e)}",
                    )
                )
                print_rich_result(
                    "Dependency Security",
                    CheckStatus.FAILED.value,
                    f"[bold red]Error checking dependency security:[/bold red] {str(e)}\n\n"
                    f"[bold cyan]How to fix:[/bold cyan] Make sure pip-audit is installed correctly.",
                )
                logger.exception("Error checking dependency security.")

    def process_branch_and_commit(self) -> bool:
        """
        Process the branch and commit changes if auto_commit is enabled.

        This method will:
        1. Check if we're on a feature branch
        2. Commit any changes if there are uncommitted changes
        3. Checkout main branch
        4. Pull latest changes
        5. Merge the feature branch
        6. Push the changes to remote
        7. Delete the feature branch

        Returns:
            True if all steps completed successfully, False otherwise
        """
        if not self.config.getboolean("general", "enable_auto_commit", fallback=False):
            logger.info("Auto-commit is disabled. Skipping branch processing.")
            console.print(
                "Auto-commit is disabled. Skipping branch processing.", style="info"
            )
            return True

        try:
            logger.info("Starting branch and commit processing.")
            console.print(
                Panel("Starting branch and commit processing...", style="header")
            )

            branch_result = self._run_command(["git", "branch", "--show-current"])
            current_branch = branch_result.stdout.strip()
            main_branch = self.config["general"]["main_branch"]
            logger.info(f"Current branch: {current_branch}")
            console.print(f"Current branch: [info]{current_branch}[/info]")

            if current_branch == main_branch:
                logger.info(f"Already on {main_branch} branch; no processing needed.")
                console.print(
                    f"Already on {main_branch} branch. No branch processing needed.",
                    style="warning",
                )
                return True

            status_result = self._run_command(["git", "status", "--porcelain"])
            if status_result.stdout.strip():
                logger.info("Uncommitted changes detected; committing changes.")
                console.print("Committing changes...", style="info")
                commit_msg = f"Quality checks passed for branch {current_branch}"
                self._run_command(["git", "add", "."])
                commit_result = self._run_command(["git", "commit", "-m", commit_msg])
                if commit_result.returncode != 0:
                    logger.error("Failed to commit changes.")
                    console.print(
                        f"Failed to commit changes: {commit_result.stderr}",
                        style="error",
                    )
                    return False
                logger.info("Changes committed successfully.")
                console.print("Changes committed successfully.", style="success")
            else:
                logger.info("No changes to commit.")
                console.print("No changes to commit.", style="info")

            logger.info(f"Checking out main branch: {main_branch}")
            console.print(f"Checking out {main_branch} branch...", style="info")
            checkout_result = self._run_command(["git", "checkout", main_branch])
            if checkout_result.returncode != 0:
                logger.error(f"Failed to checkout {main_branch}.")
                console.print(
                    f"Failed to checkout {main_branch}: {checkout_result.stderr}",
                    style="error",
                )
                return False

            logger.info(f"Merging {current_branch} into {main_branch}.")
            console.print(
                f"Merging {current_branch} into {main_branch}...", style="info"
            )
            merge_result = self._run_command(["git", "merge", current_branch])
            if merge_result.returncode != 0:
                logger.error(f"Merge of {current_branch} failed.")
                console.print(
                    f"Failed to merge {current_branch}: {merge_result.stderr}",
                    style="error",
                )
                console.print(
                    f"Aborting merge and returning to {current_branch}...", style="info"
                )
                self._run_command(["git", "merge", "--abort"])
                self._run_command(["git", "checkout", current_branch])
                return False

            logger.info(f"Merge successful: {current_branch} into {main_branch}.")
            console.print(
                f"Successfully merged {current_branch} into {main_branch}.",
                style="success",
            )
            logger.info(f"Deleting branch {current_branch}.")
            console.print(f"Deleting branch {current_branch}...", style="info")
            delete_result = self._run_command(["git", "branch", "-d", current_branch])
            if delete_result.returncode != 0:
                logger.warning(f"Could not delete branch {current_branch}.")
                console.print(
                    f"Could not delete branch {current_branch}: {delete_result.stderr}",
                    style="warning",
                )
            else:
                logger.info(f"Branch {current_branch} deleted.")
                console.print(f"Branch {current_branch} deleted.", style="success")
            return True
        except Exception as e:
            logger.exception("Error during branch processing.")
            console.print(f"Error during branch processing: {str(e)}", style="error")
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
