"""
Tests for the formatting check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.formatting import FormattingCheck
from code_quality.utils import CheckResult, CheckStatus


class TestFormattingCheck(unittest.TestCase):
    """Test cases for the FormattingCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = FormattingCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("code_quality.links.formatting.run_command")
    def test_check_formatting_success(self, mock_run_command):
        """Test the formatting check when all files are properly formatted."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="All files are properly formatted.", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["black", "--check", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Formatting (Black)")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[0].details, "All code is properly formatted.")

    @patch("code_quality.links.formatting.run_command")
    def test_check_formatting_failure(self, mock_run_command):
        """Test the formatting check when files need formatting."""
        # Setup the mock to return a failing check
        mock_run_command.return_value = MagicMock(
            returncode=1, stdout="Would reformat file.py", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["black", "--check", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Formatting (Black)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Would reformat file.py", results[0].details)

    @patch("code_quality.links.formatting.run_command")
    def test_check_formatting_with_error(self, mock_run_command):
        """Test the formatting check when black encounters an error."""
        # Setup the mock to return an error
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: cannot format file.py: invalid syntax",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Code Formatting (Black)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Error: cannot format file.py", results[0].details)

    @patch("code_quality.links.formatting.run_command")
    def test_check_formatting_with_multiple_dirs(self, mock_run_command):
        """Test the formatting check with multiple source directories."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="All files are properly formatted.", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src", "tests"]}

        # Execute the check
        self.check._execute_check(context)

        # Verify the expected command was run with multiple directories
        mock_run_command.assert_called_once_with(
            ["black", "--check", "src", "tests"], cwd=self.project_path
        )


if __name__ == "__main__":
    unittest.main()
