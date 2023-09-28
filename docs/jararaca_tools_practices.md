# Jararaca's Tools & Best Practices for Improved Python Coding

## TL;DR

### 1. **Code Formatting and Style:**
   - **Tools:** `mypy` for static typing, `black` for uniform and PEP 8 compliant formatting, `pylint` and `flake8` for linting, and `McCabe` for complexity measurement.

### 2. **Documentation and Comments:**
   - **Tools:** `darglint` for docstring format enforcement, `Sphinx` and `Read the Docs` for automated documentation generation.
   - **Guideline:** Follow Google Style Python Docstrings.

### 3. **Testing and Quality Assurance:**
   - **Tools:** `unittest.mock` for mocking, `Hypothesis` for property-based testing, `pytest` for unit testing, `coverage.py` for code coverage, `bandit` and `pyup.io` for security analysis, and `SonarQube` for continuous inspection.

### 4. **Continuous Integration and Deployment:**
   - **Tools:** `Terraform` for infrastructure, Jenkins or GitHub Actions for CI/CD pipelines, and Docker and Kubernetes for containerization.

### 5. **Version Control and Dependency Management:**
   - **Tools:** `poetry` or `pipenv` for dependency management.
   - **Guideline:** Use Git’s feature-branch workflow and semantic versioning.

### 6. **Performance and Optimization:**
   - **Tools:** `memory_profiler` for memory profiling, `safety` for dependency security, `cProfile` or `line_profiler` for performance profiling.
   - **Guideline:** Explore async capabilities and concurrent.futures.

### 7. **Development Environment and Interactive Prototyping:**
   - **Tools:** `conda` for environment management, Jupyter notebooks, or IPython for interactive computing.

### 8. **Code Management and Import Organization:**
   - **Tools:** `sourcery` for automated refactoring, `pre-commit` for pre-commit management, `ReviewNB` for notebook review, and `isort` for

## 1. Code Formatting and Style

### Type Annotations and Enforcement:

- **Tool:** Leverage `mypy` for static typing to enforce consistency and reduce runtime errors.

- **Reference:** [Mypy Documentation](http://mypy-lang.org/)

### Code Formatter:

- **Tool:** Implement `black` to ensure a uniform and PEP 8 compliant codebase.

- **Reference:** [Black Documentation](https://black.readthedocs.io/en/stable/)

### Linting:

- **Tool:** Integrate `pylint` and `flake8` to catch coding errors and enforce code standards.

- **Reference:** [Pylint Documentation](https://pylint.org/), [Flake8 Documentation](https://flake8.pycqa.org/en/latest/)

### Complexity Measurement:

- **Tool:** Utilize `McCabe` to measure the cyclomatic complexity of the code and identify potential areas that require refactoring.

- **Reference:** [McCabe Documentation](https://pypi.org/project/mccabe/)

## 2. Documentation and Comments

### Docstring Format Enforcement:

- **Tool:** Use `darglint` to ensure that docstrings conform to the style and are complete.

- **Reference:** [Darglint Documentation](https://github.com/terrencepreilly/darglint)

### Automated Documentation Generation:

- **Tool:** Use `Sphinx` coupled with `Read the Docs` to automate documentation generation and hosting.

- **Reference:** [Sphinx Documentation](https://www.sphinx-doc.org/en/master/), [Read the Docs Documentation](https://docs.readthedocs.io/en/stable/index.html)

- **Guideline:** Follow the Google Style Python Docstrings and document all public APIs, classes, and methods.

## 3. Testing and Quality Assurance:

### Mocking and Patching:

- **Tool:** Consider `unittest.mock` for creating mock objects and replacing parts of the system under test with these objects.

- **Reference:** [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Property-based Testing:

- **Tool:** Use `Hypothesis` to conduct property-based tests, automatically generating test cases.

- **Reference:** [Hypothesis Documentation](https://hypothesis.readthedocs.io/en/latest/)

### Unit Testing:

- **Tool:** Adopt `pytest` for a more feature-rich and scalable testing framework.

- **Reference:** [Pytest Documentation](https://docs.pytest.org/en/stable/)

### Code Coverage:

- **Tool:** Incorporate `coverage.py` to analyze the effectiveness of your tests.

- **Reference:** [Coverage.py Documentation](https://coverage.readthedocs.io/en/latest/)

### Security Analysis:

- **Tool:** Integrate `bandit` and `pyup.io` for identifying security vulnerabilities and managing updates.

- **Reference:** [Bandit Documentation](https://bandit.readthedocs.io/en/latest/), [PyUp Documentation](https://pyup.io/)

### Continuous Inspection:

- **Tool:** Utilize `SonarQube` to continually assess code quality and security risks.

- **Reference:** [SonarQube Documentation](https://docs.sonarqube.org/latest/)

## 4. Continuous Integration and Deployment

### Infrastructure as Code:

- **Tool:** Use `Terraform` to provision and manage infrastructure in a declarative and reproducible manner.

- **Reference:** [Terraform Documentation](https://www.terraform.io/docs/index.html)

### CI/CD Pipelines:

- **Tool:** Employ Jenkins or GitHub Actions for robust and customizable automation pipelines.

- **Reference:** [Jenkins Documentation](https://www.jenkins.io/doc/), [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Containerization:

- **Tool:** Use Docker and Kubernetes for scalable and manageable container orchestration.

- **Reference:** [Docker Documentation](https://docs.docker.com/), [Kubernetes Documentation](https://kubernetes.io/docs/)

## **5. Version Control and Dependency Management:

### Version Control:

- **Guideline:** Embrace Git’s feature-branch workflow for collaborative development and use semantic versioning for releases.

### Dependency Management:

- **Tool:** Leverage `poetry` or `pipenv` to simplify dependency management and packaging.

- **Reference:** [Poetry Documentation](https://python-poetry.org/docs/), [Pipenv Documentation](https://pipenv.pypa.io/en/latest/)

## 6. Performance and Optimization

### Memory Profiling:

- **Tool:** Use `memory_profiler` to monitor your Python code's memory consumption in real-time.

- **Reference:** [memory_profiler Documentation](https://pypi.org/project/memory-profiler/)

### Dependency Security:

- **Tool:** Consider using `safety` to check the project dependencies against the Python known vulnerabilities database.

- **Reference:** [Safety Documentation](https://pyup.io/safety/)

### Performance Profiling:

- **Tool:** Employ `cProfile` or `line_profiler` to identify and eliminate performance bottlenecks.

- **Reference:** [cProfile Documentation](https://docs.python.org/3/library/profile.html#module-cProfile), [line_profiler Documentation](https://github.com/pyutils/line_profiler)

### Concurrency and Parallelism:

- **Guideline:** Explore Python’s async capabilities and concurrent.futures for efficient I/O-bound and CPU-bound processing.

- **Reference:** [concurrent.futures Documentation](https://docs.python.org/3/library/concurrent.futures.html), [Async IO Documentation](https://docs.python.org/3/library/asyncio.html)

## 7. Development Environment and Interactive Prototyping

### Environment Management:

- **Tool:** Use `conda` for efficient environment and package management, especially for projects involving data science and machine learning.

- **Reference:** [Conda Documentation](https://docs.conda.io/en/latest/)

### Interactive Computing:

- **Tool:** Leverage Jupyter notebooks or IPython for dynamic development and data analysis.

- **Reference:** [Jupyter Documentation](https://jupyter.org/documentation), [IPython Documentation](https://ipython.readthedocs.io/en/stable/)

## 8. Code Management and Import Organization

### Code Review:

- **Guideline:** Conduct regular code reviews and utilize tools like `ReviewNB` to review Jupyter notebooks.

- **Reference:** [ReviewNB Documentation](https://www.reviewnb.com/)

### Automated Refactoring:

- **Tool:** Use `sourcery` for automatic code refactoring to improve readability and efficiency.

- **Reference:** [Sourcery Documentation](https://sourcery.ai/)

### Pre-Commit Management:

- **Tool:** Implement `pre-commit` to manage and maintain pre-commit hooks, ensuring that issues are identified and fixed before committing.

- **Reference:** [Pre-Commit Documentation](https://pre-commit.com/)

- **Guideline:** Configure pre-commit hooks to run code formatters, linters, and other tools automatically before each commit, preventing commits if the checks fail.

### Import Organization:

- **Tool:** Use `isort` to automatically organize imports in a consistent, PEP 8-compliant manner.

- **Reference:** [isort Documentation](https://pycqa.github.io/isort/)

- **Guideline:** Regularly run `isort` to maintain import organization and reduce merge conflicts related to import order.
