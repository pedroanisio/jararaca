"""
Tests for the file length check link.
"""

import os
import tempfile
import unittest
from unittest.mock import mock_open as mock_builtin_open
from unittest.mock import patch

from src.code_quality.links.file_length import FileLengthCheck
from src.code_quality.utils import CheckStatus


class TestFileLengthCheck(unittest.TestCase):
    """Test cases for the FileLengthCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = FileLengthCheck(max_lines=300)  # Match default in original tests

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_check_file_length_no_violations(self):
        """Test the file length check when all files are under the limit."""
        # Create a source directory with files under the limit
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a few short files
        with open(os.path.join(src_dir, "short_file1.py"), "w") as f:
            f.write("# Short file\n" * 10)  # 10 lines

        with open(os.path.join(src_dir, "short_file2.py"), "w") as f:
            f.write("# Another short file\n" * 20)  # 20 lines

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "File Length")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn("All files are under the maximum length", results[0].details)
        self.assertIn("300 lines", results[0].details)

    def test_check_file_length_with_violations(self):
        """Test the file length check when files exceed the limit."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a short file
        with open(os.path.join(src_dir, "short_file.py"), "w") as f:
            f.write("# Short file\n" * 10)  # 10 lines

        # Create a long file
        with open(os.path.join(src_dir, "long_file.py"), "w") as f:
            f.write("# Long file\n" * 500)  # 500 lines, exceeding default max of 300

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "File Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("long_file.py", results[0].details)
        self.assertIn("500 lines", results[0].details)

    def test_check_file_length_with_multiple_violations(self):
        """Test the file length check when multiple files exceed the limit."""
        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create multiple long files
        with open(os.path.join(src_dir, "long_file1.py"), "w") as f:
            f.write("# Long file 1\n" * 400)  # 400 lines

        with open(os.path.join(src_dir, "long_file2.py"), "w") as f:
            f.write("# Long file 2\n" * 350)  # 350 lines

        with open(os.path.join(src_dir, "short_file.py"), "w") as f:
            f.write("# Short file\n" * 10)  # 10 lines

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "File Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("long_file1.py", results[0].details)
        self.assertIn("400 lines", results[0].details)
        self.assertIn("long_file2.py", results[0].details)
        self.assertIn("350 lines", results[0].details)

    def test_check_file_length_custom_max_lines(self):
        """Test the file length check with a custom maximum line limit."""
        # Create a check with custom max lines
        custom_check = FileLengthCheck(max_lines=50)

        # Create a source directory
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Create a medium length file
        with open(os.path.join(src_dir, "medium_file.py"), "w") as f:
            f.write("# Medium file\n" * 75)  # 75 lines, exceeding custom max of 50

        context = {"project_path": self.project_path, "source_dirs": ["src"]}

        # Execute the check
        results = custom_check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "File Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("medium_file.py", results[0].details)
        self.assertIn("75 lines", results[0].details)
        self.assertIn("50 lines", results[0].details)  # Custom limit mentioned

    def test_check_file_length_with_error(self):
        """Test the file length check when there's an error reading a file."""
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
            m = mock_builtin_open()
            m.side_effect = Exception("Permission denied")

            with patch("builtins.open", m):
                context = {"project_path": self.project_path, "source_dirs": ["src"]}

                # Execute the check
                results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "File Length")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Error", results[0].details)


if __name__ == "__main__":
    unittest.main()
