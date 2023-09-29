# {root}/modules/io/directory_creator.py
import os
from interfaces.io.creatable import Creatable

class DirectoryCreator(Creatable):
    def create(self, path: str, comment: str = ""):
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Created Directory: {path}")
        except OSError as e:
            print(f"Error creating directory {path}: {e}")

    def create_with_content(self, path: str, comment: str = None, content: str = None) -> None:
        """
        Creates a new entity at the given path with optional comment and content.

        :param path: The path where the new entity will be created.
        :param comment: An optional comment to be added to the entity.
        :param content: The content to be added to the new entity.
        """
        pass