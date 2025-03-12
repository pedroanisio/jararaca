"""
Tests for the utility functions in the jararaca.utils module.
"""

import unittest
from unittest.mock import MagicMock, patch

from jararaca.utils import (
    CheckResult,
    CheckStatus,
    Colors,
    CommandResult,
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
        mock_result.returncode = 0
        mock_result.stdout = "test output"
        mock_result.stderr = "test error"
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
        self.assertEqual(result.returncode, mock_result.returncode)
        self.assertEqual(result.stdout, mock_result.stdout)
        self.assertEqual(result.stderr, mock_result.stderr)

    def test_format_result_output_passed(self):
        """Test formatting a passed result for terminal output."""
        name = "Test Check"
        status = "PASSED"
        details = "All tests passed."

        result = format_result_output(name, status, details)

        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(Colors.GREEN, result)
        self.assertIn(Colors.BOLD, result)
        self.assertIn(details, result)

    def test_format_result_output_failed(self):
        """Test formatting a failed result for terminal output."""
        name = "Test Check"
        status = "FAILED"
        details = "Some tests failed."

        result = format_result_output(name, status, details)

        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(Colors.FAIL, result)
        self.assertIn(Colors.BOLD, result)
        self.assertIn(details, result)

    def test_format_result_output_skipped(self):
        """Test formatting a skipped result for terminal output."""
        name = "Test Check"
        status = "SKIPPED"
        details = ""

        result = format_result_output(name, status, details)

        self.assertIn(name, result)
        self.assertIn(status, result)
        self.assertIn(Colors.BLUE, result)
        self.assertIn(Colors.BOLD, result)

        # Check that with no details, we don't get an extra newline
        self.assertNotIn("\n", result)

    @patch("jararaca.utils.console")
    def test_print_rich_result_passed(self, mock_console):
        """Test printing a passed result with rich formatting."""
        name = "Test Check"
        status = CheckStatus.PASSED
        details = "All tests passed."

        result = CheckResult(name=name, status=status, details=details)
        print_rich_result(result)

        # Verify console.print was called
        self.assertEqual(mock_console.print.call_count, 1)
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "green")

    @patch("jararaca.utils.console")
    def test_print_rich_result_failed(self, mock_console):
        """Test printing a failed result with rich formatting."""
        name = "Test Check"
        status = CheckStatus.FAILED
        details = "Some tests failed."

        result = CheckResult(name=name, status=status, details=details)
        print_rich_result(result)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "red")

    @patch("jararaca.utils.console")
    def test_print_rich_result_skipped(self, mock_console):
        """Test printing a skipped result with rich formatting."""
        name = "Test Check"
        status = CheckStatus.SKIPPED
        details = "Check was skipped."

        result = CheckResult(name=name, status=status, details=details)
        print_rich_result(result)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "yellow")

    @patch("jararaca.utils.console")
    def test_print_rich_result_no_details(self, mock_console):
        """Test printing a result with no details."""
        name = "Test Check"
        status = CheckStatus.PASSED
        details = ""

        result = CheckResult(name=name, status=status, details=details)
        print_rich_result(result)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        # The call should have a Panel object
        args, _ = mock_console.print.call_args
        self.assertEqual(len(args), 1)
        # Check panel properties
        panel = args[0]
        self.assertEqual(panel.border_style, "green")

    def test_create_summary_table(self):
        """Test creating a summary table."""
        passed = 5
        failed = 2
        skipped = 1

        table = create_summary_table(passed, failed, skipped)

        # Check that the table has the right number of rows
        self.assertEqual(len(table.rows), 3)
        # Check that the table has the right header
        self.assertEqual(table.title, None)
        # Check that the table has the right columns
        self.assertEqual(len(table.columns), 3)
        # Check that the table has the right data
        self.assertEqual(table.columns[0].header, "Status")
        self.assertEqual(table.columns[1].header, "Count")
        self.assertEqual(table.columns[2].header, "Symbol")


if __name__ == "__main__":
    unittest.main()
