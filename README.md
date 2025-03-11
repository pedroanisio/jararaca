# Jararaca - Python Code Quality Pipeline

A comprehensive Python code quality validation tool that ensures code follows established development standards and guidelines. The tool validates code structure, style, quality, and testing before optionally automating branch management and commits.

## Features

- **Formatting checks** with [Black](https://github.com/psf/black)
- **Import ordering** with [isort](https://github.com/PyCQA/isort)
- **Linting** with [Flake8](https://github.com/PyCQA/flake8) and optionally [Ruff](https://github.com/charliermarsh/ruff)
- **Static type checking** with [mypy](https://github.com/python/mypy)
- **Security scanning** with [Bandit](https://github.com/PyCQA/bandit)
- **Test execution and coverage validation**
- **Naming convention verification**
- **File and function length checks**
- **Docstring validation**
- **Dependency security checks** with [pip-audit](https://github.com/pypa/pip-audit)
- **Optional Git branch and commit management**

## Installation

### From PyPI (recommended)

```bash
pip install jararaca
```

### From Source

```bash
git clone https://github.com/jararaca/jararaca.git
cd jararaca
pip install -e .
```

## Usage

### Basic Usage

```bash
code-quality /path/to/your/python/project
```

### With Configuration File

```bash
code-quality /path/to/your/python/project --config /path/to/config.ini
```

### With Automatic Commits

```bash
code-quality /path/to/your/python/project --auto-commit
```

## Configuration

Create a configuration file to customize the behavior of the pipeline:

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

## JSON Output

You can save the quality check results as JSON for programmatic consumption by using the `--json-output` option:

```bash
code-quality . --json-output results.json
```

The JSON file will contain a comprehensive report including metadata, summary of check results, and structured detailed information for each check:

```json
{
  "metadata": {
    "timestamp": "2025-03-11T10:23:01.123456",
    "project_path": "/path/to/project",
    "configuration": {
      "src_dirs": "src",
      "test_dir": "tests",
      "min_test_coverage": "80"
      // Additional configuration values...
    },
    "version": "1.0"
  },
  "summary": {
    "passed": 2,
    "failed": 10,
    "skipped": 0,
    "total": 12,
    "status": "FAILED"
  },
  "checks": [
    {
      "name": "Code Formatting (Black)",
      "status": "FAILED",
      "raw_details": "Files need formatting:\n...",
      "details": {
        "summary": "Files need formatting",
        "issues": [],
        "files": ["src/file1.py", "src/file2.py"]
      }
    },
    {
      "name": "Import Sorting (isort)",
      "status": "PASSED",
      "raw_details": "All imports are properly sorted.",
      "details": {
        "summary": "All imports are properly sorted.",
        "issues": []
      }
    },
    {
      "name": "Type Checking (mypy)",
      "status": "FAILED",
      "raw_details": "Type checking issues found:\n...",
      "details": {
        "summary": "Type checking issues found:",
        "issues": [
          "src/file.py:10: error: Function is missing a return type annotation",
          "src/file.py:20: error: Unexpected keyword argument"
        ]
      }
    },
    {
      "name": "Test Coverage",
      "status": "FAILED",
      "raw_details": "Test coverage is 59%, which is below the minimum requirement of 80%.",
      "details": {
        "summary": "Test coverage is 59%, which is below the minimum requirement of 80%.",
        "issues": [],
        "coverage_percentage": 59.0
      }
    }
    // Additional checks...
  ]
}
```

Features of the JSON output:

1. **Metadata**: Includes timestamp, project path, and configuration used
2. **Summary**: Overall counts and status
3. **Detailed check results**:
   - Both raw details (as displayed in the console) and structured information
   - Check-specific parsed data (like files, issues, coverage percentages)
   - Specific error messages and locations

This structured JSON output can be used to integrate the quality checks with CI/CD pipelines, dashboards, or other automated systems.

## Development

```bash
pytest
```

### Building Documentation

```bash
cd docs
make html
```

## License

MIT License - see LICENSE file for details. 