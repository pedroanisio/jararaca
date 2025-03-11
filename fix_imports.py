#!/usr/bin/env python3
"""
Script to fix import statements in test files.
This script will replace 'from src.code_quality' with 'from code_quality'
and 'import src.code_quality' with 'import code_quality' in all Python
files under the tests directory.
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix import statements in a single file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace import patterns
    modified_content = re.sub(r'from src\.code_quality', 'from code_quality', content)
    modified_content = re.sub(r'import src\.code_quality', 'import code_quality', modified_content)
    
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        return True
    return False

def fix_imports(directory):
    """Recursively fix imports in all Python files in a directory."""
    fixed_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_files.append(file_path)
    return fixed_files

if __name__ == "__main__":
    tests_dir = "tests"
    fixed_files = fix_imports(tests_dir)
    
    print(f"Fixed imports in {len(fixed_files)} files:")
    for file in fixed_files:
        print(f"  - {file}") 