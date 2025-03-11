"""
Tests for the Linked Chain Pattern implementation.
"""

import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from src.code_quality.chain import CheckChain, CheckLink
from src.code_quality.utils import CheckResult, CheckStatus


class MockCheckLink(CheckLink):
    """Mock implementation of a check link for testing."""

    def __init__(
        self,
        name: str,
        status: CheckStatus = CheckStatus.PASSED,
        should_fail: bool = False,
    ):
        """
        Initialize a mock check link.

        Args:
            name: The name of the check.
            status: The status to return for this check.
            should_fail: Whether this check should raise an exception.
        """
        super().__init__(name)
        self.status = status
        self.should_fail = should_fail
        self.context_received = None

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute the mock check.

        Args:
            context: A dictionary containing context for the check.

        Returns:
            A list containing a single mock check result.
        """
        self.context_received = context

        if self.should_fail:
            raise Exception("Mock check failure")

        return [
            CheckResult(
                name=self.name,
                status=self.status,
                details=f"Mock check details for {self.name}",
            )
        ]


class TestCheckLink(unittest.TestCase):
    """Test cases for the CheckLink class."""

    def test_set_next(self):
        """Test setting the next link in the chain."""
        link1 = MockCheckLink("Test 1")
        link2 = MockCheckLink("Test 2")

        # Set link2 as the next link after link1
        result = link1.set_next(link2)

        # Check that set_next returns the next link
        self.assertEqual(result, link2)

        # Check that link1's next_link is set to link2
        self.assertEqual(link1.next_link, link2)

    def test_execute_single_link(self):
        """Test executing a single link in the chain."""
        link = MockCheckLink("Test")
        context = {"test": "value"}

        results = link.execute(context)

        # Check that the link received the context
        self.assertEqual(link.context_received, context)

        # Check that the results contain a single result with the expected properties
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Test")
        self.assertEqual(results[0].status, CheckStatus.PASSED)

    def test_execute_multiple_links(self):
        """Test executing multiple links in the chain."""
        link1 = MockCheckLink("Test 1", CheckStatus.PASSED)
        link2 = MockCheckLink("Test 2", CheckStatus.FAILED)
        link3 = MockCheckLink("Test 3", CheckStatus.SKIPPED)

        # Chain the links together
        link1.set_next(link2).set_next(link3)

        context = {"test": "value"}
        results = link1.execute(context)

        # Check that all links received the context
        self.assertEqual(link1.context_received, context)
        self.assertEqual(link2.context_received, context)
        self.assertEqual(link3.context_received, context)

        # Check that the results contain three results with the expected properties
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Test 1")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[1].name, "Test 2")
        self.assertEqual(results[1].status, CheckStatus.FAILED)
        self.assertEqual(results[2].name, "Test 3")
        self.assertEqual(results[2].status, CheckStatus.SKIPPED)

    def test_execute_with_exception(self):
        """Test executing a chain where one link raises an exception."""
        link1 = MockCheckLink("Test 1", CheckStatus.PASSED)
        link2 = MockCheckLink("Test 2", CheckStatus.FAILED, should_fail=True)
        link3 = MockCheckLink("Test 3", CheckStatus.SKIPPED)

        # Chain the links together
        link1.set_next(link2).set_next(link3)

        # The execution should raise an exception
        with self.assertRaises(Exception):
            link1.execute({"test": "value"})


class TestCheckChain(unittest.TestCase):
    """Test cases for the CheckChain class."""

    def test_add_link(self):
        """Test adding links to the chain."""
        chain = CheckChain()
        link1 = MockCheckLink("Test 1")
        link2 = MockCheckLink("Test 2")

        # Add link1 to the chain
        result1 = chain.add_link(link1)

        # Check that add_link returns the chain
        self.assertEqual(result1, chain)

        # Check that the head and tail are set correctly
        self.assertEqual(chain.head, link1)
        self.assertEqual(chain.tail, link1)

        # Add link2 to the chain
        result2 = chain.add_link(link2)

        # Check that add_link returns the chain
        self.assertEqual(result2, chain)

        # Check that the head and tail are set correctly
        self.assertEqual(chain.head, link1)
        self.assertEqual(chain.tail, link2)

        # Check that link1's next_link is set to link2
        self.assertEqual(link1.next_link, link2)

    def test_execute_empty_chain(self):
        """Test executing an empty chain."""
        chain = CheckChain()

        results = chain.execute({"test": "value"})

        # Check that an empty chain returns an empty list of results
        self.assertEqual(results, [])

    def test_execute_chain(self):
        """Test executing a chain with multiple links."""
        chain = CheckChain()
        link1 = MockCheckLink("Test 1", CheckStatus.PASSED)
        link2 = MockCheckLink("Test 2", CheckStatus.FAILED)
        link3 = MockCheckLink("Test 3", CheckStatus.SKIPPED)

        # Add the links to the chain
        chain.add_link(link1).add_link(link2).add_link(link3)

        context = {"test": "value"}
        results = chain.execute(context)

        # Check that all links received the context
        self.assertEqual(link1.context_received, context)
        self.assertEqual(link2.context_received, context)
        self.assertEqual(link3.context_received, context)

        # Check that the results contain three results with the expected properties
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].name, "Test 1")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[1].name, "Test 2")
        self.assertEqual(results[1].status, CheckStatus.FAILED)
        self.assertEqual(results[2].name, "Test 3")
        self.assertEqual(results[2].status, CheckStatus.SKIPPED)
