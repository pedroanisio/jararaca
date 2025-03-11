"""
Tests for the code quality utils module.
"""

import unittest
from unittest.mock import MagicMock, patch

from code_quality.utils import (
    Colors,
    create_summary_table,
    format_result_output,
    print_rich_result,
    run_command,
)


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

        # Verify the function called subprocess.run correctly with ANY order of kwargs
        self.assertEqual(mock_run.call_count, 1)
        call_args, call_kwargs = mock_run.call_args
        self.assertEqual(call_args[0], command)
        self.assertEqual(call_kwargs["cwd"], cwd)
        self.assertEqual(call_kwargs["capture_output"], True)
        self.assertEqual(call_kwargs["text"], True)
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

    @patch("code_quality.utils.console")
    def test_print_rich_result_passed(self, mock_console):
        """Test printing a passed result with rich formatting."""
        name = "Test Check"
        status = "PASSED"
        details = "All tests passed."

        print_rich_result(name, status, details)

        # Verify console.print was called
        self.assertEqual(mock_console.print.call_count, 1)
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "success")

    @patch("code_quality.utils.console")
    def test_print_rich_result_failed(self, mock_console):
        """Test printing a failed result with rich formatting."""
        name = "Test Check"
        status = "FAILED"
        details = "Some tests failed."

        print_rich_result(name, status, details)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "error")

    @patch("code_quality.utils.console")
    def test_print_rich_result_skipped(self, mock_console):
        """Test printing a skipped result with rich formatting."""
        name = "Test Check"
        status = "SKIPPED"
        details = "Check was skipped."

        print_rich_result(name, status, details)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "skipped")

    @patch("code_quality.utils.console")
    def test_print_rich_result_no_details(self, mock_console):
        """Test printing a result with no details."""
        name = "Test Check"
        status = "PASSED"

        print_rich_result(name, status)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # Without details, print should be called with a Text object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check it's not a Panel
        from rich.panel import Panel

        self.assertNotIsInstance(args[0], Panel)

    def test_create_summary_table(self):
        """Test creating a summary table for pipeline results."""
        # Create a table with some results
        passed = 5
        failed = 2
        skipped = 1

        table = create_summary_table(passed, failed, skipped)

        # Check the table has the correct title
        self.assertEqual(table.title, "Pipeline Summary")

        # Check the table has the correct number of columns
        self.assertEqual(len(table.columns), 3)

        # Check the column titles
        self.assertEqual(table.columns[0].header, "Status")
        self.assertEqual(table.columns[1].header, "Count")
        self.assertEqual(table.columns[2].header, "Symbol")

        # Check the table has 3 rows (PASSED, FAILED, SKIPPED)
        self.assertEqual(len(table.rows), 3)


if __name__ == "__main__":
    unittest.main()
