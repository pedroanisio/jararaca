"""
Utility functions for the code quality pipeline.
"""

import logging
import subprocess
from typing import Any, Dict, List, Optional

from rich.console import Console
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
console = Console(theme=custom_theme)


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


def run_command(
    command: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
) -> subprocess.CompletedProcess:
    """
    Run a command and return the result.

    Args:
        command: Command to run as a list of strings
        cwd: Working directory to run the command in
        env: Environment variables to set

    Returns:
        CompletedProcess instance with return code, stdout, and stderr
    """
    logger.info(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, env=env)
    return result


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


def print_rich_result(name: str, status: str, details: str = "") -> None:
    """
    Print a check result with rich formatting.

    Args:
        name: Name of the check
        status: Status of the check (PASSED, FAILED, SKIPPED)
        details: Details about the check result
    """
    if status == "PASSED":
        status_style = "success"
        icon = "✓"
    elif status == "FAILED":
        status_style = "error"
        icon = "✗"
    else:
        status_style = "skipped"
        icon = "⚠"

    # Create a panel for each check result
    text = Text()
    text.append(f"{icon} {name}: ", style="bold")
    text.append(status, style=status_style)

    if details:
        panel = Panel(
            Text(details.strip()),
            title=text,
            border_style=status_style,
            expand=False,
        )
        console.print(panel)
    else:
        console.print(text)


def create_summary_table(passed: int, failed: int, skipped: int) -> Table:
    """
    Create a rich table for the summary.

    Args:
        passed: Number of passed checks
        failed: Number of failed checks
        skipped: Number of skipped checks

    Returns:
        Rich Table object
    """
    table = Table(title="Pipeline Summary", show_header=True, show_lines=True)
    table.add_column("Status", style="bold")
    table.add_column("Count")
    table.add_column("Symbol")

    table.add_row("PASSED", f"[success]{passed}[/success]", "✓")
    table.add_row("FAILED", f"[error]{failed}[/error]", "✗")
    table.add_row("SKIPPED", f"[skipped]{skipped}[/skipped]", "⚠")

    return table
