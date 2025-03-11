# API Reference

This document provides detailed information about the Jararaca code quality API for developers who want to integrate it into their own tools.

## Main Classes

### `CodeQualityPipeline`

The main class that runs all the quality checks.

```python
from code_quality.pipeline import CodeQualityPipeline

# Initialize the pipeline
pipeline = CodeQualityPipeline(
    project_path="/path/to/project",
    config_file="/path/to/config.ini"  # Optional
)

# Run all checks
all_passed = pipeline.run_all_checks()

# Process branch if checks passed (optional)
if all_passed:
    pipeline.process_branch_and_commit()
```

#### Methods

##### `__init__(project_path, config_file=None)`

Initializes the pipeline with the project path and optional configuration file.

Parameters:
- `project_path`: Path to the Python project to check
- `config_file`: Optional path to configuration file

##### `load_config(config_file)`

Loads configuration from a file or uses defaults.

Parameters:
- `config_file`: Path to configuration file

##### `run_all_checks()`

Runs all quality checks on the project.

Returns:
- `bool`: True if all non-skipped checks passed, False otherwise

##### `process_branch_and_commit()`

Processes branch management and commits if all checks passed and auto-commit is enabled.

Returns:
- `bool`: True if processing was successful, False otherwise

### `CheckResult`

A data class representing the result of a single check.

```python
from code_quality.pipeline import CheckResult, CheckStatus

result = CheckResult(
    name="Code Formatting",
    status=CheckStatus.PASSED,
    details="All files are properly formatted."
)
```

#### Attributes

- `name`: Name of the check
- `status`: Status of the check (PASSED, FAILED, or SKIPPED)
- `details`: Additional details about the check result

### `CheckStatus`

An enumeration of possible check statuses.

```python
from code_quality.pipeline import CheckStatus

status = CheckStatus.PASSED
```

Values:
- `PASSED`: Check passed successfully
- `FAILED`: Check failed
- `SKIPPED`: Check was skipped

## Utility Functions

### `run_command(command, cwd)`

Runs a shell command in the specified directory.

```python
from code_quality.utils import run_command

result = run_command(["ls", "-la"], "/path/to/directory")
```

Parameters:
- `command`: Command to run as a list of strings
- `cwd`: Directory to run the command in

Returns:
- `CompletedProcess`: Subprocess result with stdout and stderr

### `format_result_output(name, status, details="")`

Formats a check result for terminal output with colors.

```python
from code_quality.utils import format_result_output

output = format_result_output(
    name="Code Formatting",
    status="PASSED",
    details="All files are properly formatted."
)
print(output)
```

Parameters:
- `name`: Name of the check
- `status`: Status string (PASSED, FAILED, or SKIPPED)
- `details`: Optional details about the result

Returns:
- `str`: Formatted string for terminal output

## Command-line Interface

The package provides a command-line interface that can be used directly.

```
code-quality /path/to/project [--config CONFIG] [--auto-commit]
```

Arguments:
- `project_path`: Path to the Python project
- `--config`: Path to configuration file
- `--auto-commit`: Enable automatic commit and branch processing 