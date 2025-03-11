"""
Tests for the test coverage check link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.test_coverage import TestCoverageCheck
from code_quality.utils import CheckStatus, CommandResult


class TestTestCoverageCheck(unittest.TestCase):
    """Test cases for the TestCoverageCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = TestCoverageCheck(min_coverage=80)  # Default min coverage

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_coverage_success(self):
        """Test the coverage check when coverage meets the minimum requirement."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file
        with open(os.path.join(src_dir, "module.py"), "w") as f:
            f.write(
                """
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b
"""
            )

        # Create a test directory
        tests_dir = os.path.join(self.project_path, "tests")
        os.makedirs(tests_dir)

        # Create a test file
        with open(os.path.join(tests_dir, "test_module.py"), "w") as f:
            f.write(
                """
import unittest
from src.module import add, subtract

class TestModule(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
"""
            )

        # Mock the run_command function to return a successful result with good coverage
        with patch("src.code_quality.links.test_coverage.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=0,
                stdout="""
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /tmp/project
plugins: cov-2.12.1
collected 2 items

tests/test_module.py ..                                                 [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name             Stmts   Miss  Cover
------------------------------------
src/module.py        4      0   100%
------------------------------------
TOTAL                4      0   100%

============================== 2 passed in 0.02s ===============================
""",
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                ["pytest", "--cov=src", "--cov-report=term", "--cov-fail-under", "80"],
                cwd=self.project_path,
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Test Coverage")
            self.assertEqual(results[0].status, CheckStatus.PASSED)
            self.assertIn("100%", results[0].details)
            self.assertIn("meets the minimum requirement of 80%", results[0].details)

    def test_check_coverage_failure(self):
        """Test the coverage check when coverage is below the minimum requirement."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with multiple functions
        with open(os.path.join(src_dir, "module.py"), "w") as f:
            f.write(
                """
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b
    
def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
    
def divide(a, b):
    \"\"\"Divide a by b.\"\"\"
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
"""
            )

        # Create a test directory
        tests_dir = os.path.join(self.project_path, "tests")
        os.makedirs(tests_dir)

        # Create a test file that only tests some functions
        with open(os.path.join(tests_dir, "test_module.py"), "w") as f:
            f.write(
                """
import unittest
from src.module import add, subtract

class TestModule(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
"""
            )

        # Mock the run_command function to return a result with low coverage
        with patch("src.code_quality.links.test_coverage.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=1,  # Non-zero return code indicates failure
                stdout="""
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /tmp/project
plugins: cov-2.12.1
collected 2 items

tests/test_module.py ..                                                 [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name             Stmts   Miss  Cover
------------------------------------
src/module.py       10      5    50%
------------------------------------
TOTAL               10      5    50%

FAIL Required test coverage of 80% not reached. Total coverage: 50.00%
============================== 2 passed in 0.02s ===============================
""",
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                ["pytest", "--cov=src", "--cov-report=term", "--cov-fail-under", "80"],
                cwd=self.project_path,
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Test Coverage")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertIn("50%", results[0].details)
            self.assertIn("below the minimum requirement of 80%", results[0].details)

    def test_check_coverage_custom_threshold(self):
        """Test the coverage check with a custom minimum coverage threshold."""
        # Create a check with custom min coverage
        custom_check = TestCoverageCheck(min_coverage=90)

        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file
        with open(os.path.join(src_dir, "module.py"), "w") as f:
            f.write(
                """
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b
"""
            )

        # Mock the run_command function to return a result with 85% coverage
        with patch("src.code_quality.links.test_coverage.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=1,  # Non-zero return code indicates failure
                stdout="""
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /tmp/project
plugins: cov-2.12.1
collected 2 items

tests/test_module.py ..                                                 [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name             Stmts   Miss  Cover
------------------------------------
src/module.py        4      1    85%
------------------------------------
TOTAL                4      1    85%

FAIL Required test coverage of 90% not reached. Total coverage: 85.00%
============================== 2 passed in 0.02s ===============================
""",
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = custom_check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                ["pytest", "--cov=src", "--cov-report=term", "--cov-fail-under", "90"],
                cwd=self.project_path,
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Test Coverage")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertIn("85%", results[0].details)
            self.assertIn("below the minimum requirement of 90%", results[0].details)

    def test_check_coverage_multiple_dirs(self):
        """Test the coverage check with multiple source directories."""
        # Create multiple source directories
        src_dir1 = os.path.join(self.project_path, "src")
        src_dir2 = os.path.join(self.project_path, "lib")
        os.makedirs(src_dir1)
        os.makedirs(src_dir2)

        # Create Python files in both directories
        with open(os.path.join(src_dir1, "module1.py"), "w") as f:
            f.write(
                """
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""
            )

        with open(os.path.join(src_dir2, "module2.py"), "w") as f:
            f.write(
                """
def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b
"""
            )

        # Mock the run_command function to return a successful result
        with patch("src.code_quality.links.test_coverage.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=0,
                stdout="""
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /tmp/project
plugins: cov-2.12.1
collected 2 items

tests/test_modules.py ..                                                [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name               Stmts   Miss  Cover
--------------------------------------
src/module1.py         2      0   100%
lib/module2.py         2      0   100%
--------------------------------------
TOTAL                  4      0   100%

============================== 2 passed in 0.02s ===============================
""",
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src", "lib"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                [
                    "pytest",
                    "--cov=src,lib",
                    "--cov-report=term",
                    "--cov-fail-under",
                    "80",
                ],
                cwd=self.project_path,
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Test Coverage")
            self.assertEqual(results[0].status, CheckStatus.PASSED)
            self.assertIn("100%", results[0].details)
            self.assertIn("meets the minimum requirement of 80%", results[0].details)

    def test_check_coverage_error(self):
        """Test the coverage check when there's an error running pytest."""
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

        # Mock the run_command function to return an error result
        with patch("src.code_quality.links.test_coverage.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=1,
                stdout="",
                stderr="""
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.10.0, pluggy-0.13.1
rootdir: /tmp/project
plugins: cov-2.12.1
collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_syntax_error.py _________________
ImportError: cannot import name 'function_with_syntax_error' from 'src.syntax_error'
=========================== short test summary info ============================
ERROR tests/test_syntax_error.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.05s ===============================
""",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                ["pytest", "--cov=src", "--cov-report=term", "--cov-fail-under", "80"],
                cwd=self.project_path,
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Test Coverage")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertIn("Failed to determine test coverage", results[0].details)
            self.assertIn("ImportError", results[0].details)

    def test_extract_coverage_valid_output(self):
        """Test the _extract_coverage method with valid output."""
        output = """
---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name             Stmts   Miss  Cover
------------------------------------
src/module.py        4      0   100%
------------------------------------
TOTAL                4      0   100%
"""
        coverage = self.check._extract_coverage(output)
        self.assertEqual(coverage, 100)

    def test_extract_coverage_partial_coverage(self):
        """Test the _extract_coverage method with partial coverage."""
        output = """
---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name             Stmts   Miss  Cover
------------------------------------
src/module.py       10      5    50%
------------------------------------
TOTAL               10      5    50%
"""
        coverage = self.check._extract_coverage(output)
        self.assertEqual(coverage, 50)

    def test_extract_coverage_invalid_output(self):
        """Test the _extract_coverage method with invalid output."""
        output = "No coverage information found"
        coverage = self.check._extract_coverage(output)
        self.assertIsNone(coverage)


if __name__ == "__main__":
    unittest.main()
