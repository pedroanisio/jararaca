"""
Dependency Check implementation for Python projects.

This module provides a check that verifies dependencies are up-to-date in requirements.txt.
"""

import os
import json
import subprocess
from typing import Any, Dict, List, Set, Tuple

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus, run_command


class DependencyCheck(CheckLink):
    """
    Check that dependencies in requirements.txt are up-to-date.
    
    This helps maintain security and performance by encouraging the use of
    up-to-date libraries that include bug fixes and security patches.
    """

    def __init__(self):
        """Initialize the dependency check."""
        super().__init__("Dependency Check")
        self.description = "Checks that dependencies are up-to-date"

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
        requirements_files = []
        for root, _, files in os.walk(project_path):
            for file in files:
                if file == "requirements.txt" or file.endswith("-requirements.txt"):
                    requirements_files.append(os.path.join(root, file))
        
        if not requirements_files:
            return [CheckResult(
                self.name,
                CheckStatus.SKIPPED,
                "No requirements.txt files found."
            )]
        
        # Get the list of installed packages
        command = ["pip", "list", "--outdated", "--format=json"]
        result = run_command(command)
        
        if result.returncode != 0:
            return [CheckResult(
                self.name,
                CheckStatus.FAILED,
                f"Failed to check for outdated packages:\n{result.stderr}"
            )]
        
        try:
            outdated_packages = json.loads(result.stdout)
        except json.JSONDecodeError:
            return [CheckResult(
                self.name,
                CheckStatus.FAILED,
                f"Failed to parse pip output:\n{result.stdout}"
            )]
        
        # Create a dictionary of outdated packages
        outdated_dict = {pkg["name"].lower(): pkg for pkg in outdated_packages}
        
        # Check each requirements file for outdated packages
        outdated_dependencies = []
        
        for req_file in requirements_files:
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        # Parse the package name from the line
                        # Handle different formats like package==1.0.0, package>=1.0.0, etc.
                        parts = line.split('=')[0].split('>')[0].split('<')[0].strip()
                        package_name = parts.lower()
                        
                        if package_name in outdated_dict:
                            pkg_info = outdated_dict[package_name]
                            outdated_dependencies.append((
                                req_file,
                                pkg_info["name"],
                                pkg_info["version"],
                                pkg_info["latest_version"]
                            ))
            except Exception as e:
                outdated_dependencies.append((req_file, f"Error: {str(e)}", "", ""))
        
        # Determine the status based on outdated dependencies found
        if outdated_dependencies:
            status = CheckStatus.FAILED
            details = "Outdated dependencies found:\n"
            for req_file, pkg_name, current_version, latest_version in outdated_dependencies:
                if current_version and latest_version:
                    details += f"- {req_file}: {pkg_name} (current: {current_version}, latest: {latest_version})\n"
                else:
                    details += f"- {req_file}: {pkg_name}\n"
        else:
            status = CheckStatus.PASSED
            details = "All dependencies are up-to-date."
            
        return [CheckResult(self.name, status, details)] 