.PHONY: clean clean-build clean-cache jararaca setup init

# Run all tests (excluding the samples directory)
test:
	clear; pytest

# Run tests with coverage and generate an HTML report
coverage-html:
	clear; pytest --cov=src/jararaca --cov-report=html

# Run tests with coverage (terminal report)
coverage:
	clear; pytest --cov=src/jararaca --cov-report=term-missing

# Main clean target aggregates all cleaning tasks
clean: clean-build clean-cache
	@rm -f .coverage

# Remove build artifacts and generated directories
clean-build:
	@rm -rf htmlcov .pytest_cache dist build *.egg-info

# Remove Python cache files (recursively)
clean-cache:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete

# Run Jararaca: format code and then run the Jararaca tool
jararaca:
	black .
	isort .
	clear
	python -m jararaca .

# Install dependencies from requirements.txt
setup: requirements.txt
	pip install -r requirements.txt

# Create a virtual environment (note: activation must be done manually)
init:
	python3 -m venv venv
	@echo "Virtual environment created. Activate it by running: source venv/bin/activate"

# Build the package (requires the 'build' package: pip install build)
build: clean
	python -m build
