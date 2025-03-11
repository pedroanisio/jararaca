"""
Tests for the code quality utils module.
"""

import unittest
from unittest.mock import MagicMock, patch

from code_quality.utils import Colors, format_result_output, run_command


class TestUtils(unittest.TestCase):
    """Test cases for the utility functions."""

    @patch("subprocess.run")
    def test_run_command(self, mock_run):
        """Test the run_command function."""
        # Setup the mock
        mock_result = MagicMock()
        mock_run.return_value = mock_result

        # Call the function
        command = ["echo", "test"]
        cwd = "/test/dir"
        result = run_command(command, cwd)

        # Verify the function called subprocess.run correctly
        mock_run.assert_called_once_with(
            command, cwd=cwd, capture_output=True, text=True
        )
        # Verify the result is the mock result
        self.assertEqual(result, mock_result)

    def test_format_result_output_passed(self):
        """Test formatting a passed result."""
        name = "Test Check"
        status = "PASSED"
        details = "All tests passed."

        result = format_result_output(name, status, details)

        # Check that the result contains the expected elements
        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(details, result)
        self.assertIn(Colors.GREEN, result)
        self.assertIn(Colors.BOLD, result)

    def test_format_result_output_failed(self):
        """Test formatting a failed result."""
        name = "Test Check"
        status = "FAILED"
        details = "Some tests failed."

        result = format_result_output(name, status, details)

        # Check that the result contains the expected elements
        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(details, result)
        self.assertIn(Colors.FAIL, result)
        self.assertIn(Colors.BOLD, result)

    def test_format_result_output_skipped(self):
        """Test formatting a skipped result."""
        name = "Test Check"
        status = "SKIPPED"

        result = format_result_output(name, status)

        # Check that the result contains the expected elements
        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(Colors.BLUE, result)
        self.assertIn(Colors.BOLD, result)

        # Check that with no details, we don't get an extra newline
        self.assertNotIn("\n", result)


if __name__ == "__main__":
    unittest.main()
