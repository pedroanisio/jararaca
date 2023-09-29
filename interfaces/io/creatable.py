# {root}/interfaces/io/creatable.py

from abc import ABC, abstractmethod

class Creatable(ABC):

    @abstractmethod
    def create(self, path: str, comment: str = ""):
        """
        Creates a new entity at the given path with an optional comment.

        :param path: The path where the new entity will be created.
        :param comment: An optional comment to be added to the entity.
        """
        pass

    @abstractmethod
    def create_with_content(self, path: str, comment: str = None, content: str = None) -> None:
        """
        Creates a new entity at the given path with optional comment and content.

        :param path: The path where the new entity will be created.
        :param comment: An optional comment to be added to the entity.
        :param content: The content to be added to the new entity.
        """
        pass
