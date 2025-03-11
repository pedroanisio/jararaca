"""
Tests for the imports check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.imports import ImportsCheck
from code_quality.utils import CheckResult, CheckStatus


class TestImportsCheck(unittest.TestCase):
    """Test cases for the ImportsCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = ImportsCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("code_quality.links.imports.run_command")
    def test_check_imports_success(self, mock_run_command):
        """Test the imports check when all imports are properly sorted."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["isort", "--check-only", "--diff", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Import Sorting (isort)")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[0].details, "All imports are properly sorted.")

    @patch("code_quality.links.imports.run_command")
    def test_check_imports_failure(self, mock_run_command):
        """Test the imports check when imports need sorting."""
        # Setup the mock to return a failing check
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="ERROR: src/code_quality/chain_pipeline.py Imports are incorrectly sorted.",
            stderr="",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["isort", "--check-only", "--diff", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Import Sorting (isort)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("incorrectly sorted", results[0].details)

    @patch("code_quality.links.imports.run_command")
    def test_check_imports_with_errors(self, mock_run_command):
        """Test the imports check when isort encounters errors."""
        # Setup the mock to return an error
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="ERROR: src/code_quality/chain_pipeline.py Imports are incorrectly sorted.",
            stderr="Error processing file: syntax error",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Import Sorting (isort)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("incorrectly sorted", results[0].details)
        self.assertIn("Error processing file", results[0].details)

    @patch("code_quality.links.imports.run_command")
    def test_check_imports_with_multiple_dirs(self, mock_run_command):
        """Test the imports check with multiple source directories."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(returncode=0, stdout="", stderr="")

        context = {"project_path": self.project_path, "source_dirs": ["src", "tests"]}

        # Execute the check
        self.check._execute_check(context)

        # Verify the expected command was run with multiple directories
        mock_run_command.assert_called_once_with(
            ["isort", "--check-only", "--diff", "src", "tests"], cwd=self.project_path
        )


if __name__ == "__main__":
    unittest.main()
