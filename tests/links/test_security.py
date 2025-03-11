"""
Tests for the security check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.code_quality.links.security import SecurityCheckLink
from src.code_quality.utils import CheckResult, CheckStatus


class TestSecurityCheckLink(unittest.TestCase):
    """Test cases for the SecurityCheckLink class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = SecurityCheckLink()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("src.code_quality.links.security.run_command")
    def test_check_security_success(self, mock_run_command):
        """Test the security check when no security issues are found."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="No issues found", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Verify the expected command was run
        mock_run_command.assert_called_once_with(
            ["bandit", "-r", "src"], cwd=self.project_path
        )

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Security Check (Bandit)")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertEqual(results[0].details, "No security issues found.")

    @patch("src.code_quality.links.security.run_command")
    def test_check_security_with_issues(self, mock_run_command):
        """Test the security check when security issues are found."""
        # Setup the mock to return a failing check
        mock_run_command.return_value = MagicMock(
            returncode=1,
            stdout="""
>> Issue: [B602:subprocess_popen_with_shell_equals_true] subprocess call with shell=True identified, security issue.
   Severity: High   Confidence: High
   Location: src/module.py:10
9  def run_command(cmd):
10     subprocess.Popen(cmd, shell=True)
""",
            stderr="",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Security Check (Bandit)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Security issues found", results[0].details)
        self.assertIn("subprocess_popen_with_shell_equals_true", results[0].details)

    @patch("src.code_quality.links.security.run_command")
    def test_check_security_with_errors(self, mock_run_command):
        """Test the security check when bandit encounters errors."""
        # Setup the mock to return a failing check with stderr
        mock_run_command.return_value = MagicMock(
            returncode=2,
            stdout="",
            stderr="Error: Cannot process file: invalid syntax in src/module.py",
        )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Security Check (Bandit)")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Security issues found", results[0].details)
        self.assertIn("Cannot process file", results[0].details)

    @patch("src.code_quality.links.security.run_command")
    def test_check_security_with_multiple_dirs(self, mock_run_command):
        """Test the security check with multiple source directories."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="No issues found", stderr=""
        )

        context = {"project_path": self.project_path, "source_dirs": ["src", "scripts"]}

        # Execute the check
        self.check._execute_check(context)

        # Verify the expected command was run with multiple directories
        mock_run_command.assert_called_once_with(
            ["bandit", "-r", "src", "scripts"], cwd=self.project_path
        )


if __name__ == "__main__":
    unittest.main()
