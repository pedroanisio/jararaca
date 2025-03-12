"""
Tests for the Ruff linting check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from jararaca.links.ruff import RuffCheck
from jararaca.utils import CheckResult, CheckStatus


class TestRuffCheck(unittest.TestCase):
    """Test cases for the RuffCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = RuffCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("jararaca.links.ruff.run_command")
    def test_check_ruff_success(self, mock_run_command):
        """Test the Ruff check when all code passes linting checks."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["ruff", "check", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Ruff)")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[0].details, "All code passes Ruff checks.")

    @patch("jararaca.links.ruff.run_command")
    def test_check_ruff_with_issues(self, mock_run_command):
        """Test the Ruff check when code has linting issues."""
        # Setup the mock to return a failing check
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="src/module.py:10:1: E501 Line too long (100 > 88 characters)",
            stderr="",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Ruff)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Ruff issues found", results[0].details)
        self.assertIn("Line too long", results[0].details)

    @patch("jararaca.links.ruff.run_command")
    def test_check_ruff_with_errors(self, mock_run_command):
        """Test the Ruff check when it encounters errors."""
        # Setup the mock to return a failing check with stderr
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: Cannot parse src/module.py: invalid syntax",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Ruff)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Ruff issues found", results[0].details)
        self.assertIn("Cannot parse", results[0].details)

    @patch("jararaca.links.ruff.run_command")
    def test_check_ruff_with_multiple_dirs(self, mock_run_command):
        """Test the Ruff check with multiple source directories."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src", "tests"]}

        # Execute the check
        self.check._execute_check(context)

        # Verify the expected command was run with multiple directories
        mock_run_command.assert_called_once_with(
            ["ruff", "check", "src", "tests"], cwd=self.project_path
        )


if __name__ == "__main__":
    unittest.main()
