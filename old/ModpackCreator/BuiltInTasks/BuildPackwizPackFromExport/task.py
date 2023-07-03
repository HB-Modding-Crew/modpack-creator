from ModpackCreator.ATask import ATask
from ModpackCreator.ATask import AVarDef
from ModpackCreator.InputVarTypes.PathVar import RelativeToPathVar
import os
import re
from ..CurseForgeToMultiMC.task import MultiMCInstancePathVar
from ..BuildCurseforgePackFromExport.task import ModpackNameVar

from . import FilesFunctions
import json

from pathlib import Path
from shutil import unpack_archive, make_archive

default_instance_includes_list = [
    "config",
    "mods",
    "resourcepacks",
    "options.txt"
]


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

        # Find minecraft folder name
        if FilesFunctions.zip_contains_dir(self.mmc_prepared_export_path, instance_name + "/.minecraft"):
            minecraft_folder_name = ".minecraft"
        elif FilesFunctions.zip_contains_dir(self.mmc_prepared_export_path, instance_name + "/minecraft"):
            minecraft_folder_name = "minecraft"
        else:
            raise Exception("Could not find minecraft folder in zip")

        # Remove temp/instance.cfg
        if os.path.isfile("temp/instance.cfg"):
            os.remove("temp/instance.cfg")

        # Keep only the included files
        # Get the list of files to include
        included_files = self.config["instance_includes_list"]
        # If the directory already exists, delete it
        if os.path.isdir("temp/temp_mmc_export_before_includes"):
            FilesFunctions.remove_dir("temp/temp_mmc_export_before_includes", "old before includes")
        # Open the zip file and copy content to temp
        unpack_archive(self.mmc_prepared_export_path, "temp/temp_mmc_export_before_includes")
        # If the directory already exists, delete it
        if os.path.isdir("temp/temp_mmc_export_after_includes"):
            FilesFunctions.remove_dir("temp/temp_mmc_export_after_includes", "old after includes")
        # create after includes directory
        os.mkdir("temp/temp_mmc_export_after_includes")
        # Copy all the files except .minecraft folder
        print("Copying all files except .minecraft folder")
        for file in os.listdir("temp/temp_mmc_export_before_includes" + "/" + instance_name):
            if file != minecraft_folder_name:
                if os.path.isfile("temp/temp_mmc_export_before_includes/" + instance_name + "/" + file):
                    FilesFunctions.copy_file("temp/temp_mmc_export_before_includes/" + instance_name + "/" + file, "temp/temp_mmc_export_after_includes/" + instance_name + "/" + file, "included file", "prepare profile")
                if os.path.isdir("temp/temp_mmc_export_before_includes/" + instance_name + "/" + file):
                    FilesFunctions.copy_dir("temp/temp_mmc_export_before_includes/" + instance_name + "/" + file, "temp/temp_mmc_export_after_includes/" + instance_name + "/" + file, "included file", "prepare profile")
        print("Copying included files in .minecraft folder")
        # Copy only the included files in the <instance_name> folder
        for file in included_files:
            if os.path.isfile("temp/temp_mmc_export_before_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file):
                FilesFunctions.copy_file("temp/temp_mmc_export_before_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file, "temp/temp_mmc_export_after_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file, "included file", "prepare profile")
            if os.path.isdir("temp/temp_mmc_export_before_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file):
                FilesFunctions.copy_dir("temp/temp_mmc_export_before_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file, "temp/temp_mmc_export_after_includes/" + instance_name + "/" + minecraft_folder_name + "/" + file, "included file", "prepare profile")
        
        # Normalize all end of lines with CRLF
        print("Normalizing all end of lines with CRLF")
        for root, dirs, files in os.walk("temp/temp_mmc_export_after_includes/" + instance_name):
            for file in files:
                list_of_txt_extensions = [".txt", ".json", ".toml", ".cfg", ".properties", ".lang", ".mcmeta", ".log", ".md", ".yml", ".yaml", ".json5"]
                if os.path.splitext(file)[1] in list_of_txt_extensions:
                    print("Normalizing " + file)
                    file_path = os.path.join(root, file)
                    with open(file_path, "r+") as f:
                        content = f.read()
                        content = content.replace("\r", "\n")
                        content = content.replace("\n\n", "\n")
                        content = content.replace("\n", "\r\n")
                        f.seek(0)
                        f.truncate()
                        f.write(content)

        # temp/temp_mmc_export_after_includes is now ready to be packed
        # Pack the zip
        print("Packing zip prepared for export")
        make_archive("temp/mmc_prepared_export", "zip", "temp/temp_mmc_export_after_includes")


    def pack_packwiz(self):
        print("Packing Packwiz profile")

        # Preparing command
        program = "mmc-export"
        from_zip = "-i " + self.mmc_prepared_export_path
        output_format = "-f packwiz"
        search_mod = "--modrinth-search loose"
        output_directory = "-o ./temp"
        toml_file = "-c ./Packwiz/mmc-export.toml"
        pack_version = "-v " + self.args["version"]
        provider_priority = "--provider-priority Modrinth CurseForge Other"
        scheme = f'--scheme mmc_export_packwiz_output'

        # Concatenate command
        cmd = f"{program} {from_zip} {output_format} {search_mod} {output_directory} {toml_file} {pack_version} {provider_priority} {scheme} --exclude-providers GitHub"
        print(cmd)

        # Run command
        os.system(cmd)

        # Packwiz zip path
        packwiz_zip_path = f"./temp/mmc_export_packwiz_output.zip"
        # Packwiz output path
        packwiz_output_path = Path("./") / "Packwiz" / f"{self.args['version']}"
        # Remove old packwiz output
        if os.path.isdir(packwiz_output_path):
            FilesFunctions.remove_dir(packwiz_output_path, "Old packwiz output")
        # Create packwiz output directory
        os.mkdir(packwiz_output_path)
        # Copy packwiz zip to packwiz output
        unpack_archive(packwiz_zip_path, packwiz_output_path)
        # Remove packwiz zip
        if os.path.isfile(packwiz_zip_path):
            os.remove(packwiz_zip_path)
        

    # Run the task
    def _run(self):

        # Verify in the configuation if the instance_includes_list is set
        if not "instance_includes_list" in self.config.keys():
            # If not, set it to the default value
            self.config["instance_includes_list"] = default_instance_includes_list
            # Save the configuration
            self.save_config()
            # Advise the user
            print("No instance includes list found in the configuration file. Set config with defaults includes. You can change it in the configuration file.")

        self.prepare_mmc_profile()
        self.pack_packwiz()
