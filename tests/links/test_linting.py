"""
Tests for the linting check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.linting import LintingCheck
from code_quality.utils import CheckResult, CheckStatus


class TestLintingCheck(unittest.TestCase):
    """Test cases for the LintingCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = LintingCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("code_quality.links.linting.run_command")
    def test_check_linting_success(self, mock_run_command):
        """Test the linting check when all code passes linting checks."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["pylint", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Pylint)")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[0].details, "All code passes linting checks.")

    @patch("code_quality.links.linting.run_command")
    def test_check_linting_with_warnings(self, mock_run_command):
        """Test the linting check when code has warnings but no errors."""
        # Pylint returns exit code 4 when it finds warnings
        mock_run_command.return_value = MagicMock(
            returncode=4,
            stdout="W0612: Unused variable 'x' (unused-variable)",
            stderr="",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Pylint)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Linting issues found", results[0].details)
        self.assertIn("unused-variable", results[0].details)

    @patch("code_quality.links.linting.run_command")
    def test_check_linting_with_errors(self, mock_run_command):
        """Test the linting check when code has errors."""
        # Pylint returns exit code 2 for errors
        mock_run_command.return_value = MagicMock(
            returncode=2, stdout="E0001: Syntax error at line 5", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Pylint)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Linting issues found", results[0].details)
        self.assertIn("Syntax error", results[0].details)

    @patch("code_quality.links.linting.run_command")
    def test_check_linting_with_fatal_error(self, mock_run_command):
        """Test the linting check when pylint encounters a fatal error."""
        # Pylint returns exit code >= 16 for fatal errors
        mock_run_command.return_value = MagicMock(
            returncode=32,
            stdout="",
            stderr="Fatal error: could not process src/module.py",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Linting (Pylint)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Linting failed with an error", results[0].details)
        self.assertIn("Fatal error", results[0].details)

    @patch("code_quality.links.linting.run_command")
    def test_check_linting_with_multiple_dirs(self, mock_run_command):
        """Test the linting check with multiple source directories."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src", "tests"]}

        # Execute the check
        self.check._execute_check(context)

        # Verify the expected command was run with multiple directories
        mock_run_command.assert_called_once_with(
            ["pylint", "src", "tests"], cwd=self.project_path
        )


if __name__ == "__main__":
    unittest.main()
