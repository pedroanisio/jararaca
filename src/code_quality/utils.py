"""
Utility functions for the code quality pipeline.
"""

import logging
import subprocess
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Terminal colors for better readability
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def run_command(command: List[str], cwd: str) -> subprocess.CompletedProcess:
    """
    Run a shell command in the specified directory.

    Args:
        command: The command to run as a list of strings
        cwd: The directory to run the command in

    Returns:
        A CompletedProcess instance with command output

    Raises:
        subprocess.SubprocessError: If the command fails to execute
    """
    logger.info(f"Running command: {' '.join(command)}")
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True)


def format_result_output(name: str, status: str, details: str = "") -> str:
    """
    Format a check result for terminal output.

    Args:
        name: Name of the check
        status: Status of the check (PASSED, FAILED, SKIPPED)
        details: Details about the check result

    Returns:
        Formatted string for terminal output
    """
    if status == "PASSED":
        status_str = f"{Colors.GREEN}{status}{Colors.ENDC}"
    elif status == "FAILED":
        status_str = f"{Colors.FAIL}{status}{Colors.ENDC}"
    else:
        status_str = f"{Colors.BLUE}{status}{Colors.ENDC}"

    result = f"{Colors.BOLD}{name}:{Colors.ENDC} {status_str}"
    if details:
        result += f"\n{details}"

    return result
