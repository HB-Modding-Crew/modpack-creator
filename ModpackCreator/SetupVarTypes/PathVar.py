from ATask import AVarDef
import re
import os

regex_path_unix = r"^((/)|((~|\.\.?|\.)/?))?([\w-]+/)*[\w-]*/?$"

class PathVar(AVarDef):

    format_feedback = "Invalid path format. Expected a valid Unix path."

    # Verify that the value is a valid path
    def __validate(self, value: str):
        # Verify that the path is valid Unix path
        if re.match(regex_path_unix, value):
            return True
        return False

class AbsolutePathVar(PathVar):

    format_feedback = "Invalid path format. Expected a valid absolute Unix path."

    # Verify that the value is a valid absolute path
    def __validate(self, value: str):
        # Verify PathVar validation
        if not super().__validate(value):
            return False
        # Verify that the path is absolute
        if value[0] == "/" or value[0:2] == "~/":
            return True
        return False

class RelativePathVar(PathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path."

    # Verify that the value is a valid relative path
    def __validate(self, value: str):
        # Verify PathVar validation
        if not super().__validate(value):
            return False
        # Verify that the path is relative
        if value[0] != "/" and value[0:2] != "~/":
            return True
        return False

class RelativeToPathVar(RelativePathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The target path must exist."

    # Init
    def __init__(self, name: str, description: str, default: str = None, abs_path: str = ""):
        super().__init__(name, description, default)
        self.path = abs_path

    # Verify that the value is a valid relative path
    def __validate(self, value: str):
        # Verify RelativePathVar validation
        if not super().__validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path exists
        if os.path.exists(path):
            return True
        return False

class DirectoryRelativeToPathVar(RelativeToPathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The target path must be an existing directory."

    # Verify that the value is a valid relative path
    def __validate(self, value: str):
        # Verify RelativeToPathVar validation
        if not super().__validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path is a directory
        if os.path.isdir(path):
            return True
        return False

class FileRelativeToPathVar(RelativeToPathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The target path must be an existing file."

    # Verify that the value is a valid relative path
    def __validate(self, value: str):
        # Verify RelativeToPathVar validation
        if not super().__validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path is a file
        if os.path.isfile(path):
            return True
        return False