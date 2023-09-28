# Jararaca Naming and Folder Conventions

## Repository File Structure:

```plaintext
jararaca/
│
├── docs/                  # Documentation Files Reside Here
│   ├── module_docs.md     # Overview of Various Modules
│   └── examples/          # Contains Examples and Tests
│       └── ...
│
├── interfaces/            # Houses Interface Classes
│   ├── loggable.py        # Example Interface Class
│   └── ...
│
├── modules/               # Holds Concrete Classes
│   ├── io/                # Category for IO Classes
│   │   └── yaml_file_reader.py   # Sample IO Class
│   ├── util/              # Category for Utility Classes
│   │   └── utility.py    
│   └── ...
│
├── tests/                 # Encompasses Test Cases and Suites
│   └── ...
│
```

## Interfaces:
- **Convention:** End interface class names with `-able` for clear denotation of their role.
- **Location:** Store all interfaces in the `interfaces/` directory.
- **Example:** `interfaces/loggable.py` - It establishes logging functionality contracts.

## Concrete Classes:
- **Convention:** Concrete class names should be descriptive, indicating their functions.
- **Location:** Position them in the `modules/` directory, sorted by function or role.
- **Example:** `modules/io/yaml_file_reader.py` - Focuses on reading file operations.

## Application-Specific Classes:
- **Convention:** Use distinct, project-appropriate names for these classes.
- **Location:** Organize these classes in the relevant application directory, formatted as `apps/{app_name}/`.
- **Example:** `apps/{app_name}/implementation.py` - Fulfills the exclusive requirements of '{app_name}'.

## Documentation:
- **Location:** All documentation should be located in the `docs/` directory, with filenames accurately depicting their subject matter. Position example docs in a `docs/` subdirectory.
- **Example:** `docs/module_docs.md` - Enumerates various project modules.

## Test Cases:
- **Convention:** Test case names should be explicit, signifying the module or functionality under test.
- **Location:** Arrange all test cases in the `tests/` directory.
- **Example:** `tests/test_file_reader.py` - Contains tests for the `file_reader.py` class.