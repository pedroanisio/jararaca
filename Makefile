# Jararaca Project Makefile
# ------------------------

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
COVERAGE_PATH := src/jararaca
VENV_DIR := venv
DIST_DIR := dist

# Package repository information
REPO_NAME := arc4d3-pypi
LOCATION := us-west1
PROJECT_ID := $(shell gcloud config get-value project)
PYTHON_REPO_URL := https://$(LOCATION)-python.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)

# Consolidated PHONY declaration
.PHONY: test coverage-html coverage clean clean-build clean-cache jararaca setup init create_repo build upload publish gen_pypirc

# Default target
.DEFAULT_GOAL := test

#######################
### Testing Targets ###
#######################

# Run all tests (excluding the samples directory)
test:
	@echo "Running tests..."
	@clear
	$(PYTEST)

# Run tests with coverage and generate an HTML report
coverage-html:
	@echo "Generating HTML coverage report..."
	@clear
	$(PYTEST) --cov=$(COVERAGE_PATH) --cov-report=html

# Run tests with coverage (terminal report)
coverage:
	@echo "Running coverage tests..."
	@clear
	$(PYTEST) --cov=$(COVERAGE_PATH) --cov-report=term-missing

########################
### Cleaning Targets ###
########################

# Main clean target aggregates all cleaning tasks
clean: clean-build clean-cache
	@echo "Performing full cleanup..."
	@rm -f .coverage

# Remove build artifacts and generated directories
clean-build:
	@echo "Cleaning build artifacts..."
	@rm -rf htmlcov .pytest_cache $(DIST_DIR) build *.egg-info

# Remove Python cache files (recursively)
clean-cache:
	@echo "Cleaning Python cache files..."
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete

################################
### Code Quality & Execution ###
################################

# Format code and then run the Jararaca tool
jararaca:
	@echo "Formatting code and running jararaca..."
	black .
	isort .
	@clear
	$(PYTHON) -m jararaca .

###########################
### Environment Setup ###
###########################

# Install dependencies from requirements.txt
setup: requirements.txt
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt

# Create a virtual environment
init:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created. Activate it by running: source $(VENV_DIR)/bin/activate"

######################################
### Package Build and Deployment ###
######################################

# Build the package using the modern build tool
build: clean
	@echo "Building package..."
	$(PYTHON) -m build

# Upload package using twine
upload: build
	@echo "Uploading package to $(PYTHON_REPO_URL)..."
	twine upload --repository-url $(PYTHON_REPO_URL) $(DIST_DIR)/*

# Build and then upload the package
publish: upload

# Generate .pypirc file with authentication token
gen_pypirc:
	@echo "Generating .pypirc file..."
	@echo "[distutils]" > .pypirc
	@echo "index-servers =" >> .pypirc
	@echo "    gcp" >> .pypirc
	@echo "" >> .pypirc
	@echo "[gcp]" >> .pypirc
	@echo "repository: https://$(LOCATION)-python.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)" >> .pypirc
	@echo "username: oauth2accesstoken" >> .pypirc
	@echo "password: $$(gcloud auth print-access-token)" >> .pypirc
	@echo ".pypirc file created."