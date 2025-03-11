"""
Code quality check links package.

This package contains implementations of the CheckLink abstract base class
for specific code quality checks that can be chained together.
"""

from ..chain import CheckLink as CheckLink  # Explicit re-export

__all__ = ["CheckLink"]  # Define what's available when importing from this package
