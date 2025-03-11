"""
Main entry point for the code quality tool.
"""

import logging
import sys

from .chain_pipeline import main as chain_main


def main() -> int:
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

    # Clean up any legacy --use-chain flags which are no longer needed
    args = [arg for arg in args if arg != "--use-chain"]

    # Call the chain-based implementation
    return chain_main(args)


if __name__ == "__main__":
    sys.exit(main())
