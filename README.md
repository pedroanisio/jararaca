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

The JSON file will contain a summary of the check results and detailed information for each check, in the following format:

```json
{
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
      "details": "Files need formatting:\n..."
    },
    {
      "name": "Import Sorting (isort)",
      "status": "PASSED",
      "details": "All imports are properly sorted."
    },
    // ... other checks
  ]
}
```

This JSON output can be used to integrate the quality checks with CI/CD pipelines, dashboards, or other automated systems.

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