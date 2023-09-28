# Jararaca Code Style Guide and Practices

## TL;DR:

#### 1. **Code Formatting and Style:**
   - Strict compliance with [PEP 8](https://pep8.org/).
   - Use `snake_case` for variables, functions, and `CamelCase` for classes.
   - 4 spaces for indentation, following PEP 8 spacing.

#### 2. **Documentation and Comments:**
   - Clear and concise docstrings for each module, class, and function following [PEP 257](https://pep257.readthedocs.io/en/latest/).
   - Informative inline comments focusing on the 'why' over the 'how'.

#### 3. **Code Construction and Best Practices:**
   - Code should be modular, maintainable, and reusable.
   - Robust error handling, with relevant error messages, adhering to [PEP 8](https://pep8.org/#errors) error guidelines.
   - Follow SOLID principles for adaptable and extendable code; reference [SOLID Principles](https://en.wikipedia.org/wiki/SOLID).

#### 4. **Project Structure and Resource Management:**
   - Logical segmentation of code into packages/modules, with `setup.py` or `pyproject.toml` for dependency organization.
   - Effective resource management using context managers and following [PEP 343](https://pep-343.org/).

#### 5. **Testing and Quality Assurance:**
   - Comprehensive tests (unit, integration, and E2E) using `pytest` or `unittest`; reference [Testing Guide](https://docs.python-guide.org/writing/tests/).
   - Advocate for Test-Driven Development (TDD) and prioritize testing pivotal scenarios.

#### 6. **Performance and Optimization:**
   - Regularly profile and refine code for resource efficiency and consider performance during development.
   - Choose suitable algorithms and data structures and justify choices in code reviews; reference [Python Profilers](https://docs.python.org/3/library/profile.html).

## 1. Code Formatting and Style

### PEP 8 Compliance

- **Guideline:** Maintain strict compliance with the [PEP 8 Style Guide](https://pep8.org/) to preserve uniformity and readability in the Python codebase.

### Naming Conventions

- **Guideline:** Apply `snake_case` for variables, functions, methods, and file names; utilize `CapWords` or `CamelCase` for class names.

- **Reference:** [PEP 8 -- Descriptive: Naming Styles](https://pep8.org/#descriptive-naming-styles)

### Indentation and Spacing

- **Guideline:** Employ 4 spaces for each indentation level and adhere to consistent spacing as per PEP 8 standards.

### Type Annotations and Enforcement

- **Guideline:** Adhere to [PEP 484](https://pep-484.org/) and [PEP 585](https://www.python.org/dev/peps/pep-0585/) for type annotations/hints.

- **Enforcement**

- Implement a review checklist to ensure adherence during code reviews.

- **Guideline**

- Promote the incorporation of type hints in function signatures to augment code clarity.

## 2. Documentation and Comments

### Mandatory Docstrings

- **Guideline:** Supply succinct and clear docstrings for each module, class, and function, following [PEP 257 – Docstring Conventions](https://pep257.readthedocs.io/en/latest/).

### Commenting and Inline Documentation

- **Guideline:** Embed comprehensive inline comments for intricate code sections, maintaining clarity, conciseness, and relevance.

- **Guideline**

- Comments should elucidate the 'why' over the 'how', portraying the intention and nuances, not the overt functionality.

### Clarity

- Formulate comments and docstrings in plain English and abstain from jargon, making them comprehendible for varying expertise levels.

## 3. Code Construction and Best Practices

### Modularity and Decomposition

- **Guideline:** Foster reusability, maintainability, and the elimination of redundancy by organizing code into coherent, logical modules and functions.

### Error Handling

- **Guideline:** Embrace robust error handling using try/except blocks and produce informative, pertinent error messages.

- **Reference:** [PEP 8 -- Style Guide for Python Code: Errors](https://pep8.org/#errors)

### Object-Oriented Design and SOLID Principles

- **Guideline:** Adhere to SOLID principles for adaptable, extendable code, comprising:

1. **S**ingle Responsibility Principle (SRP)

2. **O**pen/Closed Principle (OCP)

3. **L**iskov Substitution Principle (LSP)

4. **I**nterface Segregation Principle (ISP)

5. **D**ependency Inversion Principle (DIP)

- **Reference:** [SOLID Principles on Wikipedia](https://en.wikipedia.org/wiki/SOLID)

- **Practical Application**

- Regularly assess and discuss the application of SOLID principles during code reviews to fortify understanding and accurate implementation amongst all team members.

## 4. Project Structure and Resource Management

### Project and Package Structure

- **Guideline:** Segment code into lucid, logical packages/modules, and leverage `setup.py` or `pyproject.toml` for project and dependency organization.

- **Reference:** [Packaging Python Projects — Python Packaging User Guide](https://packaging.python.org/tutorials/packaging-projects/)

### Resource Management

- **Guideline:** Implement context managers (using the `with` statement) for managing resources such as file or network connections.

- **Reference:** [PEP 343 -- The "with" Statement](https://pep-343.org/)

- **Best Practice**

- Advocate the correct usage of resource management strategies to preclude resource leaks and to optimize system resource utilization.

## 5. Testing and Quality Assurance

### Testing

- **Guideline:** Create exhaustive tests encompassing unit, integration, and end-to-end tests, utilizing frameworks like `pytest` or `unittest`.

- **Reference:** [Testing Your Code — The Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/tests/)

- **Best Practice**

- Advocate for Test-Driven Development (TDD) as it fosters clearer, focused code and diminishes bug occurrences.

### Coverage

- Aim for extensive test coverage, prioritizing the testing of pivotal scenarios over quantity.

- **Guideline**

- Prioritize testing for the most defect-prone or critical areas of the application’s functionality.

## 6. Performance and Optimization

### Performance Consideration

- **Guideline**

- Consistently profile and refine code to ensure resource-efficient operations and consider performance implications during feature development and existing code alterations.

- **Reference**

- [Python Profilers: Official Documentation](https://docs.python.org/3/library/profile.html)

### Algorithm and Data Structure Selection

- **Guideline**

- Opt for the most suitable algorithms and data structures given the context, and substantiate the choices made during code reviews.