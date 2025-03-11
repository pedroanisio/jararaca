"""
Tests for the docstring check link.
"""

import ast
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.docstring import DocstringCheck, DocstringVisitor
from code_quality.utils import CheckStatus


class TestDocstringCheck(unittest.TestCase):
    """Test cases for the DocstringCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = DocstringCheck(skip_private=True, skip_test_files=True)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_docstring_no_violations(self):
        """Test the docstring check when all modules, classes, and functions have docstrings."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with proper docstrings
        with open(os.path.join(src_dir, "good_docstrings.py"), "w") as f:
            f.write(
                '''"""
This module has a proper docstring.
"""

class GoodClass:
    """This class has a docstring."""
    
    def good_method(self):
        """This method has a docstring."""
        pass
        
    def __init__(self):
        """Constructor has a docstring."""
        pass
        
    def __str__(self):
        """Magic method has a docstring."""
        return "GoodClass"
        
    def _private_method(self):
        # Private method doesn't need a docstring
        pass


def good_function():
    """This function has a docstring."""
    return True


async def good_async_function():
    """This async function has a docstring."""
    pass
'''
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn(
            "All modules, classes, and functions have docstrings", results[0].details
        )

    @patch("src.code_quality.links.docstring.DocstringVisitor")
    def test_check_docstring_with_violations(self, mock_visitor_class):
        """Test the docstring check when modules, classes, or functions are missing docstrings."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with missing docstrings
        with open(os.path.join(src_dir, "missing_docstrings.py"), "w") as f:
            f.write(
                """# This is not a proper module docstring

class BadClass:
    # Missing class docstring
    
    def bad_method(self):
        # Missing method docstring
        pass
        
    def __init__(self):
        # Missing constructor docstring
        pass
        
    def _private_method(self):
        # Private method doesn't need a docstring
        pass


def bad_function():
    # Missing function docstring
    return False
"""
            )

        # Mock the DocstringVisitor to return the expected missing docstrings
        mock_visitor = MagicMock()
        mock_visitor.missing_docstrings = [
            ("module", "", 1),
            ("class", "BadClass", 3),
            ("function", "bad_method", 6),
            ("function", "__init__", 10),
            ("function", "bad_function", 19),
        ]
        mock_visitor.has_module_docstring = False
        mock_visitor_class.return_value = mock_visitor

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)

    def test_check_docstring_skip_test_files(self):
        """Test the docstring check when test files are skipped."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a test file with missing docstrings
        with open(os.path.join(src_dir, "test_something.py"), "w") as f:
            f.write(
                """# This test file is missing docstrings

class TestClass:
    # Missing class docstring
    
    def test_method(self):
        # Missing method docstring
        pass
"""
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly (should pass as test files are skipped)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn(
            "All modules, classes, and functions have docstrings", results[0].details
        )

    @patch("src.code_quality.links.docstring.DocstringVisitor")
    def test_check_docstring_include_test_files(self, mock_visitor_class):
        """Test the docstring check when test files are included."""
        # Create a check that doesn't skip test files
        check = DocstringCheck(skip_private=True, skip_test_files=False)

        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a test file with missing docstrings
        with open(os.path.join(src_dir, "test_something.py"), "w") as f:
            f.write(
                """# This test file is missing docstrings

class TestClass:
    # Missing class docstring
    
    def test_method(self):
        # Missing method docstring
        pass
"""
            )

        # Mock the DocstringVisitor to return the expected missing docstrings
        mock_visitor = MagicMock()
        mock_visitor.missing_docstrings = [
            ("module", "", 1),
            ("class", "TestClass", 3),
            ("function", "test_method", 6),
        ]
        mock_visitor.has_module_docstring = False
        mock_visitor_class.return_value = mock_visitor

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = check._execute_check(context)

        # Check that the result was created correctly (should fail as test files are included)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)

    @patch("src.code_quality.links.docstring.DocstringVisitor")
    def test_check_docstring_include_private(self, mock_visitor_class):
        """Test the docstring check when private methods are included."""
        # Create a check that doesn't skip private methods
        check = DocstringCheck(skip_private=False, skip_test_files=True)

        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a file with missing docstrings in private methods
        with open(os.path.join(src_dir, "private_methods.py"), "w") as f:
            f.write(
                '''"""
Module with proper docstring but missing private method docstrings.
"""

class SomeClass:
    """Class with proper docstring."""
    
    def public_method(self):
        """Public method has a docstring."""
        pass
        
    def _private_method(self):
        # Private method missing docstring
        pass
        
    def _another_private_method(self):
        # Another private method missing docstring
        pass
'''
            )

        # Mock the DocstringVisitor to return the expected missing docstrings
        mock_visitor = MagicMock()
        mock_visitor.missing_docstrings = [
            ("function", "_private_method", 12),
            ("function", "_another_private_method", 16),
        ]
        mock_visitor.has_module_docstring = True
        mock_visitor_class.return_value = mock_visitor

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)

    @patch("src.code_quality.links.docstring.DocstringVisitor")
    def test_check_docstring_with_multiple_dirs(self, mock_visitor_class):
        """Test the docstring check with multiple source directories."""
        # Create multiple source directories
        src_dir1 = os.path.join(self.project_path, "src")
        src_dir2 = os.path.join(self.project_path, "lib")
        os.makedirs(src_dir1)
        os.makedirs(src_dir2)

        # Create files in both directories
        with open(os.path.join(src_dir1, "good_file.py"), "w") as f:
            f.write(
                '''"""
This module has a proper docstring.
"""

def good_function():
    """This function has a docstring."""
    return True
'''
            )

        with open(os.path.join(src_dir2, "bad_file.py"), "w") as f:
            f.write(
                """# This module is missing a proper docstring

def bad_function():
    # Missing docstring
    return False
"""
            )

        # Mock the DocstringVisitor for good file
        mock_visitor_good = MagicMock()
        mock_visitor_good.missing_docstrings = []
        mock_visitor_good.has_module_docstring = True

        # Mock the DocstringVisitor for bad file
        mock_visitor_bad = MagicMock()
        mock_visitor_bad.missing_docstrings = [
            ("module", "", 1),
            ("function", "bad_function", 3),
        ]
        mock_visitor_bad.has_module_docstring = False

        # Configure the mock visitor class to return different visitor instances
        mock_visitor_class.side_effect = [mock_visitor_good, mock_visitor_bad]

        context = {"project_path": self.project_path, "source_dirs": ["src", "lib"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)

    def test_check_docstring_with_syntax_error(self):
        """Test the docstring check when there's a syntax error in a file."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file with a syntax error
        with open(os.path.join(src_dir, "syntax_error.py"), "w") as f:
            f.write(
                '''"""
This module has a proper docstring but a syntax error.
"""

def function_with_syntax_error():
    """This function has a docstring but a syntax error."""
    if True
        print("Missing colon after if statement")
    return 42
'''
            )

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)
        self.assertIn("syntax_error.py", results[0].details)
        self.assertIn("Syntax error", results[0].details)

    def test_check_docstring_with_file_error(self):
        """Test the docstring check when there's an error reading a file."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a Python file that will trigger an error
        file_path = os.path.join(src_dir, "error_file.py")
        with open(file_path, "w") as f:
            f.write("# File content\n")

        # Patch open to raise an exception when reading the file
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
        self.assertEqual(results[0].name, "Docstring Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Missing docstrings found", results[0].details)
        self.assertIn("error_file.py", results[0].details)
        self.assertIn("Error:", results[0].details)

    def test_docstring_visitor(self):
        """Test the DocstringVisitor class directly."""
        # Create some Python code with and without docstrings
        code = '''"""
Module docstring.
"""

class ClassWithDocstring:
    """Class docstring."""
    
    def method_with_docstring(self):
        """Method docstring."""
        pass
        
    def _private_method(self):
        # No docstring needed
        pass

class ClassWithoutDocstring:
    
    def method_without_docstring(self):
        pass

def function_with_docstring():
    """Function docstring."""
    pass

def function_without_docstring():
    pass

async def async_function_with_docstring():
    """Async function docstring."""
    pass

async def async_function_without_docstring():
    pass
'''

        # Parse the code
        tree = ast.parse(code)

        # Create a visitor that skips private methods
        visitor = DocstringVisitor(skip_private=True)
        visitor.visit(tree)

        # Check that the missing docstrings were found
        missing_docstrings = visitor.missing_docstrings
        self.assertEqual(len(missing_docstrings), 4)

        # Check for specific missing docstrings
        element_types = [element_type for element_type, _, _ in missing_docstrings]
        names = [name for _, name, _ in missing_docstrings]

        self.assertIn("class", element_types)
        self.assertIn("function", element_types)
        self.assertIn("async function", element_types)

        self.assertIn("ClassWithoutDocstring", names)
        self.assertIn("method_without_docstring", names)
        self.assertIn("function_without_docstring", names)
        self.assertIn("async_function_without_docstring", names)

        # Check that we found the module docstring
        self.assertTrue(visitor.has_module_docstring)

        # Create a visitor that doesn't skip private methods
        visitor = DocstringVisitor(skip_private=False)
        visitor.visit(tree)

        # Check that private methods are now included
        missing_docstrings = visitor.missing_docstrings
        self.assertEqual(len(missing_docstrings), 5)  # One more for the private method

        # Check for the private method
        names = [name for _, name, _ in missing_docstrings]
        self.assertIn("_private_method", names)


if __name__ == "__main__":
    unittest.main()
