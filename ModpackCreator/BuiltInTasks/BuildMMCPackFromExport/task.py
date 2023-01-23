from ModpackCreator.ATask import ATask
from ModpackCreator.ATask import AVarDef
from ModpackCreator.InputVarTypes.PathVar import RelativeToPathVar
import os
import re
from ..CurseForgeToMultiMC.task import MultiMCInstancePathVar
from ..BuildCurseforgePackFromExport.task import ModpackNameVar

from . import FilesFunctions
import json


class MultiMCInstanceExportPathVar(RelativeToPathVar):
    format_feedback = "Invalid path. Expected a valid MultiMC instance .zip export."

    def __init__(self, name: str, default: str = None):
        description = "The path to the MultiMC instance .zip export. The path must be relative to the exports directory (./exports/)."
        super().__init__(name, description, default, "./exports/")

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Get zip name
        zip_name = '.'.join(value.split("/")[-1].split(".")[0:-1])
        # Verify RelativeToPathVar validation
        if not super()._validate(value):
            return False
        # Concatenate the path and the value
        path = self.path + '/' + value
        # Verify that the path is a .zip file
        if not os.path.isfile(path) or not path.endswith(".zip"):
            print("Not a .zip")
            return False
        # Verify that the .zip contains a minecraft or .minecraft folder
        if not FilesFunctions.zip_contains_dir(path, zip_name + "/minecraft") and not FilesFunctions.zip_contains_dir(path, zip_name + "/.minecraft"):
            print("No minecraft folder found in .zip")
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


class Task(ATask):

    # Prepared export paths
    curseforge_prepared_export_path = "temp/curseforge_prepared_export.zip"
    mmc_prepared_export_path = "temp/mmc_prepared_export.zip"

    # Setup configs list
    setup_configs = [
        MultiMCInstancePathVar("mmc_instance", "Path to the MMC instance folder", passive=True),
        ModpackNameVar("modpack_name", "Name of the modpack", passive=True)
    ]

    # Run variables
    run_args = [
        MultiMCInstanceExportPathVar("mmc_instance_export_path"),
        VersionVar("version", "New version of the pack")
    ]

    def prepare_mmc_profile(self):
        print("Preparing MultiMC profile")
        # Name value regex
        name_value_regex = re.compile(r"\d+\.\d+\.\d+-?\w*\.?\d*")
        # Get instance name
        instance_name = self.config["mmc_instance"].split("/")[-1].split("\\")[-1]
        # Get the raw export path
        raw_export_path = "./exports/" + self.args["mmc_instance_export_path"]
        # Remove old prepared export
        if os.path.isfile(self.mmc_prepared_export_path):
            os.remove(self.mmc_prepared_export_path)
        # Copy the export to the prepared export path
        FilesFunctions.copy_file(raw_export_path, self.mmc_prepared_export_path, "exported profile", "prepare profile")
        # Copy instance.cfg from zip to temp
        FilesFunctions.copy_from_zip(instance_name + "/instance.cfg", "temp/instance.cfg", self.mmc_prepared_export_path)
        # Open the instance.cfg file
        with open("temp/instance.cfg", "r+") as instance_cfg_file:
            content = instance_cfg_file.read()
            # Replace the version
            content = name_value_regex.sub(self.args["version"], content)
            # Replace the instance name
            instance_cfg_file.seek(0)
            instance_cfg_file.truncate()
            instance_cfg_file.write(content)
        # Copy instance.cfg from temp to zip
        FilesFunctions.copy_to_zip("temp/instance.cfg", instance_name + "/instance.cfg", self.mmc_prepared_export_path)

        # Remove temp/instance.cfg
        if os.path.isfile("temp/instance.cfg"):
            os.remove("temp/instance.cfg")

    def pack_mmc(self):
        print("Packing MultiMC profile")

        # Preparing command
        program = "mmc-export"
        from_zip = "-i " + self.mmc_prepared_export_path
        output_format = "-f Modrinth"
        search_mod = "--modrinth-search loose"
        output_directory = "-o ./output"
        toml_file = "-c ./mmc-export.toml"
        pack_version = "-v " + self.args["version"]
        scheme = f'--scheme {self.config["modpack_name"]+"-{version}"}'

        # Concatenate command
        cmd = f"{program} {from_zip} {output_format} {search_mod} {output_directory} {toml_file} {pack_version} {scheme}"
        print(cmd)

        # Run command
        os.system(cmd)
        

    # Run the task
    def _run(self):
        self.prepare_mmc_profile()
        self.pack_mmc()
