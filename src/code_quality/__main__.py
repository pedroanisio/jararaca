"""
Main entry point for code quality module.

This module allows running the code quality pipeline from the command line:
`python -m code_quality /path/to/project`
"""

from .pipeline import main

if __name__ == "__main__":
    main()
