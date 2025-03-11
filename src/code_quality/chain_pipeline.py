"""
Code quality pipeline implementation using the Chain of Responsibility pattern.

This module provides a more modular approach to running code quality checks
by using the Chain of Responsibility pattern, allowing checks to be added,
removed, or modified without affecting the rest of the pipeline.
"""

import logging
import os
import sys
from argparse import ArgumentParser
from typing import Any, Dict, List, Optional

from rich.console import Console

from .chain import CheckChain
from .checks import (
    FormattingCheck,
    ImportsCheck,
    LintingCheck,
    TestCoverageCheck,
)
from .utils import CheckResult, CheckStatus, create_summary_table, print_rich_result


class CodeQualityChainPipeline:
    """
    Code quality pipeline implementation using the Chain of Responsibility pattern.

    This class orchestrates the execution of code quality checks using the
    Chain of Responsibility pattern, making it more modular and maintainable.
    """

    def __init__(self, project_path: str):
        """
        Initialize the code quality pipeline.

        Args:
            project_path: The path to the project to check.
        """
        self.project_path = os.path.abspath(project_path)
        self.console = Console()
        self.results: List[CheckResult] = []
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
        chain.add_link(TestCoverageCheck(min_coverage=80))

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

        # Create context for the checks
        context = {
            "project_path": self.project_path,
            "source_dirs": ["src"],
        }

        # Execute the chain of checks
        self.results = self.check_chain.execute(context)

        # Print summary
        self._print_summary()

        # Return True if all checks passed
        return all(result.status == CheckStatus.PASSED for result in self.results)

    def _print_summary(self) -> None:
        """Print a summary of the check results."""
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


def main(args: Optional[List[str]] = None) -> int:
    """
    Execute the code quality checks.

    Args:
        args: Command line arguments. If None, sys.argv[1:] will be used.

    Returns:
        An exit code (0 for success, non-zero for failure).
    """
    if args is None:
        args = sys.argv[1:]

    # Parse command line arguments
    parser = ArgumentParser(description="Run code quality checks on a Python project")
    parser.add_argument(
        "project_path",
        help="Path to the Python project to check",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    try:
        # Create and run the pipeline
        pipeline = CodeQualityChainPipeline(parsed_args.project_path)
        result = pipeline.run()

        logging.info("Pipeline finished.")

        # Return appropriate exit code
        return 0 if result else 1

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return 1
