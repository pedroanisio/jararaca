---
{root}/docs/project_creator.md
---
# Project Creator Documentation

This document provides comprehensive details on the `project_creator` app of the Jararaca project. It describes the interfaces, modules, functionalities, and usage of the project creator application.

## Interfaces
### Creatable
Located at `interfaces/io/creatable.py`, it defines the contract for creating entities such as directories and files.

## Modules
### DirectoryCreator
Located at `modules/io/directory_creator.py`, it implements the `Creatable` interface for creating directories.

### FileCreator
Located at `modules/io/file_creator.py`, it implements the `Creatable` interface for creating files with specified content.

## Application
The main application is located at `apps/project_creator/main.py`. It orchestrates the use of `DirectoryCreator` and `FileCreator` to generate the project structure based on the provided command-line arguments.

## Usage
To generate the Jararaca project structure, run the `main.py` with the appropriate command-line arguments specifying the root directory, app name, interface groups, and module groups.
