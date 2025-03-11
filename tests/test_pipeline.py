"""
Tests for the code quality pipeline module.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.pipeline import CheckResult, CheckStatus, CodeQualityPipeline


class TestCodeQualityPipeline(unittest.TestCase):
    """Test cases for the CodeQualityPipeline class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name

    def tearDown(self):
        """Clean up test environment after each test."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test pipeline initialization with default config."""
        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)

            # Verify default configuration is loaded
            self.assertEqual(pipeline.config["general"]["min_test_coverage"], "80")
            self.assertEqual(pipeline.config["paths"]["test_dir"], "tests")

    def test_load_config_from_file(self):
        """Test loading configuration from a file."""
        # Create a test config file
        config_path = os.path.join(self.project_path, "test_config.ini")
        with open(config_path, "w") as f:
            f.write(
                """
[general]
min_test_coverage = 90
max_file_length = 200

[paths]
test_dir = custom_tests
"""
            )

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path, config_path)

            # Verify custom configuration values
            self.assertEqual(pipeline.config["general"]["min_test_coverage"], "90")
            self.assertEqual(pipeline.config["general"]["max_file_length"], "200")
            self.assertEqual(pipeline.config["paths"]["test_dir"], "custom_tests")

    @patch("code_quality.pipeline.run_command")
    def test_check_formatting(self, mock_run_command):
        """Test the formatting check functionality."""
        # Setup the mock to return a passing check
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="All files are properly formatted."
        )

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            pipeline._check_formatting()

            # Check that the result was added correctly
            self.assertEqual(len(pipeline.results), 1)
            self.assertEqual(pipeline.results[0].name, "Code Formatting (Black)")
            self.assertEqual(pipeline.results[0].status, CheckStatus.PASSED)

    @patch("code_quality.pipeline.run_command")
    def test_check_formatting_failure(self, mock_run_command):
        """Test handling of formatting check failure."""
        # Setup the mock to return a failing check
        mock_run_command.return_value = MagicMock(
            returncode=1, stderr="would reformat file.py"
        )

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            pipeline._check_formatting()

            # Check that the result was added correctly as a failure
            self.assertEqual(len(pipeline.results), 1)
            self.assertEqual(pipeline.results[0].name, "Code Formatting (Black)")
            self.assertEqual(pipeline.results[0].status, CheckStatus.FAILED)
            self.assertIn("would reformat", pipeline.results[0].details)

    def test_get_python_files(self):
        """Test the _get_python_files method."""
        # Create a source directory structure with Python files
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(os.path.join(src_dir, "module1"))
        os.makedirs(os.path.join(src_dir, "module2"))

        # Create some Python files
        with open(os.path.join(src_dir, "module1", "file1.py"), "w") as f:
            f.write("# Test file 1")
        with open(os.path.join(src_dir, "module2", "file2.py"), "w") as f:
            f.write("# Test file 2")
        with open(os.path.join(src_dir, "module2", "file3.txt"), "w") as f:
            f.write("# Not a Python file")

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            python_files = pipeline._get_python_files()

            # Check that only Python files were found
            self.assertEqual(len(python_files), 2)
            self.assertTrue(any(f.endswith("file1.py") for f in python_files))
            self.assertTrue(any(f.endswith("file2.py") for f in python_files))
            self.assertFalse(any(f.endswith("file3.txt") for f in python_files))

    def test_check_naming_conventions(self):
        """Test the _check_naming_conventions method."""
        # Create a source directory with files that follow and violate naming conventions
        src_dir = os.path.join(self.project_path, "src")
        os.makedirs(src_dir)

        # Good file with proper naming
        with open(os.path.join(src_dir, "good_file.py"), "w") as f:
            f.write(
                """
class GoodClass:
    \"\"\"A properly named class.\"\"\"
    
    def good_method(self):
        \"\"\"A properly named method.\"\"\"
        pass
"""
            )

        # Bad file with improper naming
        with open(os.path.join(src_dir, "BadFile.py"), "w") as f:
            f.write(
                """
class bad_class:
    \"\"\"An improperly named class.\"\"\"
    
    def BadMethod(self):
        \"\"\"An improperly named method.\"\"\"
        pass
"""
            )

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            pipeline._check_naming_conventions()

            # Check that naming convention violations were detected
            self.assertEqual(len(pipeline.results), 1)
            self.assertEqual(pipeline.results[0].name, "Naming Conventions")
            self.assertEqual(pipeline.results[0].status, CheckStatus.FAILED)

            # Check for specific violations in the details
            details = pipeline.results[0].details
            self.assertIn("BadFile.py", details)  # File name should be snake_case
            self.assertIn("bad_class", details)  # Class name should be PascalCase
            self.assertIn("BadMethod", details)  # Method name should be snake_case

    @patch("code_quality.pipeline.run_command")
    def test_check_dependencies(self, mock_run_command):
        """Test the _check_dependencies method."""
        # Create a requirements.txt file
        req_path = os.path.join(self.project_path, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("pytest==7.0.0\nflask==2.0.0\n")

        # Mock the pip-audit command to return secure dependencies
        mock_run_command.return_value = MagicMock(
            returncode=0, stdout="No known vulnerabilities found"
        )

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            pipeline._check_dependencies()

            # Check that dependency check passed
            self.assertEqual(
                len(pipeline.results), 2
            )  # Two results: management and security
            self.assertEqual(pipeline.results[0].name, "Dependency Management")
            self.assertEqual(pipeline.results[0].status, CheckStatus.PASSED)
            self.assertEqual(pipeline.results[1].name, "Dependency Security")
            self.assertEqual(pipeline.results[1].status, CheckStatus.PASSED)

    @patch("code_quality.pipeline.run_command")
    def test_check_dependencies_with_vulnerability(self, mock_run_command):
        """Test the _check_dependencies method with vulnerable dependencies."""
        # Create a requirements.txt file
        req_path = os.path.join(self.project_path, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("pytest==7.0.0\nflask==2.0.0\n")

        # Configure the mock to simulate different return values based on which command is being run
        def side_effect(command, *args, **kwargs):
            if command[0] == "pip-audit":
                return MagicMock(
                    returncode=1, stdout="Found vulnerability in flask==2.0.0"
                )
            return MagicMock(returncode=0, stdout="")

        mock_run_command.side_effect = side_effect

        with patch("code_quality.pipeline.subprocess.run") as mock_run:
            # Mock the tool check to avoid actual command execution
            mock_run.return_value.returncode = 0

            pipeline = CodeQualityPipeline(self.project_path)
            pipeline._check_dependencies()

            # Check that dependency security check failed
            self.assertEqual(
                len(pipeline.results), 2
            )  # Two results: management and security
            self.assertEqual(pipeline.results[0].name, "Dependency Management")
            self.assertEqual(pipeline.results[0].status, CheckStatus.PASSED)
            self.assertEqual(pipeline.results[1].name, "Dependency Security")
            self.assertEqual(pipeline.results[1].status, CheckStatus.FAILED)
            self.assertIn("vulnerability", pipeline.results[1].details)


if __name__ == "__main__":
    unittest.main()
