"""
Utility functions and classes for code quality checks.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Create a rich console with custom styles
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "header": "magenta",
        "skipped": "blue",
    }
)
# Enable markup processing
console = Console(theme=custom_theme, markup=True)


# Terminal colors for better readability (kept for backwards compatibility)
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


class CheckStatus(Enum):
    """Status of a quality check."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class CheckResult:
    """Result of a code quality check."""

    name: str
    status: CheckStatus
    details: str


@dataclass
class CommandResult:
    """Result of a command execution."""

    returncode: int
    stdout: str
    stderr: str


def run_command(command: List[str], cwd: Optional[str] = None) -> CommandResult:
    """
    Run a command and return the result.

    Args:
        command: Command to run
        cwd: Working directory

    Returns:
        Result of the command execution
    """
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=False
        )
        return CommandResult(
            returncode=result.returncode, stdout=result.stdout, stderr=result.stderr
        )
    except Exception as e:
        return CommandResult(returncode=1, stdout="", stderr=str(e))


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


def print_rich_result(result: CheckResult) -> None:
    """
    Print a rich formatted check result.

    Args:
        result: Check result to print
    """
    if result.status == CheckStatus.PASSED:
        title = f"✓ {result.name}: PASSED"
        style = "green"
    elif result.status == CheckStatus.FAILED:
        title = f"✗ {result.name}: FAILED"
        style = "red"
    else:
        title = f"⚠ {result.name}: SKIPPED"
        style = "yellow"

    panel = Panel(result.details, title=title, title_align="left", border_style=style)
    console.print(panel)


def create_summary_table(passed: int, failed: int, skipped: int) -> Table:
    """
    Create a summary table for check results.

    Args:
        passed: Number of passed checks
        failed: Number of failed checks
        skipped: Number of skipped checks

    Returns:
        A rich table with the summary
    """
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("Status", style="bold")
    table.add_column("Count")
    table.add_column("Symbol")

    table.add_row("PASSED", str(passed), "✓", style="green")
    table.add_row("FAILED", str(failed), "✗", style="red")
    table.add_row("SKIPPED", str(skipped), "⚠", style="yellow")

    return table
