from ModpackCreator.ATask import ATask
from ModpackCreator.ATask import AVarDef
from ModpackCreator.InputVarTypes.PathVar import RelativeToPathVar
import os
import re
from ..CurseForgeToMultiMC.task import MultiMCInstancePathVar

from . import FilesFunctions
import json

class CurseforgeInstanceExportPathVar(RelativeToPathVar):
    format_feedback = "Invalid path. Expected a valid CurseForge instance .zip export (it must contain a manifest.json file)."

    def __init__(self, name: str, description: str, default: str = None):
        description = "The path to the CurseForge instance .zip export. The path must be relative to the exports directory (./exports/)."
        super().__init__(name, description, default, "./exports/")

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify RelativeToPathVar validation
        if not super()._validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + '/' + value
        # Verify that the path is a .zip file
        if not os.path.isfile(path) or not path.endswith(".zip"):
            print("Not a .zip")
            return False
        # Verify that the .zip contains a manifest.json file
        if not FilesFunctions.zip_contains_file(path, "manifest.json"):
            print("No manifest.json found in .zip")
            return False
        return True

class VersionVar(AVarDef):
    format_feedback = "Invalid version. Expected a valid version number (ex: 1.0.0)."

    # Version regex: X.X.X
    version_regex = re.compile(r"\d+\.\d+\.\d+-?\w*\.?\d*")

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify that the value matches the version regex
        if not self.version_regex.match(value):
            print("Invalid version number")
            return False
        return True

class ModpackNameVar(AVarDef):
    format_feedback = "Invalid modpack name. Expected a valid modpack name (sould not conain any path forbidden characters)."

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Should not contain aany path forbidden characters
        if not re.match(r"^[^\\/:*?\"<>|]+$", value):
            print("Invalid modpack name")
            return False
        return True


class Task(ATask):

    # Prepared export paths
    curseforge_prepared_export_path = "temp/curseforge_prepared_export.zip"
    mmc_prepared_export_path = "temp/mmc_prepared_export.zip"

    # Setup configs list
    setup_configs = [
        ModpackNameVar("modpack_name", "Name of the modpack", passive=True),
    ]

    # Run variables
    run_args = [
        CurseforgeInstanceExportPathVar("curseforge_instance_export_path", "Path to the curseforge instance .zip export"),
        VersionVar("version", "New version of the pack")
    ]

    def prepare_curseforge_profile(self):
        print("Preparing curseforge profile")
        # Get the raw export path
        raw_export_path = "./exports/" + self.args["curseforge_instance_export_path"]
        # Remove old prepared export
        if os.path.isfile(self.curseforge_prepared_export_path):
            os.remove(self.curseforge_prepared_export_path)
        # Copy the export to the prepared export path
        FilesFunctions.copy_file(raw_export_path, self.curseforge_prepared_export_path, "exported profile", "prepare profile")
        # Copy manifest.json from zip to temp
        FilesFunctions.copy_from_zip("manifest.json", "temp/manifest.json", self.curseforge_prepared_export_path)
        # Open the manifest.json file
        with open("temp/manifest.json", "r+") as manifest_file:
            content = manifest_file.read()
            # As json
            content_json = json.loads(content)
            # Replace the version
            content_json["version"] = self.args["version"]
            # Replace the manifest file
            manifest_file.seek(0)
            manifest_file.truncate()
            manifest_file.write(json.dumps(content_json, indent=4))
        # Copy manifest.json from temp to zip
        FilesFunctions.copy_to_zip("temp/manifest.json", "manifest.json", self.curseforge_prepared_export_path)

    def pack_curseforge(self):
        print("Packing curseforge")
        # Copy the prepared export to the output directory
        FilesFunctions.copy_file(self.curseforge_prepared_export_path, "output/" + self.config["modpack_name"] + "-" + self.args["version"] + ".zip", "prepared curseforge export", "output pack")
        
    # Run the task
    def _run(self):
        self.prepare_curseforge_profile()
        self.pack_curseforge()
