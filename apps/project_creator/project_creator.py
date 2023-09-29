# {root}/apps/project_creator/project_creator.py

import os
import logging
import sys
from typing import List, Dict, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from modules.io.directory_creator import DirectoryCreator
from modules.io.file_creator import FileCreator

logger = logging.getLogger(__name__)

class ProjectCreator:
    def __init__(self, dir_creator: DirectoryCreator, file_creator: FileCreator):
        self.dir_creator = dir_creator
        self.file_creator = file_creator

    def create_project(self, root_dir: str, app_name: str, interface_groups: List[str], module_groups: List[str]) -> None:
        try:
            dirs, files = self._setup_structure(root_dir, app_name, interface_groups, module_groups)
            self._create_directories(dirs)
            self._create_files(files, app_name)
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    def _setup_structure(self, root_dir: str, app_name: str, interface_groups: List[str], module_groups: List[str]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
        dirs = {
            'apps': [os.path.join(root_dir, "apps", app_name)],
            'docs': [os.path.join(root_dir, "docs")],
            'tests': [os.path.join(root_dir, "tests")],
            'interfaces': [],
            'modules': [],
        }
        
        files = {
            'apps': [os.path.join(dirs['apps'][0], "__init__.py"), os.path.join(dirs['apps'][0], "main.py")],
            'docs': [os.path.join(dirs['docs'][0], f"{app_name}.md")],
        }
        
        for group in set(interface_groups + module_groups):
            dirs['interfaces'].append(os.path.join(root_dir, "interfaces", group))
            dirs['modules'].append(os.path.join(root_dir, "modules", group))
        
        return dirs, files

    def _create_directories(self, dirs: Dict[str, List[str]]) -> None:
        for dir_list in dirs.values():
            for dir in dir_list:
                try:
                    self.dir_creator.create(dir)
                except Exception as e:
                    logger.error(f"Failed to create directory {dir}: {e}")
                    raise

    def _create_files(self, files: Dict[str, List[str]], app_name: str) -> None:
        for key, file_list in files.items():
            comment = f"Module: {key.capitalize()}"
            for file in file_list:
                content = None
                if 'main.py' in file:
                    content = '''\
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
'''
                try:
                    self.file_creator.create_with_content(file, comment, content)
                except Exception as e:
                    logger.error(f"Failed to create file {file}: {e}")
                    raise
