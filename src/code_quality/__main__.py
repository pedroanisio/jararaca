"""
Main entry point for the code quality tool.
"""

import logging
import sys
from typing import List

from .chain_pipeline import main as chain_main
from .pipeline import main as old_main


def main():
    """
    Execute the code quality checks.

    This is the main entry point for the code quality tool.
    It parses command line arguments and executes the checks.

    Returns:
        int: The exit code (0 for success, non-zero for failure)
    """
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Get command-line arguments
    args = sys.argv[1:]

    # Call the main function with args
    if "--use-chain" in args:
        # Remove the --use-chain flag
        args = [arg for arg in args if arg != "--use-chain"]
        return chain_main(args)
    else:
        # Use the original pipeline for backward compatibility
        return old_main(args)


if __name__ == "__main__":
    sys.exit(main())
