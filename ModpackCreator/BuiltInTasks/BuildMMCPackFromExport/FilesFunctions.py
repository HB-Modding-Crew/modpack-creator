import os
import shutil
import zipfile

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
    if os.path.isfile(from_path):
        shutil.copy2(from_path, to_path)
        print("Copied " + from_desc + " to " + to_desc)
    else:
        print("Skipped " + from_desc + " copying to " + to_desc + ", didn't exist")

def zip_contains_file(zip_path, file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return file_name in zip_ref.namelist()

def zip_contains_dir(zip_path, dir_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.startswith(dir_name):
                return True
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