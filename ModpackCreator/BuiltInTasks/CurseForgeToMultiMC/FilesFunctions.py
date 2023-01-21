import os
import shutil

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