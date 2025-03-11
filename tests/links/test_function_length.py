"""
Tests for the function length check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.function_length import FunctionLengthCheck
from code_quality.utils import CheckResult, CheckStatus


class TestFunctionLengthCheck(unittest.TestCase):
    """Test cases for the FunctionLengthCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = FunctionLengthCheck(max_lines=50)  # Default max lines

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_function_length_no_violations(self):
        """Test the function length check when all functions are under the limit."""
        # Create a source directory with files under the limit
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with a short function
        with open(os.path.join(src_dir, "short_function.py"), "w") as f:
            f.write(
                """
def short_function():
    \"\"\"A short function.\"\"\"
    a = 1
    b = 2
    return a + b
"""
            )

        # Create another file with multiple short functions
        with open(os.path.join(src_dir, "multiple_short_functions.py"), "w") as f:
            f.write(
                """
def function1():
    \"\"\"First short function.\"\"\"
    return 1

def function2():
    \"\"\"Second short function.\"\"\"
    return 2

class TestClass:
    def method1(self):
        \"\"\"A short method.\"\"\"
        return 3
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn("All functions are under 50 lines", results[0].details)

    def test_check_function_length_with_violations(self):
        """Test the function length check when functions exceed the limit."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with a short function
        with open(os.path.join(src_dir, "short_function.py"), "w") as f:
            f.write(
                """
def short_function():
    \"\"\"A short function.\"\"\"
    a = 1
    b = 2
    return a + b
"""
            )

        # Create a file with a long function
        with open(os.path.join(src_dir, "long_function.py"), "w") as f:
            f.write("def long_function():\n")
            f.write('    """A long function."""\n')
            for i in range(100):  # Default max is 50
                f.write(f"    x_{i} = {i}\n")
            f.write("    return 42\n")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("long_function.py", results[0].details)
        self.assertIn("long_function", results[0].details)
        self.assertIn("103 lines", results[0].details)  # Actual line count is 103

    def test_check_function_length_with_multiple_violations(self):
        """Test the function length check when multiple functions exceed the limit."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with multiple long functions
        with open(os.path.join(src_dir, "multiple_long_functions.py"), "w") as f:
            # First long function
            f.write("def long_function1():\n")
            f.write('    """First long function."""\n')
            for i in range(60):
                f.write(f"    x_{i} = {i}\n")
            f.write("    return 42\n\n")

            # Second long function
            f.write("def long_function2():\n")
            f.write('    """Second long function."""\n')
            for i in range(70):
                f.write(f"    y_{i} = {i}\n")
            f.write("    return 84\n\n")

            # A class with a long method
            f.write("class TestClass:\n")
            f.write("    def long_method(self):\n")
            f.write('        """A long method."""\n')
            for i in range(55):
                f.write(f"        z_{i} = {i}\n")
            f.write("        return 126\n")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("multiple_long_functions.py", results[0].details)
        self.assertIn("long_function1", results[0].details)
        self.assertIn("long_function2", results[0].details)
        self.assertIn("long_method", results[0].details)

    def test_check_function_length_custom_max_lines(self):
        """Test the function length check with a custom maximum line limit."""
        # Create a check with custom max lines
        custom_check = FunctionLengthCheck(max_lines=10)

        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with a medium length function
        with open(os.path.join(src_dir, "medium_function.py"), "w") as f:
            f.write("def medium_function():\n")
            f.write('    """A medium function."""\n')
            for i in range(15):  # Exceeds custom max of 10
                f.write(f"    x_{i} = {i}\n")
            f.write("    return 42\n")

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = custom_check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("medium_function.py", results[0].details)
        self.assertIn("medium_function", results[0].details)
        self.assertIn("10 lines", results[0].details)  # Custom limit mentioned

    def test_check_function_length_with_syntax_error(self):
        """Test the function length check when there's a syntax error in a file."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with a syntax error
        with open(os.path.join(src_dir, "syntax_error.py"), "w") as f:
            f.write(
                """
def function_with_syntax_error():
    \"\"\"A function with a syntax error.\"\"\"
    if True
        print("Missing colon after if statement")
    return 42
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("syntax_error.py", results[0].details)
        self.assertIn("Syntax error", results[0].details)

    def test_check_function_length_with_file_error(self):
        """Test the function length check when there's an error reading a file."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file that will trigger an error
        file_path = os.path.join(src_dir, "error_file.py")
        with open(file_path, "w") as f:
            f.write("# File content\n")

        # Patch os.walk to return our test file
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(src_dir, [], ["error_file.py"])]

            # Patch open to raise an exception when reading the file
            with patch("builtins.open") as mock_open:
                # First call to open succeeds (during file creation), subsequent calls fail
                mock_open.side_effect = [
                    mock_open.return_value,  # First call succeeds
                    Exception("Permission denied"),  # Second call fails
                ]

                context = {"project_path": self.project_path, "source_dirs": ["src"]}

                # Execute the check
                results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Function Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Error", results[0].details)

    def test_check_function_length_no_project_path(self):
        """Test the function length check when no project path is provided."""
        context = {"project_path": "", "source_dirs": ["src"]}

        # Patch the CheckResult constructor to handle the 'message' parameter
        with patch(
            "code_quality.links.function_length.CheckResult"
        ) as mock_check_result:
            # Create a mock CheckResult instance
            mock_result = MagicMock()
            mock_result.name = "Function Length"
            mock_result.status = CheckStatus.FAILED
            mock_result.details = "No project path provided"

            # Configure the mock to return our mock result
            mock_check_result.return_value = mock_result

            # Execute the check
            results = self.check._execute_check(context)

            # Verify that CheckResult was called with the expected arguments
            mock_check_result.assert_called_once_with(
                name="Function Length",
                status=CheckStatus.FAILED,
                message="No project path provided",
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Function Length")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertEqual(results[0].details, "No project path provided")


if __name__ == "__main__":
    unittest.main()
