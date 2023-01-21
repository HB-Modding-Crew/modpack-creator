from ModpackCreator.ATask import AVarDef
import re
import os

regex_path_unix = r"^((/)|((~|\.\.?|\.)/?))?([\w\-\.0-9 ]+/)*[\w\-\.0-9 ]*/?$"

class PathVar(AVarDef):

    format_feedback = "Invalid path format. Expected a valid Unix path."

    # Verify that the value is a valid path
    def _validate(self, value: str):
        # Verify that the path is valid Unix path
        if re.match(regex_path_unix, value):
            return True
        return False

class AbsolutePathVar(PathVar):

    format_feedback = "Invalid path format. Expected a valid absolute Unix path."

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify PathVar validation
        if not super()._validate(value):
            return False
        # Verify that the path is absolute
        if value[0] == "/" or value[0:2] == "~/":
            return True
        return False

class RelativePathVar(PathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path."

    # Verify that the value is a valid relative path
    def _validate(self, value: str):
        # Verify PathVar validation
        if not super()._validate(value):
            return False
        # Verify that the path is relative
        if value[0] != "/" and value[0:2] != "~/":
            return True
        return False

class RelativeToPathVar(RelativePathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The target path must exist. From the anchor path: '{selfpath}'"

    # Init
    def __init__(self, name: str, description: str, default: str = None, anchor_path: str = ""):
        super().__init__(name, description, default)
        self.path = anchor_path

    # Verify that the value is a valid relative path
    def _validate(self, value: str):
        # Format the feedback
        self.format_feedback = self.format_feedback.format(selfpath=self.path)
        # Verify RelativePathVar validation
        if not super()._validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path exists
        if os.path.exists(path):
            return True
        return False

class DirectoryRelativeToPathVar(RelativeToPathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The path must target an existing directory from the anchor path: '{selfpath}'"

    # Verify that the value is a valid relative path
    def _validate(self, value: str):
        # Verify RelativeToPathVar validation
        if not super()._validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path is a directory
        if os.path.isdir(path):
            return True
        return False

class FileRelativeToPathVar(RelativeToPathVar):

    format_feedback = "Invalid path format. Expected a valid relative Unix path. The path must target an existing file from the anchor path: '{selfpath}'"

    # Verify that the value is a valid relative path
    def _validate(self, value: str):
        # Verify RelativeToPathVar validation
        if not super()._validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + value
        # Verify that the path is a file
        if os.path.isfile(path):
            return True
        return False

class FileAbsolutePathVar(AbsolutePathVar):

    format_feedback = "Invalid path format. Expected a valid absolute Unix path. The path must target an existing file."

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify AbsolutePathVar validation
        if not super()._validate(value):
            return False
        # Verify that the path is a file
        if os.path.isfile(value):
            return True
        return False

class DirectoryAbsolutePathVar(AbsolutePathVar):
    
        format_feedback = "Invalid path format. Expected a valid absolute Unix path. The path must target an existing directory."
    
        # Verify that the value is a valid absolute path
        def _validate(self, value: str):
            # Verify AbsolutePathVar validation
            if not super()._validate(value):
                return False
            # Verify that the path is a directory
            if os.path.isdir(value):
                return True
            return False