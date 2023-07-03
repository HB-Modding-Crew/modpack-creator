import sys
import os
import shutil
import zipfile
import json
import re
import pathlib

""" CONFIG """

PATH_CONFIG = "config.json"
with open(PATH_CONFIG, "r") as f:
    CONFIG = json.load(f)

""" CONSTANTS """

# Names
REGEX_VERSION_NAME = r"((\d\.){2}\d(-(alpha|beta)\.(\d+))?)"
MODPACK_NAME = CONFIG["modpack_name"]
FORMAT_MODPACK_FILE_NAME = f"{MODPACK_NAME}-{'{}'}"

# Paths
PATH_EXPORTS = "exports"
PATH_PRISM_PREPARED_EXPORT = "temp/mmc_prepared_export.zip"
PATH_UNPACKED_PRISM_BEFORE_INCLUDE = "temp/temp_mmc_export_before_includes"
PATH_UNPACKED_PRISM_AFTER_INCLUDE = "temp/temp_mmc_export_after_includes"

# mmc-export
MMC_EXPORT_PROGRAM = "mmc-export"
MMC_EXPORT_FROMZIP = f"-i {PATH_PRISM_PREPARED_EXPORT}"
MMC_EXPORT_OUTPUT_MODRINTH = "-f Modrinth"
MMC_EXPORT_OUTPUT_PACKWIZ = "-f packwiz"
MMC_EXPORT_MODRINTH_OUTPUT_PATH = "-o ./output"
MCC_EXPORT_SEARCH_MOD = "--modrinth-search loose"
MMC_EXPORT_PACKWIZ_OUTPUT_PATH = "-o ./temp"
MMC_EXPORT_CONFIG_PATH = "-c ./Packwiz/mmc-export.toml"
MMC_EXPORT_VERSION = "-v {}"
MMC_EXPORT_MODRINTH_SCHEME = f"--scheme {MODPACK_NAME + '-{}'}"
MMC_EXPORT_PACKWIZ_SCHEME = "--scheme mmc_export_packwiz_output"
MMC_EXPORT_EXCLUDE_PROVIDERS = "--exclude-providers GitHub --exclude-providers CurseForge"
MMC_EXPORT_TO_MODRINTH_COMMAND = f"{MMC_EXPORT_PROGRAM} {MMC_EXPORT_FROMZIP} {MMC_EXPORT_OUTPUT_MODRINTH} {MCC_EXPORT_SEARCH_MOD} {MMC_EXPORT_MODRINTH_OUTPUT_PATH} {MMC_EXPORT_CONFIG_PATH} {MMC_EXPORT_VERSION} {MMC_EXPORT_MODRINTH_SCHEME} {MMC_EXPORT_EXCLUDE_PROVIDERS}"
MMC_EXPORT_TO_PACKWIZ_COMMAND = f"{MMC_EXPORT_PROGRAM} {MMC_EXPORT_FROMZIP} {MMC_EXPORT_OUTPUT_PACKWIZ} {MCC_EXPORT_SEARCH_MOD} {MMC_EXPORT_PACKWIZ_OUTPUT_PATH} {MMC_EXPORT_CONFIG_PATH} {MMC_EXPORT_VERSION} {MMC_EXPORT_PACKWIZ_SCHEME} {MMC_EXPORT_EXCLUDE_PROVIDERS}"


""" FILE UTILS """

def is_existing_zip(zip_path):
    return os.path.isfile(zip_path) and zipfile.is_zipfile(zip_path)

def remove_dir(path, description):
    if os.path.isdir(path):
        shutil.rmtree(path)
        print("Deleted " + description)
    else:
        print("Skipped " + description + " deletion, didn't exist")

def remove_file(path, description):
    if os.path.isfile(path):
        os.remove(path)
        print("Deleted " + description)
    else:
        print("Skipped " + description + " deletion, didn't exist")

def copy_dir(from_path, to_path, from_desc, to_desc):
    if os.path.isdir(from_path):
        ret = shutil.copytree(from_path, to_path, dirs_exist_ok=True)
        print("Copied " + from_desc + " to " + to_desc)
    else:
        print("Skipped " + from_desc + " copying to " + to_desc + ", didn't exist")

def copy_file(from_path, to_path, from_desc, to_desc):
    # Create the directory if it doesn't exist
    if not os.path.exists(os.path.dirname(to_path)):
        os.makedirs(os.path.dirname(to_path))
    if os.path.isfile(from_path):
        shutil.copy2(from_path, to_path)
        print("Copied " + from_desc + " to " + to_desc)
    else:
        print("Skipped " + from_desc + " copying to " + to_desc + ", didn't exist")

def zip_contains_file(zip_path, file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        if file_name in zip_ref.namelist():
            print(file_name + " in " + zip_path + " found !")
            return True
    print("No " + file_name + " in " + zip_path)

def zip_contains_dir(zip_path, dir_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.startswith(dir_name):
                print(dir_name + " in " + zip_path + " found !")
                return True
    print("No " + dir_name + " in " + zip_path)
    return False

def copy_to_zip(from_path, to_path, archive_path):

    files = []

    with zipfile.ZipFile(archive_path) as archive:
        for zipinfo in archive.infolist():
            if zipinfo.filename != to_path:
                files.append((zipinfo.filename, archive.read(zipinfo.filename)))

    with zipfile.ZipFile(archive_path, "w") as archive:
        for filename, content in files:
            archive.writestr(filename, content)
        archive.write(from_path, to_path)

def copy_from_zip(from_path, to_path, archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        with open(to_path, "wb") as file:
            file.write(archive.read(from_path))

""" PACK MAKER """

# Prism instance

class PrismInstance:

    def __init__(self, zip_path):
        # Verify that the .zip exists
        if not is_existing_zip(zip_path):
            raise Exception(f"The Prism instance zip file '{zip_path}' doesn't exist")
        # Zip path
        self.zip_path = zip_path
        # Load
        self.load()

    def create_temp_directory():
        if not os.path.exists("temp"):
            os.makedirs("temp")

    def verify_zip_validity(self):
        # Verify that the .zip contains a minecraft or .minecraft folder
        if not zip_contains_dir(self.zip_path, "minecraft") and not zip_contains_dir(self.zip_path, ".minecraft"):
            raise Exception("The Prism instance zip file doesn't contain a minecraft folder")
        # Set minecraft dir
        if zip_contains_dir(self.zip_path, "minecraft"):
            self.minecraft_dir = "minecraft"
        else:
            self.minecraft_dir = ".minecraft"
        # Get version from zip name with regex
        self.version = re.search(REGEX_VERSION_NAME, self.zip_path).group(0)
        # If version is None, raise an exception
        if self.version is None:
            raise Exception("The Prism instance zip file name doesn't contain a valid version")

    def remove_old_prepared_export(self):
        # Remove old prepared export
        if os.path.isfile(PATH_PRISM_PREPARED_EXPORT):
            os.remove(PATH_PRISM_PREPARED_EXPORT)

    def create_new_prepared_export(self):
        # Create new prepared export
        copy_file(self.zip_path, PATH_PRISM_PREPARED_EXPORT, "raw prism instance", "prepared export")

    def remove_not_included_files(self):
        # Keep only the included files
        # List of files to keep
        include_list = CONFIG["instance_includes_list"]
        # If the directory already exists, delete it
        if os.path.isdir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE):
            remove_dir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE, "old \"before include\" directory")
        # If the directory already exists, delete it
        if os.path.isdir(PATH_UNPACKED_PRISM_AFTER_INCLUDE):
            remove_dir(PATH_UNPACKED_PRISM_AFTER_INCLUDE, "old \"after include\" directory")
        # Open the zip file and copy content to temp except minecraft folder
        shutil.unpack_archive(PATH_PRISM_PREPARED_EXPORT, PATH_UNPACKED_PRISM_BEFORE_INCLUDE)
        for file in os.listdir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE):
            if file != ".minecraft" and file != "minecraft":
                if os.path.isfile(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + file):
                    copy_file(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + file, PATH_UNPACKED_PRISM_AFTER_INCLUDE + "/" + file, "included file", "prepared profile")
                if os.path.isdir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + file):
                    copy_dir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + file, PATH_UNPACKED_PRISM_AFTER_INCLUDE + "/" + file, "included file", "prepared profile")
        # Copy included content from minecraft folder
        for file in include_list:
            if os.path.isfile(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + self.minecraft_dir + "/" + file):
                copy_file(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + self.minecraft_dir + "/" + file, PATH_UNPACKED_PRISM_AFTER_INCLUDE + "/" + self.minecraft_dir + "/" + file, file, "prepared profile")
            if os.path.isdir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + self.minecraft_dir + "/" + file):
                copy_dir(PATH_UNPACKED_PRISM_BEFORE_INCLUDE + "/" + self.minecraft_dir + "/" + file, PATH_UNPACKED_PRISM_AFTER_INCLUDE + "/" + self.minecraft_dir + "/" + file, file, "prepared profile")

    def normalize_file_ending(self):
        # Normalize all end of lines with CRLF
        print("Normalizing all end of lines with CRLF")
        for root, dirs, files in os.walk(PATH_UNPACKED_PRISM_AFTER_INCLUDE):
            for file in files:
                list_of_txt_extensions = [".txt", ".json", ".toml", ".cfg", ".properties", ".lang", ".mcmeta", ".log", ".md", ".yml", ".yaml", ".json5"]
                if os.path.splitext(file)[1] in list_of_txt_extensions:
                    print("Normalizing " + file)
                    file_path = os.path.join(root, file)
                    with open(file_path, "r+") as f:
                        content = f.read()
                        content = "\r\n".join(content.splitlines())
                        f.seek(0)
                        f.truncate()
                        f.write(content)


    def load(self):
        # Verify zip validity
        self.verify_zip_validity()
        # Remove old prepared export
        self.remove_old_prepared_export()
        # Create new prepared export
        self.create_new_prepared_export()
        # Remove not included files
        self.remove_not_included_files()
        # Normalize files
        self.normalize_file_ending()
        # Finalize prepared pack
        shutil.make_archive(PATH_PRISM_PREPARED_EXPORT.split(".")[0], "zip", PATH_UNPACKED_PRISM_AFTER_INCLUDE)

    def pack_modrinth(self):
        cmd = MMC_EXPORT_TO_MODRINTH_COMMAND.format(self.get_version(), self.get_version())
        print(cmd)
        os.system(cmd)

    def pack_packwiz(self):
        cmd = MMC_EXPORT_TO_PACKWIZ_COMMAND.format(self.get_version(), self.get_version())
        print(cmd)
        os.system(cmd)

        # Unzip and put packiz output in the right directory

        # Packwiz zip path
        packwiz_zip_path = f"./temp/mmc_export_packwiz_output.zip"
        # Packwiz output path
        packwiz_output_path = pathlib.Path("./") / "Packwiz" / f"{self.get_version()}"
        # Remove old packwiz output
        if os.path.isdir(packwiz_output_path):
            remove_dir(packwiz_output_path, "Old packwiz output")
        # Create packwiz output directory
        os.mkdir(packwiz_output_path)
        # Copy packwiz zip to packwiz output
        shutil.unpack_archive(packwiz_zip_path, packwiz_output_path)
        # Remove packwiz zip
        if os.path.isfile(packwiz_zip_path):
            os.remove(packwiz_zip_path)

    """ GETTERS """

    # Get version
    def get_version(self):
        return self.version

    # Get zip path
    def get_zip_path(self):
        return self.zip_path

def run():
    zip_name = " ".join(sys.argv[1:])
    zip_name = zip_name.removeprefix("'")
    zip_name = zip_name.removesuffix("'")
    instance = PrismInstance(PATH_EXPORTS + "/" + zip_name)
    instance.pack_modrinth()
    instance.pack_packwiz()

if __name__ == '__main__':
    run()

        
