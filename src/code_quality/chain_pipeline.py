"""
Code quality pipeline implementation using the Chain of Responsibility pattern.

This module provides a more modular approach to running code quality checks
by using the Chain of Responsibility pattern, allowing checks to be added,
removed, or modified without affecting the rest of the pipeline.
"""

import configparser
import logging
import os
import subprocess
import sys
import json
import traceback
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.table import Table

from .chain import CheckChain
from .links.dependency import DependencyCheck
from .links.docstring import DocstringCheck
from .links.file_length import FileLengthCheck
from .links.formatting import FormattingCheck
from .links.function_length import FunctionLengthCheck
from .links.imports import ImportsCheck
from .links.linting import LintingCheck
from .links.naming_conventions import NamingConventionsCheck
from .links.ruff import RuffCheck
from .links.security import SecurityCheckLink
from .links.test_coverage import TestCoverageCheck
from .links.type_checking import TypeCheckingLink
from .utils import CheckResult, CheckStatus, create_summary_table, print_rich_result


def create_summary_table(passed: int, failed: int, skipped: int) -> Table:
    """Create a table summarizing the check results."""
    table = Table(show_header=False)
    table.add_row("Passed", str(passed))
    table.add_row("Failed", str(failed))
    table.add_row("Skipped", str(skipped))
    table.add_row("Total", str(passed + failed + skipped))
    return table


class CodeQualityChainPipeline:
    """
    Code quality pipeline implementation using the Chain of Responsibility pattern.

    This class orchestrates the execution of code quality checks using the
    Chain of Responsibility pattern, making it more modular and maintainable.
    """

    def __init__(self, project_path: str, config_file: Optional[str] = None):
        """
        Initialize the code quality pipeline.

        Args:
            project_path: The path to the project to check.
            config_file: Optional path to a configuration file.
        """
        self.project_path = os.path.abspath(project_path)
        self.console = Console()
        self.results: List[CheckResult] = []
        self.config = self._load_config(config_file)
        self.check_chain = self._build_check_chain()

        logging.info(f"Starting pipeline for project: {project_path}")

    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.

        Args:
            config_file: Path to the configuration file

        Returns:
            A dictionary containing the configuration
        """
        logging.info("Loading configuration.")
        config_parser = configparser.ConfigParser()

        # Default configuration
        config_parser["general"] = {
            "min_test_coverage": "80",
            "max_file_length": "300",
            "max_function_length": "50",
            "check_bandit": "true",
            "check_mypy": "true",
            "check_ruff": "true",
            "main_branch": "main",
            "enable_auto_commit": "false",
        }
        config_parser["paths"] = {
            "src_dirs": "src,app",
            "test_dir": "tests",
            "exclude_dirs": "venv,.venv,__pycache__,build,dist",
        }

        if config_file and os.path.exists(config_file):
            config_parser.read(config_file)
            logging.info(f"Configuration loaded from {config_file}.")
        else:
            logging.info("Using default configuration.")

        # Convert config to dictionary
        config = {}
        for section in config_parser.sections():
            for key, value in config_parser[section].items():
                config[key] = value

        return config

    def _build_check_chain(self) -> CheckChain:
        """
        Build the chain of code quality checks.

        Returns:
            A chain of code quality checks.
        """
        chain = CheckChain()

        # Add code quality checks to the chain
        chain.add_link(FormattingCheck())
        chain.add_link(ImportsCheck())
        chain.add_link(LintingCheck())
        chain.add_link(RuffCheck())
        chain.add_link(TypeCheckingLink())
        chain.add_link(SecurityCheckLink())

        # Get the minimum test coverage from config
        min_coverage = int(self.config.get("min_test_coverage", "80"))
        chain.add_link(TestCoverageCheck(min_coverage=min_coverage))

        chain.add_link(NamingConventionsCheck())

        # Get max lengths from config
        max_file_length = int(self.config.get("max_file_length", "300"))
        max_function_length = int(self.config.get("max_function_length", "50"))
        chain.add_link(FileLengthCheck(max_lines=max_file_length))
        chain.add_link(FunctionLengthCheck(max_lines=max_function_length))

        chain.add_link(DocstringCheck())
        chain.add_link(DependencyCheck())

        return chain

    def run(self) -> bool:
        """
        Run all code quality checks.

        Returns:
            True if all checks passed, False otherwise.
        """
        logging.info("Starting Python Code Quality Chain Pipeline.")

        self.console.print(
            "\n[bold]Running Python Code Quality Chain Pipeline[/bold]\n",
            style="white on blue",
            justify="center",
        )
        self.console.print(f"Project path: {self.project_path}")

        # Check if all required tools are installed
        self._check_prerequisites()

        # Create context for the checks
        all_src_dirs = [
            dir.strip() for dir in self.config.get("src_dirs", "src,app").split(",")
        ]
        
        # Filter out directories that don't exist
        src_dirs = []
        for dir_path in all_src_dirs:
            full_path = os.path.join(self.project_path, dir_path)
            if os.path.exists(full_path) and os.path.isdir(full_path):
                src_dirs.append(dir_path)
            else:
                logging.warning(f"Source directory '{dir_path}' does not exist, skipping.")
        
        if not src_dirs:
            logging.warning("No valid source directories found. Some checks may fail.")
        
        context = {
            "project_path": self.project_path,
            "source_dirs": src_dirs,
            "config": self.config,
        }

        # Execute the chain of checks
        self.results = self.check_chain.execute(context)

        # Print summary
        self._print_summary()

        # Return True if all checks passed
        return all(result.status == CheckStatus.PASSED for result in self.results)

    def _check_prerequisites(self) -> None:
        """
        Check if required tools are installed.
        """
        logging.info("Checking required tools.")

        # List of required tools
        required_tools = [
            "pytest",
            "black",
            "isort",
            "flake8",
            "mypy",
            "bandit",
            "ruff",
            "pylint",
            "coverage",
            "git",
        ]

        missing_tools = []
        
        for tool in required_tools:
            cmd = ["which", tool] if sys.platform != "win32" else ["where", tool]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logging.info(f"Tool found: {tool}")
                else:
                    logging.warning(f"Tool not found: {tool}")
                    missing_tools.append(tool)
            except Exception as e:
                logging.error(f"Error checking for tool {tool}: {str(e)}")
                missing_tools.append(tool)

        if missing_tools:
            missing_str = ", ".join(missing_tools)
            logging.warning(f"Missing tools that might affect checks: {missing_str}")
            self.console.print(
                f"[bold yellow]Warning: Some required tools are missing: {missing_str}[/bold yellow]"
            )
            self.console.print(
                "Some quality checks may fail. Consider installing the missing tools."
            )
        else:
            logging.info("✓ All required tools are installed.")
            self.console.print(
                "✓ All required tools are installed.",
                style="bold green"
            )

    def _print_summary(self) -> None:
        """Print a summary of the check results."""
        # First print detailed results for each check
        self.console.print("\n      Detailed Check Results      \n")
        for result in self.results:
            print_rich_result(result.name, result.status.value, result.details)

        # Then print the summary as before
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == CheckStatus.SKIPPED)

        # Create and print the summary table
        table = create_summary_table(passed, failed, skipped)
        self.console.print("\n      Pipeline Summary      ")
        self.console.print(table)

        # Print the overall status
        if failed > 0:
            self.console.print(
                "✗ Some quality checks failed. See details above.",
                style="bold red",
            )
            logging.warning("Some quality checks failed.")
        else:
            self.console.print(
                "✓ All quality checks passed!",
                style="bold green",
            )
            logging.info("All quality checks passed.")

        logging.info(
            f"Overall quality check status: {'PASSED' if failed == 0 else 'FAILED'}"
        )

    def _results_to_json(self) -> Dict[str, Any]:
        """
        Convert the check results to a JSON-serializable dictionary.
        
        Returns:
            A dictionary containing the results in a format suitable for JSON conversion.
        """
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAILED)
        skipped = sum(1 for r in self.results if r.status == CheckStatus.SKIPPED)
        
        # Create the JSON structure
        json_output = {
            "summary": {
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "total": len(self.results),
                "status": "PASSED" if failed == 0 else "FAILED"
            },
            "checks": []
        }
        
        # Add detailed information for each check
        for result in self.results:
            json_output["checks"].append({
                "name": result.name,
                "status": result.status.value,
                "details": result.details
            })
            
        return json_output
    
    def save_json_output(self, json_file: str) -> None:
        """
        Save the check results as JSON to the specified file.
        
        Args:
            json_file: Path to the file where the JSON output should be saved.
        """
        if not self.results:
            logging.warning("No results to save as JSON.")
            return
            
        json_output = self._results_to_json()
        
        try:
            with open(json_file, 'w') as f:
                json.dump(json_output, f, indent=2)
            logging.info(f"Results saved as JSON to {json_file}")
            self.console.print(f"Results saved as JSON to {json_file}", style="bold green")
        except Exception as e:
            logging.error(f"Failed to save JSON output: {str(e)}")
            self.console.print(f"Failed to save JSON output: {str(e)}", style="bold red")


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the code quality pipeline.

    Args:
        args: Command line arguments.

    Returns:
        0 if all checks passed, 1 otherwise.
    """
    parser = ArgumentParser(description="Run code quality checks on a Python project.")
    parser.add_argument(
        "project_path", help="Path to the project to check.", nargs="?", default="."
    )
    parser.add_argument(
        "--config", help="Path to a configuration file.", default=None
    )
    parser.add_argument(
        "--json-output", 
        help="Path to save results as JSON.", 
        default=None,
        dest="json_output"
    )

    parsed_args = parser.parse_args(args)

    try:
        # Initialize and run the pipeline
        pipeline = CodeQualityChainPipeline(parsed_args.project_path, parsed_args.config)
        success = pipeline.run()
        
        # Save JSON output if specified
        if parsed_args.json_output:
            pipeline.save_json_output(parsed_args.json_output)
            
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Pipeline failed with an error: {str(e)}")
        traceback.print_exc()
        return 2
