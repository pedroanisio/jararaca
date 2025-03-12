"""
Prerequisite checks for the code quality pipeline.

This module handles checking for required tools and dependencies.
"""

import logging
import subprocess
import sys
from typing import Any, List


def _check_tool_availability(tool: str) -> bool:
    """
    Check if a specific tool is available in the system.

    Args:
        tool: Name of the tool to check

    Returns:
        True if the tool is available, False otherwise
    """
    cmd = ["which", tool] if sys.platform != "win32" else ["where", tool]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Tool found: {tool}")
            return True
        else:
            logging.warning(f"Tool not found: {tool}")
            return False
    except Exception as e:
        logging.error(f"Error checking for tool {tool}: {str(e)}")
        return False


def check_prerequisites(console: Any) -> List[str]:
    """
    Check if required tools are installed.

    Args:
        console: Rich console instance for output

    Returns:
        A list of missing tools, empty if all tools are installed
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

    # Check each tool
    for tool in required_tools:
        if not _check_tool_availability(tool):
            missing_tools.append(tool)

    # Report results
    if missing_tools:
        missing_str = ", ".join(missing_tools)
        logging.warning(f"Missing tools that might affect checks: {missing_str}")
        console.print(
            f"[bold yellow]Warning: Some required tools are missing: {missing_str}[/bold yellow]"
        )
        console.print(
            "Some quality checks may fail. Consider installing the missing tools."
        )
    else:
        logging.info("✓ All required tools are installed.")
        console.print("✓ All required tools are installed.", style="bold green")

    return missing_tools
