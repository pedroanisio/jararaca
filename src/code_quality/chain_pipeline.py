"""
Code quality pipeline implementation using the Chain of Responsibility pattern.

This module provides a more modular approach to running code quality checks
by using the Chain of Responsibility pattern, allowing checks to be added,
removed, or modified without affecting the rest of the pipeline.
"""

import logging
import os
import sys
import traceback
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional

from rich.console import Console

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
from .pipeline_config import load_config
from .pipeline_parsers import parse_details
from .pipeline_prerequisites import check_prerequisites
from .pipeline_reporting import print_summary, results_to_json, save_json_output
from .utils import CheckResult, CheckStatus


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
        self.config = load_config(config_file)
        self.check_chain = self._build_check_chain()

        logging.info(f"Starting pipeline for project: {project_path}")

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
        check_prerequisites(self.console)

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
                logging.warning(
                    f"Source directory '{dir_path}' does not exist, skipping."
                )

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
        print_summary(self.console, self.results)

        # Return True if all checks passed
        return all(result.status == CheckStatus.PASSED for result in self.results)

    def save_json_output(self, json_file: str) -> None:
        """
        Save the check results as JSON to the specified file.

        Args:
            json_file: Path to the file where the JSON output should be saved.
        """
        if not self.results:
            logging.warning("No results to save as JSON.")
            return

        json_output = results_to_json(self.results, self.project_path, self.config)
        save_json_output(json_output, json_file, self.console)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the code quality pipeline.

    Args:
        args: Command line arguments.

    Returns:
        0 if all checks passed, 1 if checks failed, 2 if an exception occurred.
    """
    parser = ArgumentParser(description="Run code quality checks on a Python project.")
    parser.add_argument(
        "project_path", help="Path to the project to check.", nargs="?", default="."
    )
    parser.add_argument("--config", help="Path to a configuration file.", default=None)
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Enable automatic commit and branch processing",
    )
    parser.add_argument(
        "--json-output",
        help="Path to save results as JSON.",
        default=None,
        dest="json_output",
    )

    parsed_args = parser.parse_args(args)

    try:
        # Initialize and run the pipeline
        pipeline = CodeQualityChainPipeline(
            parsed_args.project_path, parsed_args.config
        )

        # Update config if auto-commit is specified
        if parsed_args.auto_commit:
            pipeline.config["enable_auto_commit"] = "true"
            logging.info("Auto-commit enabled via command line argument.")

        success = pipeline.run()

        # Save JSON output if specified
        if parsed_args.json_output:
            pipeline.save_json_output(parsed_args.json_output)

        return 0 if success else 1
    except Exception as e:
        logging.error(f"Pipeline failed with an error: {str(e)}")
        traceback.print_exc()
        return 2
