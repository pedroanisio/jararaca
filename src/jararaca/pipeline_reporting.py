"""
Reporting utilities for code quality pipeline results.

This module contains utilities for formatting and outputting code quality check results.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from .pipeline_parsers import parse_details
from .utils import CheckResult, CheckStatus, create_summary_table, print_rich_result


def print_summary(console: Any, results: List[CheckResult]) -> None:
    """
    Print a summary of the check results.

    Args:
        console: Rich console instance
        results: List of check results
    """
    # First print detailed results for each check
    console.print("\n      Detailed Check Results      \n")
    for result in results:
        print_rich_result(result.name, result.status, result.details)

    # Then print the summary as before
    passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
    failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
    skipped = sum(1 for r in results if r.status == CheckStatus.SKIPPED)

    # Create and print the summary table
    table = create_summary_table(passed, failed, skipped)
    console.print("\n      Pipeline Summary      ")
    console.print(table)

    # Print the overall status
    if failed > 0:
        console.print(
            "✗ Some quality checks failed. See details above.",
            style="bold red",
        )
        logging.warning("Some quality checks failed.")
    else:
        console.print(
            "✓ All quality checks passed!",
            style="bold green",
        )
        logging.info("All quality checks passed.")

    logging.info(
        f"Overall quality check status: {'PASSED' if failed == 0 else 'FAILED'}"
    )


def _create_metadata(project_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create metadata section for the JSON output.

    Args:
        project_path: Path to the project being checked
        config: Configuration dictionary

    Returns:
        Dictionary containing metadata information
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "configuration": config,
        "version": "1.0",  # Version of the JSON format
    }


def _create_summary(results: List[CheckResult]) -> Dict[str, Any]:
    """
    Create summary section for the JSON output.

    Args:
        results: List of check results

    Returns:
        Dictionary containing summary information
    """
    # Count results by status
    passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
    failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
    skipped = sum(1 for r in results if r.status == CheckStatus.SKIPPED)

    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": len(results),
        "status": "PASSED" if failed == 0 else "FAILED",
    }


def _format_check_details(results: List[CheckResult]) -> List[Dict[str, Any]]:
    """
    Format the details of each check result.

    Args:
        results: List of check results

    Returns:
        List of dictionaries containing details for each check
    """
    checks = []

    for result in results:
        # Parse the details to extract more structured information when possible
        details_obj = parse_details(result.name, result.details)

        check_info = {
            "name": result.name,
            "status": result.status.value,
            "raw_details": result.details,  # Always include the raw details
            "details": details_obj,  # Add structured details when available
        }

        checks.append(check_info)

    return checks


def results_to_json(
    results: List[CheckResult], project_path: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert check results to a structured JSON format.

    Args:
        results: List of check results
        project_path: Path to the project being checked
        config: Configuration dictionary

    Returns:
        A dictionary with the structured JSON representation of results
    """
    # Create the JSON structure with metadata, summary, and check details
    json_output: Dict[str, Any] = {
        "metadata": _create_metadata(project_path, config),
        "summary": _create_summary(results),
        "checks": _format_check_details(results),
    }

    return json_output


def save_json_output(json_output: Dict[str, Any], json_file: str, console: Any) -> None:
    """
    Save the check results as JSON to the specified file.

    Args:
        json_output: Dictionary containing the results to save
        json_file: Path to the file where the JSON output should be saved
        console: Rich console instance for output
    """
    try:
        with open(json_file, "w") as f:
            json.dump(json_output, f, indent=2)
        logging.info(f"Results saved as JSON to {json_file}")
        console.print(f"Results saved as JSON to {json_file}", style="bold green")
    except Exception as e:
        logging.error(f"Failed to save JSON output: {str(e)}")
        console.print(f"Failed to save JSON output: {str(e)}", style="bold red")
