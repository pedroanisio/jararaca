"""
Tests for the dependency check link.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from code_quality.links.dependency import DependencyCheck
from code_quality.utils import CheckStatus, CommandResult


class TestDependencyCheck(unittest.TestCase):
    """Test cases for the DependencyCheck class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_path = self.temp_dir.name
        self.check = DependencyCheck()

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_no_requirements(self, mock_run_command):
        """Test the dependency check when no requirements files are found."""
        # Create an empty project directory
        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.SKIPPED)
        self.assertIn("No requirements.txt files found", results[0].details)

        # Verify that run_command was not called
        mock_run_command.assert_not_called()

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_up_to_date(self, mock_run_command):
        """Test the dependency check when all dependencies are up-to-date."""
        # Create a project directory with a requirements.txt file
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write(
                """
# Project dependencies
pytest==7.0.0
black==22.1.0
flake8==4.0.1
"""
            )

        # Mock the run_command function to return an empty list of outdated packages
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout="[]", stderr=""
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.PASSED)
        self.assertIn("All dependencies are up-to-date", results[0].details)

        # Verify that run_command was called correctly
        mock_run_command.assert_called_once_with(
            ["pip", "list", "--outdated", "--format=json"]
        )

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_outdated(self, mock_run_command):
        """Test the dependency check when some dependencies are outdated."""
        # Create a project directory with a requirements.txt file
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write(
                """
# Project dependencies
pytest==6.2.5
black==21.5b2
flake8==3.9.2
"""
            )

        # Mock the run_command function to return a list of outdated packages
        outdated_packages = [
            {
                "name": "pytest",
                "version": "6.2.5",
                "latest_version": "7.0.0",
                "latest_filetype": "wheel",
            },
            {
                "name": "black",
                "version": "21.5b2",
                "latest_version": "22.1.0",
                "latest_filetype": "wheel",
            },
        ]
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout=json.dumps(outdated_packages), stderr=""
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Outdated dependencies found", results[0].details)
        self.assertIn("pytest (current: 6.2.5, latest: 7.0.0)", results[0].details)
        self.assertIn("black (current: 21.5b2, latest: 22.1.0)", results[0].details)

        # Verify that run_command was called correctly
        mock_run_command.assert_called_once_with(
            ["pip", "list", "--outdated", "--format=json"]
        )

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_different_formats(self, mock_run_command):
        """Test the dependency check with various requirement formats."""
        # Create a project directory with a requirements.txt file using different formats
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write(
                """
# Project dependencies with different formats
pytest==6.2.5  # Exact version
black>=21.5b2  # Greater than or equal
flake8<4.0.0   # Less than
mypy~=0.910    # Compatible release
requests       # No version specified
"""
            )

        # Mock the run_command function to return a list of outdated packages
        outdated_packages = [
            {
                "name": "pytest",
                "version": "6.2.5",
                "latest_version": "7.0.0",
                "latest_filetype": "wheel",
            },
            {
                "name": "black",
                "version": "21.5b2",
                "latest_version": "22.1.0",
                "latest_filetype": "wheel",
            },
            {
                "name": "requests",
                "version": "2.27.1",
                "latest_version": "2.28.0",
                "latest_filetype": "wheel",
            },
        ]
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout=json.dumps(outdated_packages), stderr=""
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Outdated dependencies found", results[0].details)
        self.assertIn("pytest (current: 6.2.5, latest: 7.0.0)", results[0].details)
        self.assertIn("black (current: 21.5b2, latest: 22.1.0)", results[0].details)
        # Note: requests without a version specifier is not checked by the implementation
        # so we don't assert for it

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_multiple_files(self, mock_run_command):
        """Test the dependency check with multiple requirements files."""
        # Create a project directory with multiple requirements files
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write(
                """
# Main requirements
pytest==6.2.5
black==21.5b2
"""
            )

        # Create a subfolder
        subdir = os.path.join(self.project_path, "dev")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "dev-requirements.txt"), "w") as f:
            f.write(
                """
# Development requirements
flake8==3.9.2
mypy==0.910
"""
            )

        # Mock the run_command function to return a list of outdated packages
        outdated_packages = [
            {
                "name": "pytest",
                "version": "6.2.5",
                "latest_version": "7.0.0",
                "latest_filetype": "wheel",
            },
            {
                "name": "mypy",
                "version": "0.910",
                "latest_version": "0.971",
                "latest_filetype": "wheel",
            },
        ]
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout=json.dumps(outdated_packages), stderr=""
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Outdated dependencies found", results[0].details)
        self.assertIn("pytest (current: 6.2.5, latest: 7.0.0)", results[0].details)
        self.assertIn("mypy (current: 0.910, latest: 0.971)", results[0].details)
        self.assertIn("requirements.txt", results[0].details)
        self.assertIn("dev-requirements.txt", results[0].details)

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_command_failure(self, mock_run_command):
        """Test the dependency check when the pip command fails."""
        # Create a project directory with a requirements.txt file
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write("pytest==6.2.5\n")

        # Mock the run_command function to simulate a command failure
        mock_run_command.return_value = CommandResult(
            returncode=1,
            stdout="",
            stderr="Error: Could not determine the latest version for packages",
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Failed to check for outdated packages", results[0].details)
        self.assertIn("Could not determine the latest version", results[0].details)

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_invalid_json(self, mock_run_command):
        """Test the dependency check when pip returns invalid JSON."""
        # Create a project directory with a requirements.txt file
        with open(os.path.join(self.project_path, "requirements.txt"), "w") as f:
            f.write("pytest==6.2.5\n")

        # Mock the run_command function to return invalid JSON
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout="Not a valid JSON output", stderr=""
        )

        context = {"project_path": self.project_path}

        # Execute the check
        results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Failed to parse pip output", results[0].details)
        self.assertIn("Not a valid JSON output", results[0].details)

    @patch("code_quality.links.dependency.run_command")
    def test_check_dependency_file_error(self, mock_run_command):
        """Test the dependency check when there's an error reading a requirements file."""
        # Create a project directory with a requirements.txt file
        requirements_path = os.path.join(self.project_path, "requirements.txt")
        with open(requirements_path, "w") as f:
            f.write("pytest==6.2.5\n")

        # Mock the run_command function to return an empty list of outdated packages
        mock_run_command.return_value = CommandResult(
            returncode=0, stdout="[]", stderr=""
        )

        # Patch open to raise an exception when reading the requirements file
        original_open = open

        def side_effect(*args, **kwargs):
            if args[0] == requirements_path and kwargs.get("encoding") == "utf-8":
                raise Exception("Permission denied")
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=side_effect):
            context = {"project_path": self.project_path}

            # Execute the check
            results = self.check._execute_check(context)

        # Check that the result was created correctly
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Dependency Check")
        self.assertEqual(results[0].status, CheckStatus.FAILED)
        self.assertIn("Outdated dependencies found", results[0].details)
        self.assertIn("requirements.txt", results[0].details)
        self.assertIn("Error: Permission denied", results[0].details)


if __name__ == "__main__":
    unittest.main()
