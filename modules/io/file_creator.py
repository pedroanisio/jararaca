# {root}/modules/io/file_creator.py
from datetime import datetime
from interfaces.io.creatable import Creatable

class FileCreator(Creatable):
    
    def create(self, path: str, comment: str = None):
        """
        Creates a new file at the given path. If a comment is provided, 
        it also logs the comment, filename, and the creation date/time.
        
        :param path: The path where the new file will be created.
        :param comment: An optional comment to be added to the file.
        """
        try:
            with open(path, "w") as file:
                if comment:
                    filename = path.split("/")[-1]
                    file.write(f"# {filename} {comment}\n")
                    file.write(f"# Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            print(f"Created File: {path}")
        except Exception as e:
            print(f"Error creating file {path}: {e}")
            # Consider re-raising the exception if necessary.
            # raise e

    def create_with_content(self, path: str, comment: str = None, content: str = None) -> None:
        """
        Creates a new file at the given path with optional comment and content, 
        logs the filename and the creation date/time if comment is provided.
        
        :param path: The path where the new file will be created.
        :param comment: An optional comment to be added to the file.
        :param content: The content to be added to the new file.
        """
        try:
            with open(path, "w") as file:
                if comment:
                    filename = path.split("/")[-1]
                    file.write(f"# {filename} {comment}\n")
                    file.write(f"# Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                if content:
                    file.write(content)
            print(f"Created File: {path}")
        except Exception as e:
            print(f"Error creating file {path}: {e}")
            # Consider re-raising the exception if necessary.
            # raise e
