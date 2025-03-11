"""
Tests for the naming conventions check link.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from code_quality.links.naming_conventions import NamingConventionsCheck
from code_quality.utils import CheckStatus


class TestNamingConventionsCheck(unittest.TestCase):
    """Test cases for the NamingConventionsCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = NamingConventionsCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_naming_conventions_no_issues(self):
        """Test the naming conventions check when all naming conventions are followed."""
        # Create a project directory with a Python file that follows naming conventions
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file follows PEP 8 naming conventions
class ClassName:
    def __init__(self):
        self.attribute_name = 42
        
    def method_name(self):
        local_variable = "value"
        return local_variable

CONSTANT_VALUE = 100
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn("All code follows naming conventions", results[0].details)

    def test_check_naming_conventions_module_issue(self):
        """Test the naming conventions check when module name doesn't follow conventions."""
        # Create a project directory with a Python file with incorrect module name
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Module name should be snake_case not PascalCase
        with open(os.path.join(src_dir, "BadModuleName.py"), "w") as f:
            f.write(
                """
# This module has a name that doesn't follow conventions
class ClassName:
    def method_name(self):
        return "Hello"
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Module name 'BadModuleName'", results[0].details)
        self.assertIn("does not follow snake_case convention", results[0].details)

    def test_check_naming_conventions_class_issue(self):
        """Test the naming conventions check when class name doesn't follow conventions."""
        # Create a project directory with a Python file with incorrect class name
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file has a class name that doesn't follow conventions
class bad_class_name:  # Should be PascalCase not snake_case
    def method_name(self):
        return "Hello"
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Class name 'bad_class_name'", results[0].details)
        self.assertIn("does not follow PascalCase convention", results[0].details)

    def test_check_naming_conventions_function_issue(self):
        """Test the naming conventions check when function name doesn't follow conventions."""
        # Create a project directory with a Python file with incorrect function name
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file has a function name that doesn't follow conventions
class ClassName:
    def BadMethodName(self):  # Should be snake_case not PascalCase
        return "Hello"

def BadFunctionName():  # Should be snake_case not PascalCase
    return "World"
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Function name 'BadMethodName'", results[0].details)
        self.assertIn("Function name 'BadFunctionName'", results[0].details)
        self.assertIn("does not follow snake_case convention", results[0].details)

    def test_check_naming_conventions_variable_issue(self):
        """Test the naming conventions check when variable name doesn't follow conventions."""
        # Create a project directory with a Python file with incorrect variable name
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file has variable names that don't follow conventions
class ClassName:
    def __init__(self):
        self.BadAttribute = 42  # Should be snake_case not PascalCase
        
    def method_name(self):
        BadVariable = "value"  # Should be snake_case not PascalCase
        return BadVariable
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Variable 'BadAttribute'", results[0].details)
        self.assertIn("Variable 'BadVariable'", results[0].details)
        self.assertIn("does not follow snake_case convention", results[0].details)

    def test_check_naming_conventions_constant_issue(self):
        """Test the naming conventions check when constant name doesn't follow conventions."""
        # Create a project directory with a Python file with incorrect constant name
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file has a constant name that doesn't follow conventions
PROPER_CONSTANT = 100
bad_CONSTANT = 200  # Should be UPPER_CASE not mixed case
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Variable 'bad_CONSTANT'", results[0].details)
        self.assertIn("does not follow snake_case convention", results[0].details)

    def test_check_naming_conventions_multiple_issues(self):
        """Test the naming conventions check with multiple naming issues."""
        # Create a project directory with a Python file that has multiple issues
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "bad_Module.py"), "w") as f:
            f.write(
                """
# This file has multiple naming convention issues
class badClass:
    def Bad_method(self):
        Bad_variable = 42
        return Bad_variable

bad_CONSTANT = 100
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Module name 'bad_Module'", results[0].details)
        self.assertIn("Class name 'badClass'", results[0].details)
        self.assertIn("Function name 'Bad_method'", results[0].details)
        self.assertIn("Variable 'Bad_variable'", results[0].details)
        self.assertIn("Variable 'bad_CONSTANT'", results[0].details)

    def test_check_naming_conventions_multiple_directories(self):
        """Test the naming conventions check with multiple source directories."""
        # Create multiple source directories with Python files
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        with open(os.path.join(src_dir, "module_name.py"), "w") as f:
            f.write(
                """
# This file follows conventions
class ClassName:
    def method_name(self):
        variable_name = 42
        return variable_name
"""
            )

        # Create another source directory with an issue
        lib_dir = os.path.join(self.project_path, "lib")
        os.makedirs(lib_dir)

        with open(os.path.join(lib_dir, "BadModuleName.py"), "w") as f:
            f.write(
                """
# This file has naming issues
class goodClass:
    def BadMethod(self):
        return "Hello"
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src", "lib"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Naming convention issues found", results[0].details)
        self.assertIn("Module name 'BadModuleName'", results[0].details)
        self.assertIn("Function name 'BadMethod'", results[0].details)

    def test_check_naming_conventions_file_error(self):
        """Test the naming conventions check when there's an error reading a file."""
        # Create a source directory with a Python file
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        file_path = os.path.join(src_dir, "module_name.py")
        with open(file_path, "w") as f:
            f.write("# Some content")

        # Mock open to raise an exception
        original_open = open

        def side_effect(*args, **kwargs):
            if args[0] == file_path and kwargs.get("encoding") == "utf-8":
                raise Exception("Permission denied")
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=side_effect):
            context = {"project_path": self.project_path, "source_dirs": ["src"]}

            # Execute the check
            results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Naming Conventions")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Error reading", results[0].details)
        self.assertIn("Permission denied", results[0].details)


if __name__ == "__main__":
    unittest.main()
