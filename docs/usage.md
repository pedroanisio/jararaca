# Usage Guide

Jararaca is a comprehensive tool for validating Python code quality. This guide provides detailed information on how to use the tool effectively.

## Basic Usage

```bash
code-quality /path/to/your/python/project
```

This will run all the quality checks on your project using the default configuration.

## Configuration

### Command Line Options

```bash
code-quality /path/to/your/project --config /path/to/config.ini --auto-commit
```

Options:
- `--config`: Path to a custom configuration file
- `--auto-commit`: Enable automatic commit and branch processing

### Configuration File

Create a configuration file (INI format) to customize the behavior of the pipeline:

```ini
[general]
min_test_coverage = 80
max_file_length = 300
max_function_length = 50
check_bandit = true
check_mypy = true
check_ruff = true
main_branch = main
enable_auto_commit = false

[paths]
src_dirs = src,app
test_dir = tests
exclude_dirs = venv,.venv,__pycache__,build,dist
```

#### Configuration Options

General section:
- `min_test_coverage`: Minimum required test coverage percentage
- `max_file_length`: Maximum allowed file length in lines
- `max_function_length`: Maximum allowed function length in lines
- `check_bandit`: Whether to run security checks with Bandit
- `check_mypy`: Whether to run static type checking with mypy
- `check_ruff`: Whether to run additional linting with Ruff
- `main_branch`: Name of the main branch for Git operations
- `enable_auto_commit`: Whether to enable automatic commit processing

Paths section:
- `src_dirs`: Comma-separated list of source directories
- `test_dir`: Directory containing tests
- `exclude_dirs`: Directories to exclude from checks

## Quality Checks

Jararaca runs the following checks:

1. **Code Formatting** - Ensures code follows the Black code style
2. **Import Ordering** - Verifies imports are properly organized with isort
3. **Linting** - Checks code for errors and style issues with Flake8 and Ruff
4. **Static Type Checking** - Validates type annotations with mypy
5. **Security Scanning** - Looks for security vulnerabilities with Bandit
6. **Unit Tests** - Runs tests and verifies they pass
7. **Test Coverage** - Ensures adequate test coverage of the codebase
8. **Naming Conventions** - Checks that files, classes, and functions follow naming conventions
9. **File Lengths** - Ensures files don't exceed the maximum allowed length
10. **Function Lengths** - Ensures functions don't exceed the maximum allowed length
11. **Docstrings** - Verifies that classes and functions have proper docstrings
12. **Dependency Security** - Checks for known vulnerabilities in dependencies

## Git Integration

If `enable_auto_commit` is set to `true` or `--auto-commit` is passed as a command-line argument, Jararaca will perform Git operations when all quality checks pass:

1. Commit any uncommitted changes
2. Checkout the main branch
3. Merge the current branch into the main branch
4. Delete the current branch

This feature is useful for automating branch management in CI/CD pipelines. 