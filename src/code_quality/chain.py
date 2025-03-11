"""
Linked Chain Pattern implementation for code quality checks.

This module provides a flexible way to chain code quality checks together.
Each check is a separate link in the chain, and they can be executed sequentially.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .utils import CheckResult, CheckStatus


class CheckLink(ABC):
    """
    Abstract base class for check links in the chain.

    Each check link performs a specific code quality check and can pass the
    execution to the next link in the chain if one exists.
    """

    def __init__(self, name: str):
        """
        Initialize a check link.

        Args:
            name: The name of the check.
        """
        self.name = name
        self.next_link: Optional["CheckLink"] = None

    def set_next(self, next_link: "CheckLink") -> "CheckLink":
        """
        Set the next link in the chain.

        Args:
            next_link: The next check link to be executed after this one.

        Returns:
            The next link, allowing for method chaining.
        """
        self.next_link = next_link
        return next_link

    def execute(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute this check and then pass execution to the next link if it exists.

        Args:
            context: A dictionary containing context for the checks.

        Returns:
            A list of check results from this link and all subsequent links.
        """
        results = self._execute_check(context)

        # If there's a next link, execute it and combine the results
        if self.next_link:
            next_results = self.next_link.execute(context)
            results.extend(next_results)

        return results

    @abstractmethod
    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute the specific check implementation.

        This method should be implemented by concrete check links.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list of check results from this check.
        """
        pass


class CheckChain:
    """
    A chain of code quality checks that can be executed sequentially.
    """

    def __init__(self):
        """Initialize an empty chain of checks."""
        self.head: Optional[CheckLink] = None
        self.tail: Optional[CheckLink] = None

    def add_link(self, link: CheckLink) -> "CheckChain":
        """
        Add a link to the end of the chain.

        Args:
            link: The check link to add to the chain.

        Returns:
            Self, allowing for method chaining.
        """
        if not self.head:
            self.head = link
            self.tail = link
        else:
            self.tail.set_next(link)
            self.tail = link

        return self

    def execute(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute all checks in the chain.

        Args:
            context: A dictionary containing context for the checks.

        Returns:
            A list of check results from all links in the chain.
        """
        if not self.head:
            return []

        return self.head.execute(context)
