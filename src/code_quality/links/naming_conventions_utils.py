"""
Utility functions and patterns for naming convention checks.

This module contains regex patterns and utility functions used by the naming conventions check.
"""

import re

# Regex patterns for different naming conventions
MODULE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
CLASS_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
FUNCTION_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
VARIABLE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
CONSTANT_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

# Regex for docstrings and comments to be excluded from searches
DOCSTRING_TRIPLE_QUOTE = re.compile(r'""".*?"""', re.DOTALL)
DOCSTRING_SINGLE_QUOTE = re.compile(r"'''.*?'''", re.DOTALL)
COMMENT_PATTERN = re.compile(r"#.*$", re.MULTILINE)

# Define patterns for recognized exceptions
AST_VISITOR_PATTERN = re.compile(r"^visit_[A-Z][a-zA-Z0-9]*$")
DUNDER_PATTERN = re.compile(r"^__[a-z][a-z0-9_]*__$")

# Common words used in docstrings that might cause false positives
COMMON_WORDS = [
    "for",
    "which",
    "from",
    "class",
    "definition",
    "orchestrates",
    "contents",
    "names",
    "function",
    "methods",
    "module",
    "documentation",
]

# Python keywords that should be skipped in variable name checks
PYTHON_KEYWORDS = [
    "self",
    "cls",
    "True",
    "False",
    "None",
    "import",
    "from",
    "as",
    "class",
    "def",
    "for",
    "if",
    "return",
    "yield",
]


def strip_comments_and_docstrings(content: str) -> str:
    """
    Remove comments and docstrings from the content.

    Args:
        content: The content to process

    Returns:
        The content with comments and docstrings removed
    """
    # First remove triple-quoted docstrings
    content = DOCSTRING_TRIPLE_QUOTE.sub("", content)
    # Then remove single-quoted docstrings
    content = DOCSTRING_SINGLE_QUOTE.sub("", content)
    # Finally remove comments
    content = COMMENT_PATTERN.sub("", content)
    return content


def should_skip_variable(variable_name: str) -> bool:
    """
    Check if a variable name should be skipped in the naming convention check.

    Args:
        variable_name: The name of the variable to check

    Returns:
        True if the variable should be skipped, False otherwise
    """
    return variable_name in PYTHON_KEYWORDS or variable_name.lower() in COMMON_WORDS
