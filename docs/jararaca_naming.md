# Jararaca Naming and Folder Conventions

## TL;dr:

The _Jararaca_ project emphasizes rational organization and coherent naming conventions to enhance clarity, maintainability, and scalability. The project's structure divides interface and module classes into distinct sub-packages, reflecting their roles and usage contexts.

- **Directory Structure:**
  - `interfaces/`: Holds definitions of contracts and interface classes.
  - `modules/`: Contains concrete class implementations.
  - `docs/`: Allocated for comprehensive documentation.
  - `tests/`: Organizes testing suites and cases.
  - `apps/`: Stores implementations specific to applications.

- **Group Definitions:**
  - `util`: Hosts reusable utility classes/functions.
  - `io`: Manages classes/functions for Input/Output operations.
  - `linux`: Houses classes/functions specific to the Linux operating system.

- **Naming Guidelines:**
  - Names should be descriptive, succinct, in singular form, and domain-specific.
  - Group names should use lowercase alphabets, avoiding spaces or special characters.

- **Naming Procedure:**
  - Identify shared themes, generate reflective and concise names, evaluate and select the most fitting name ensuring adherence to protocols.

- **Naming Examples:**
  - Database Operations: `database`
  - Utility Functions/Classes: `util`
  - Input/Output Operations: `io`
  - User Management Classes: `user`

- **Importance of Naming Conventions:**
  - Ensures clearness, consistency, readability, and maintainability.
  - Aligns interfaces with their implementations, facilitating effective code navigation and adjustments.

- **Specific Naming and Location Conventions:**
  - **Interfaces:** Names should append `-able` and be located in `interfaces/{group}`.
  - **Concrete Classes:** Names should be indicative of functions and be placed in `modules/{group}`.
  - **Application-specific Classes:** Should have project-related names and be located in `apps/{app_name}/`.
  - **Documentation:** Should be housed in the `docs/` directory with descriptive filenames.
  - **Test Cases:** Should clearly reflect the functionality being tested and be organized within the `tests/` directory.

### Examples:

- **Interfaces:**
  - `interfaces/util/loggable.py` (Logging functionalities)
- **Concrete Classes:**
  - `modules/io/yaml_file_reader.py` (Reading file operations)
- **Application-specific Classes:**
  - `apps/{app_name}/implementation.py` (Unique needs of `{app_name}`)
- **Documentation:**
  - `docs/module_docs.md` (Details of various project modules)
- **Test Cases:**
  - `tests/test_file_reader.py` (Tests for `file_reader.py` class)

## Structure and Layout of Files & Directories

The _Jararaca_ project underscores the necessity for rational and coherent organization and naming of files, aiming to optimize the clarity, maintainability, and scalability of the codebase. The subsequent conventions and structures are advocated for the categorization of interface and module classes into coherent groups, corresponding to their roles and functions in the system.

```
jararaca/
│
├── interfaces/           # Definitions of Contracts and Interface Classes
├── modules/              # Concrete Classes Implementations
├── docs/                 # Exhaustive Documentation
├── tests/                # Testing Suites and Test Cases
└── apps/                 # Implementations Specific to Applications
```

```plaintext
jararaca/
│
├── interfaces/
│   ├── util/             # Interface Classes for Utilities
│   │   ├── loggable.py   # Interface for Logging Contract
│   ├── io/               # Interface Classes for Input/Output
│   │   ├── report_issuable.py   # Interface for Report Issuing Contract
│   ├── linux/            # Interface Classes Specific to Linux
│   │   ├── checker_able.py   # Interface for Checking Contract
│   └── ...
│
├── modules/
│   ├── util/             # Concrete Utility Classes
│   │   ├── logger.py     # Implementation of Logger
│   ├── io/               # Concrete Classes for Input/Output
│   │   ├── report_issuer.py   # Implementation of Report Issuer
│   ├── linux/            # Concrete Classes Specific to Linux
│   │   ├── checkers.py   # Implementations of Various Checkers
│   │   ├── package_installer.py   # Implementation of Package Installer
│   └── ...
│
├── docs/                 # Documentation
├── tests/                # Test Cases
└── apps/                 # Classes Specific to Applications
```

_Jararaca’s_ directory architecture meticulously segments interface and module classes into appropriate sub-packages, mirroring their roles and contexts of use.

### Definitions and Examples of Groups:

Establishing well-structured groups or sub-packages offers an abstraction layer, promoting effective location and comprehension of classes and their related interfaces.

1. **util**
   - **Objective:** Host reusable utility classes and functions across various modules.
   - **Illustration:** `logger.py`, `loggable.py`

2. **io**
   - **Objective:** Contain classes and functions for managing Input/Output operations, ensuring modular handling of diverse IO operations.
   - **Illustration:** `report_issuer.py`, `report_issuable.py`

3. **linux**
   - **Objective:** House classes and functions oriented towards interactions and functionalities specific to the Linux operating system.
   - **Illustration:** `checkers.py`, `checker_able.py`

#### Guidelines for Naming a Group

##### Overview:

Effective naming of a group or sub-package is pivotal for maintaining consistent organizational paradigms. Names should accurately represent the role, functionality, or domain of the classes and interfaces enclosed, aiming to offer immediate comprehension of the group's intention, thereby facilitating proficient navigation and amendments of the codebase.

##### Naming Protocols:

1. **Descriptive and Succinct:** A group name should reflect its objective or the shared functionality of its components, avoiding excessive or unclear nomenclatures.

2. **Singular Form Preference:** Opt for singular forms for group names, unless the plural form provides better intuitive and domain-relevant understanding, (e.g., `util` instead of `utils`).

3. **Lowercase Alphabets Only:** Employ lowercase alphabets and refrain from using spaces or special characters, utilizing underscores if required for readability.

4. **Domain-Specific Terms:** Prefer domain-centric terminologies when they yield clearer context and comprehension.

##### Naming Procedure:

###### Identify Shared Theme:

Examine the group’s elements to discern their shared function or purpose.

###### Generate Potential Names:

Propose potential names that are reflective and concise based on the shared theme.

###### Evaluate Proposed Names:

Scrutinize the proposals for clarity, brevity, and domain relevance. Assess adaptability to future expansions or alterations.

###### Select the Name:

Adopt the most fitting name, ensuring compliance with predefined protocols.

#### Illustrations:

Given the protocols and procedure described above, the following are examples of potential group names:

1. **For Database Operations Group:**
   - Potential Names: `database`, `db_ops`, `data_store`
   - Selected Name: `database`

2. **For Utility Functions and Classes Group:**
   - Potential Names: `util`, `common`, `helper`
   - Selected Name: `util`

3. **For Input/Output Operations Group:**
   - Potential Names: `io`, `input_output`, `io_manager`
   - Selected Name: `io`

4. **For User Management Classes Group:**
   - Potential Names: `user`, `user_mgmt`, `account`
   - Selected Name: `user`

### Recapitulation:

Formulating coherent and succinct group names is crucial for sustaining an organized and intelligible codebase. Adhering to predefined naming protocols and following a deliberate naming procedure ensures uniformity and transparency throughout the project, contributing to the refined maintainability and scalability of the _Jararaca_ project.

- **Clearness and Consistency:** Prescribed structures and grouping protocols establish a logical and intuitive organizational pattern, aligning interfaces with their practical implementations.
- **Readability and Sustainment:** Deliberate categorization of associated classes and interfaces within specific subdirectories elucidates purposes and usage contexts, smoothing the processes of code navigation and adjustment.
- **Alignment and Unity:** Developing corresponding sub-packages in `interfaces/` and `modules/` directories fortifies the symbiotic association between interfaces and their implemented classes, maintaining coherence within the codebase.

## Interfaces:

- **Convention:** Append `-able` to interface class names for clear identification of their role.
- **Location:** House interfaces in the `interfaces/{group}` directory.
- **Example:** `interfaces/util/loggable.py` - Establishes contracts for logging functionalities.

## Concrete Classes:

- **Convention:** The names of concrete classes should be indicative of their functions.
- **Location:** Place them in the `modules/{group}` directory, categorized by function or role.
- **Example:** `modules/io/yaml_file_reader.py` - Specializes in reading file operations.

## Classes Specific to Applications:

- **Convention:** Assign distinctive, project-related names to these classes.
- **Location:** Store these classes in the corresponding application directory, structured as `apps/{app_name}/`.
- **Example:** `apps/{app_name}/implementation.py` - Satisfies the unique needs of '{app_name}'.

## Documentation:

- **Location:** Allocate all documentation to the `docs/` directory, with filenames accurately representing their content. Arrange example docs in a `docs/` subdirectory.
- **Example:** `docs/module_docs.md` - Details various project modules.

## Test Cases:

- **Convention:** The names of test cases should clearly reflect the module or functionality being tested.
- **Location:** Organize all test cases within the `tests/` directory.
- **Example:** `tests/test_file_reader.py` - Holds tests for the `file_reader.py` class.
