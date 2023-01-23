from ModpackCreator.ATask import ATask
from ModpackCreator.InputVarTypes.PathVar import DirectoryAbsolutePathVar
import os

from . import FilesFunctions

default_instance_includes_list = [
    "config",
    "mods",
    "resourcepacks",
    "options.txt"
]

class MultiMCInstancePathVar(DirectoryAbsolutePathVar):
    format_feedback = "Invalid path format. Expected a valid absolute Unix path. The target path must exist. The target path must be a MultiMC instance folder and contain a .minecraft folder."

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify DirectoryAbsolutePathVar validation
        if not super()._validate(value):
            return False
        # Verify that the path contains a .minecraft folder or a minecraft folder
        if not os.path.isdir(value + "/.minecraft") and not os.path.isdir(value + "/minecraft"):
            return False
        return True

class CurseForgeInstancePathVar(DirectoryAbsolutePathVar):
    format_feedback = "Invalid path format. Expected a valid absolute Unix path. The target path must exist. The target path must be a CurseForge instance folder and contain a manifest.json file."

    # Verify that the value is a valid absolute path
    def _validate(self, value: str):
        # Verify DirectoryAbsolutePathVar validation
        if not super()._validate(value):
            return False
        # Verify that the path contains a manifest.json file
        if not os.path.isfile(value + "/manifest.json"):
            return False
        return True

class Task(ATask):
    # Setup configs list
    setup_configs = [
        CurseForgeInstancePathVar("curseforge_instance", "Path to the curseforge instance folder"),
        MultiMCInstancePathVar("mmc_instance", "Path to the MMC instance folder")
    ]

    # Run the task
    def _run(self):
        # Verify wether there is a minecraft folder or a .minecraft folder
        if os.path.isdir(self.config["mmc_instance"] + "/.minecraft"):
            mmc_minecraft_path = self.config["mmc_instance"] + "/.minecraft"
        elif os.path.isdir(self.config["mmc_instance"] + "/minecraft"):
            mmc_minecraft_path = self.config["mmc_instance"] + "/minecraft"
        else:
            raise Exception("The MultiMC instance path does not contain a .minecraft folder or a minecraft folder")

        # Verify in the configuation if the instance_includes_list is set
        if not "instance_includes_list" in self.config.keys():
            # If not, set it to the default value
            self.config["instance_includes_list"] = default_instance_includes_list
            # Save the configuration
            self.save_config()
            # Advise the user
            print("No instance includes list found in the configuration file. Set config with defaults includes. You can change it in the configuration file.")
        
        # Get the instance includes list
        instance_includes_list = self.config["instance_includes_list"]

        # Remove the included files from the MultiMC instance
        for included_file in instance_includes_list:
            # Get the path to the file
            path = mmc_minecraft_path + "/" + included_file
            # If the file is a directory
            if os.path.isdir(path):
                # Remove the directory
                FilesFunctions.remove_dir(path, included_file)
            # If the file is a file
            elif os.path.isfile(path):
                # Remove the file
                FilesFunctions.remove_file(path, included_file)

        # Copy the files from the CurseForge instance to the MultiMC instance
        for included_file in instance_includes_list:
            # Get the path to the file
            from_path = self.config["curseforge_instance"] + "/" + included_file
            to_path = mmc_minecraft_path + "/" + included_file
            # If the file is a directory
            if os.path.isdir(from_path):
                # Copy the directory
                FilesFunctions.copy_dir(from_path, to_path, included_file, included_file)
            # If the file is a file
            elif os.path.isfile(from_path):
                # Copy the file
                FilesFunctions.copy_file(from_path, to_path, included_file, included_file)
