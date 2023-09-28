# Jararaca Naming and Folder Conventions

## TL;dr:

The *Jararaca*  repository is organized into several directories: `docs/` for documentation, `interfaces/` for interface classes, `modules/` for concrete classes, and `tests/` for test cases. Interface classes are stored in `interfaces/` and should end with `-able`. Concrete classes are descriptive and sorted by function in `modules/`. Application-specific classes are placed in `apps/{app_name}/`. Documentation resides in `docs/`, with specific naming to reflect the content. Test cases are explicit and located in `tests/`. 

Example paths include:
- `interfaces/loggable.py`
- `modules/io/yaml_file_reader.py`
- `apps/{app_name}/implementation.py`
- `docs/module_docs.md`
- `tests/test_file_reader.py`

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