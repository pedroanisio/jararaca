# {root}/apps/project_creator/main.py

import argparse
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from modules.io.file_creator import FileCreator
from modules.io.directory_creator import DirectoryCreator
from project_creator import ProjectCreator

def main(args):
    root_dir = args.root_dir
    app_name = args.app_name

    # Initialize the actual DirectoryCreator and FileCreator objects here (adhering to the interfaces)
    dir_creator = DirectoryCreator()  # Assuming DirectoryCreator adheres to IDirectoryCreator
    file_creator = FileCreator()  # Assuming FileCreator adheres to IFileCreator

    project_creator = ProjectCreator(dir_creator, file_creator)
    project_creator.create_project(root_dir, app_name, args.interface_groups, args.module_groups)
    print(f"Jararaca project structure created under {root_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Jararaca project structure.')
    parser.add_argument('root_dir', type=str, help='Root directory of the project.')
    parser.add_argument('app_name', type=str, help='Name of the app.')
    parser.add_argument('--interface-groups', nargs='+', help='List of interface groups to be created.', default=[])
    parser.add_argument('--module-groups', nargs='+', help='List of module groups to be created.', default=[])
    args = parser.parse_args()
    main(args)

