"""
Tests for the type checking link.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.code_quality.links.type_checking import TypeCheckingLink
from src.code_quality.utils import CheckStatus, CommandResult


class TestTypeCheckingLink(unittest.TestCase):
    """Test cases for the TypeCheckingLink class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = TypeCheckingLink()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_type_checking_success(self):
        """Test the type checking when all code passes."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with proper type annotations
        with open(os.path.join(src_dir, "typed_file.py"), "w") as f:
            f.write(
                """
from typing import List, Dict, Optional

def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

def get_names() -> List[str]:
    \"\"\"Return a list of names.\"\"\"
    return ["Alice", "Bob", "Charlie"]

class Person:
    \"\"\"A person class with typed attributes.\"\"\"
    
    def __init__(self, name: str, age: int):
        \"\"\"Initialize a person.\"\"\"
        self.name: str = name
        self.age: int = age
        
    def get_info(self) -> Dict[str, str]:
        \"\"\"Return person info as a dictionary.\"\"\"
        return {
            "name": self.name,
            "age": str(self.age)
        }
"""
            )

        # Mock the run_command function to return a successful result
        with patch("src.code_quality.links.type_checking.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=0,
                stdout="Success: no issues found in 1 source file",
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(["mypy", "src"], cwd=self.project_path)

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Type Checking (mypy)")
            self.assertEqual(results[0].status, CheckStatus.PASSED)
            self.assertIn("All code passes type checking", results[0].details)

    def test_check_type_checking_with_issues(self):
        """Test the type checking when there are type issues."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with type errors
        with open(os.path.join(src_dir, "typed_file_with_errors.py"), "w") as f:
            f.write(
                """
from typing import List

def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers but return a string (type error).\"\"\"
    return str(a + b)  # Type error: Incompatible return value

def process_list(items: List[int]) -> None:
    \"\"\"Process a list of integers.\"\"\"
    for item in items:
        print(item)
        
# Call with wrong type
process_list("not a list")  # Type error: Argument has incompatible type
"""
            )

        # Mock the run_command function to return a result with type errors
        with patch("src.code_quality.links.type_checking.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=1,
                stdout=(
                    'src/typed_file_with_errors.py:5: error: Incompatible return value type (got "str", expected "int")\n'
                    'src/typed_file_with_errors.py:12: error: Argument 1 to "process_list" has incompatible type "str"; expected "List[int]"\n'
                    "Found 2 errors in 1 file (checked 1 source file)"
                ),
                stderr="",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(["mypy", "src"], cwd=self.project_path)

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Type Checking (mypy)")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertIn("Type checking issues found", results[0].details)
            self.assertIn("Incompatible return value type", results[0].details)
            self.assertIn("has incompatible type", results[0].details)

    def test_check_type_checking_with_errors(self):
        """Test the type checking when there are syntax errors."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with syntax errors
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

        # Mock the run_command function to return a result with syntax errors
        with patch("src.code_quality.links.type_checking.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=1,
                stdout="",
                stderr="src/syntax_error.py:4: error: invalid syntax",
            )

            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(["mypy", "src"], cwd=self.project_path)

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Type Checking (mypy)")
            self.assertEqual(results[0].status, CheckStatus.FAILED)
            self.assertIn("Type checking issues found", results[0].details)
            self.assertIn("Errors", results[0].details)
            self.assertIn("invalid syntax", results[0].details)

    def test_check_type_checking_with_multiple_dirs(self):
        """Test the type checking with multiple source directories."""
        # Create multiple source directories
        src_dir1 = os.path.join(self.project_path, "src")
        src_dir2 = os.path.join(self.project_path, "tests")
        os.makedirs(src_dir1)
        os.makedirs(src_dir2)

        # Create Python files in both directories
        with open(os.path.join(src_dir1, "module.py"), "w") as f:
            f.write(
                """
from typing import List

def get_names() -> List[str]:
    \"\"\"Return a list of names.\"\"\"
    return ["Alice", "Bob", "Charlie"]
"""
            )

        with open(os.path.join(src_dir2, "test_module.py"), "w") as f:
            f.write(
                """
from typing import List
import unittest

class TestModule(unittest.TestCase):
    def test_get_names(self) -> None:
        \"\"\"Test the get_names function.\"\"\"
        names: List[str] = ["Alice", "Bob", "Charlie"]
        self.assertEqual(names, ["Alice", "Bob", "Charlie"])
"""
            )

        # Mock the run_command function to return a successful result
        with patch("src.code_quality.links.type_checking.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                returncode=0,
                stdout="Success: no issues found in 2 source files",
                stderr="",
            )

            context = {
                "project_path": self.project_path,
                "source_dirs": ["src", "tests"],
            }

            # Execute the check
            results = self.check._execute_check(context)

            # Verify run_command was called with the correct arguments
            mock_run.assert_called_once_with(
                ["mypy", "src", "tests"], cwd=self.project_path
            )

            # Check that the result was created correctly
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Type Checking (mypy)")
            self.assertEqual(results[0].status, CheckStatus.PASSED)
            self.assertIn("All code passes type checking", results[0].details)


if __name__ == "__main__":
    unittest.main()
