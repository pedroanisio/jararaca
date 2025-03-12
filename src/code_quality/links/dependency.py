"""
Dependency Check implementation for Python projects.

This module provides a check that verifies dependencies are up-to-date in requirements.txt.
"""

import json
import os
from typing import Any, Dict, List, Tuple

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class DependencyCheck(CheckLink):
    """
    Check that dependencies in requirements.txt are up-to-date.

    This helps maintain security and performance by encouraging the use of
    up-to-date libraries that include bug fixes and security patches.
    """

    def __init__(self) -> None:
        """Initialize the dependency check."""
        super().__init__("Dependency Check")
        self.description = "Checks that dependencies are up-to-date"

    def _find_requirements_files(self, project_path: str) -> List[str]:
        """
        Find all requirements.txt files in the project.

        Args:
            project_path: The path to the project to check.

        Returns:
            A list of paths to requirements.txt files.
        """
        requirements_files = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file == "requirements.txt" or file.endswith("-requirements.txt"):
                    requirements_files.append(os.path.join(root, file))
        return requirements_files

    def _get_outdated_packages(self) -> Dict[str, Dict[str, str]]:
        """
        Get a dictionary of outdated packages from pip.

        Returns:
            A dictionary mapping package names to their information.
        """
        command = ["pip", "list", "--outdated", "--format=json"]
        result = run_command(command)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to check for outdated packages:\n{result.stderr}")

        try:
            outdated_packages = json.loads(result.stdout)
            return {pkg["name"].lower(): pkg for pkg in outdated_packages}
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to parse pip output:\n{result.stdout}")

    def _check_requirements_file(
        self, req_file: str, outdated_dict: Dict[str, Dict[str, str]]
    ) -> List[Tuple[str, str, str, str]]:
        """
        Check a requirements file for outdated packages.

        Args:
            req_file: The path to the requirements file.
            outdated_dict: A dictionary of outdated packages.

        Returns:
            A list of tuples containing (file_path, package_name, current_version, latest_version).
        """
        outdated_dependencies = []
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse the package name from the line
                    parts = line.split("=")[0].split(">")[0].split("<")[0].strip()
                    package_name = parts.lower()

                    if package_name in outdated_dict:
                        pkg_info = outdated_dict[package_name]
                        outdated_dependencies.append(
                            (
                                req_file,
                                pkg_info["name"],
                                pkg_info["version"],
                                pkg_info["latest_version"],
                            )
                        )
        except Exception as e:
            outdated_dependencies.append((req_file, f"Error: {str(e)}", "", ""))
        
        return outdated_dependencies

    def _format_results(
        self, outdated_dependencies: List[Tuple[str, str, str, str]]
    ) -> Tuple[CheckStatus, str]:
        """
        Format the results of the dependency check.

        Args:
            outdated_dependencies: A list of outdated dependencies.

        Returns:
            A tuple containing the check status and details.
        """
        if outdated_dependencies:
            status = CheckStatus.FAILED
            details = "Outdated dependencies found:\n"
            for (
                req_file,
                pkg_name,
                current_version,
                latest_version,
            ) in outdated_dependencies:
                if current_version and latest_version:
                    details += f"- {req_file}: {pkg_name} (current: {current_version}, latest: {latest_version})\n"
                else:
                    details += f"- {req_file}: {pkg_name}\n"
        else:
            status = CheckStatus.PASSED
            details = "All dependencies are up-to-date."
        
        return status, details

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check for outdated dependencies in requirements.txt files.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.

        Returns:
            A list containing the result of the dependency check.
        """
        project_path = context.get("project_path", ".")

        # Find all requirements.txt files
        requirements_files = self._find_requirements_files(project_path)

        if not requirements_files:
            return [
                CheckResult(
                    self.name, CheckStatus.SKIPPED, "No requirements.txt files found."
                )
            ]

        try:
            # Get the list of outdated packages
            outdated_dict = self._get_outdated_packages()
            
            # Check each requirements file for outdated packages
            outdated_dependencies = []
            for req_file in requirements_files:
                outdated_dependencies.extend(
                    self._check_requirements_file(req_file, outdated_dict)
                )
            
            # Format the results
            status, details = self._format_results(outdated_dependencies)
            
        except RuntimeError as e:
            return [CheckResult(self.name, CheckStatus.FAILED, str(e))]

        return [CheckResult(self.name, status, details)]
