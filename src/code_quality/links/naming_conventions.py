"""
Check link for Python naming conventions.

This module contains the NamingConventionsCheck class which verifies that Python code
follows PEP 8 naming conventions.
"""

import os
import re
from typing import Any, Dict, List

from ..chain import CheckLink
from ..utils import CheckResult, CheckStatus


class NamingConventionsCheck(CheckLink):
    """
    Check link for Python naming conventions according to PEP 8.
    """

    def __init__(self) -> None:
        """Initialize a naming conventions check link."""
        super().__init__("Naming Conventions")

        # Regex patterns for different naming conventions
        self.module_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.class_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
        self.function_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.variable_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        self.constant_pattern = re.compile(r"^[A-Z][A-Z0-9_]*$")

        # Regex for docstrings and comments to be excluded from searches
        self.docstring_triple_quote = re.compile(r'""".*?"""', re.DOTALL)
        self.docstring_single_quote = re.compile(r"'''.*?'''", re.DOTALL)
        self.comment_pattern = re.compile(r"#.*$", re.MULTILINE)
        
        # Define patterns for recognized exceptions
        self.ast_visitor_pattern = re.compile(r"^visit_[A-Z][a-zA-Z0-9]*$")
        self.dunder_pattern = re.compile(r"^__[a-z][a-z0-9_]*__$")
        
        # Common words used in docstrings that might cause false positives
        self.common_words = [
            "for", "which", "from", "class", "definition", "orchestrates", 
            "contents", "names", "function", "methods", "module", "documentation"
        ]

    def _strip_comments_and_docstrings(self, content: str) -> str:
        """
        Remove comments and docstrings from the content.
        
        Args:
            content: The content to process
            
        Returns:
            The content with comments and docstrings removed
        """
        # First remove triple-quoted docstrings
        content = self.docstring_triple_quote.sub("", content)
        # Then remove single-quoted docstrings
        content = self.docstring_single_quote.sub("", content)
        # Finally remove comments
        content = self.comment_pattern.sub("", content)
        return content

    def _check_module_name(self, module_name: str, file_path: str) -> List[str]:
        """
        Check if a module name follows the snake_case convention.

        Args:
            module_name: The name of the module to check.
            file_path: The path to the file being checked.

        Returns:
            A list of naming convention issues found.
        """
        issues = []
        
        # Skip special module names like __init__, __main__
        if module_name.startswith("__") and module_name.endswith("__"):
            return issues
            
        if not self.module_pattern.match(module_name):
            issues.append(
                f"Module name '{module_name}' in {file_path} does not follow snake_case convention"
            )
        return issues

    def _check_class_names(self, content: str, file_path: str) -> List[str]:
        """
        Check class names in a file for PascalCase convention.

        Args:
            content: The content of the file to check.
            file_path: The path to the file being checked.

        Returns:
            A list of naming convention issues found.
        """
        issues = []
        
        # Remove docstrings and comments to avoid false positives
        cleaned_content = self._strip_comments_and_docstrings(content)
        
        # Use a more specific pattern that matches 'class name:' or 'class name('
        class_pattern = re.compile(r"class\s+([A-Za-z0-9_]+)[\s\(:]")
        for match in class_pattern.finditer(cleaned_content):
            class_name = match.group(1)
            # Skip common words that might appear in docstrings
            if class_name.lower() in self.common_words:
                continue
                
            if not self.class_pattern.match(class_name):
                issues.append(
                    f"Class name '{class_name}' in {file_path} does not follow PascalCase convention"
                )
        return issues

    def _check_function_names(self, content: str, file_path: str) -> List[str]:
        """
        Check function names in a file for snake_case convention.

        Args:
            content: The content of the file to check.
            file_path: The path to the file being checked.

        Returns:
            A list of naming convention issues found.
        """
        issues = []
        
        # Remove docstrings and comments to avoid false positives
        cleaned_content = self._strip_comments_and_docstrings(content)
        
        # Use a more specific pattern that matches 'def name(' or 'def name:'
        function_pattern = re.compile(r"def\s+([A-Za-z0-9_]+)[\s\(:]")
        for match in function_pattern.finditer(cleaned_content):
            function_name = match.group(1)
            
            # Skip special methods and recognized naming patterns
            if self.dunder_pattern.match(function_name):
                continue
            if self.ast_visitor_pattern.match(function_name):
                continue
            if function_name.startswith("_"):
                # For private methods, check if rest follows snake_case
                if self.function_pattern.match(function_name[1:]):
                    continue
            
            # Skip common words that might appear in docstrings
            if function_name.lower() in self.common_words:
                continue
                    
            if not self.function_pattern.match(function_name):
                issues.append(
                    f"Function name '{function_name}' in {file_path} does not follow snake_case convention"
                )
        return issues

    def _check_variable_names(self, content: str, file_path: str) -> List[str]:
        """
        Check variable names in a file for snake_case convention.

        Args:
            content: The content of the file to check.
            file_path: The path to the file being checked.

        Returns:
            A list of naming convention issues found.
        """
        issues = []
        
        # Remove docstrings and comments to avoid false positives
        cleaned_content = self._strip_comments_and_docstrings(content)
        
        # Find variable assignments
        # This is simplified and may not catch all variable names
        variable_pattern = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*=")
        for match in variable_pattern.finditer(cleaned_content):
            variable_name = match.group(1)
            
            # Skip Python keywords and common pattern variables
            if variable_name in [
                "self", "cls", "True", "False", "None", 
                "import", "from", "as", "class", "def", "for", "if", "return", "yield"
            ] or variable_name.lower() in self.common_words:
                continue

            # Check if it's a constant (all uppercase)
            if variable_name.isupper():
                if not self.constant_pattern.match(variable_name):
                    issues.append(
                        f"Constant '{variable_name}' in {file_path} does not follow UPPER_CASE convention"
                    )
            # Skip dunder and private variables
            elif variable_name.startswith("__") or variable_name.startswith("_"):
                continue
            # Otherwise it should be a regular variable
            elif not self.variable_pattern.match(variable_name):
                issues.append(
                    f"Variable '{variable_name}' in {file_path} does not follow snake_case convention"
                )
        return issues

    def _check_file_content(self, content: str, file_path: str) -> List[str]:
        """
        Check the content of a file for naming convention issues.

        Args:
            content: The content of the file to check
            file_path: The path to the file being checked

        Returns:
            A list of naming convention issues found in the file
        """
        issues = []

        # Check class names
        issues.extend(self._check_class_names(content, file_path))

        # Check function names
        issues.extend(self._check_function_names(content, file_path))

        # Check variable names
        issues.extend(self._check_variable_names(content, file_path))

        return issues

    def _process_python_file(self, file_path: str) -> List[str]:
        """
        Process a Python file and check for naming convention issues.

        Args:
            file_path: The path to the file to check.

        Returns:
            A list of naming convention issues found in the file.
        """
        issues = []

        # Check module name (file name)
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        issues.extend(self._check_module_name(module_name, file_path))

        # Check file content for class, function, and variable names
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                file_issues = self._check_file_content(content, file_path)
                issues.extend(file_issues)
        except Exception as e:
            issues.append(f"Error reading {file_path}: {str(e)}")

        return issues

    def _execute_check(self, context: Dict[str, Any]) -> List[CheckResult]:
        """
        Check naming conventions in Python files.

        Args:
            context: A dictionary containing context for the check.
                - project_path: The path to the project to check.
                - source_dirs: List of source directories to check.

        Returns:
            A list containing the result of the naming conventions check.
        """
        project_path = context.get("project_path", ".")
        source_dirs = context.get("source_dirs", ["src"])

        issues = []

        # Check each source directory
        for source_dir in source_dirs:
            dir_path = os.path.join(project_path, source_dir)
            if not os.path.exists(dir_path):
                continue

            # Walk through the directory
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue

                    file_path = os.path.join(root, file)
                    issues.extend(self._process_python_file(file_path))

        # Determine the status based on issues found
        if issues:
            status = CheckStatus.FAILED
            details = "Naming convention issues found:\n" + "\n".join(issues)
        else:
            status = CheckStatus.PASSED
            details = "All code follows naming conventions."

        return [CheckResult(self.name, status, details)]
