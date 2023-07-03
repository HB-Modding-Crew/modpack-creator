import re

# Input new version
new_version = input("New version: ")

# Change version in pyproject.toml
with open("pyproject.toml", "r+") as f:
    pyproject = f.read()
    pyproject = re.sub(r"version = \"\d+\.\d+\.\d+\"", f"version = \"{new_version}\"", pyproject)
    f.seek(0)
    f.truncate()
    f.write(pyproject)

# Change version in __init__.py
with open("ModpackCreator/__init__.py", "r+") as i:
    init = i.read()
    init = re.sub(r"__version__ = \'\d+\.\d+\.\d+\'", f"__version__ = \'{new_version}\'", init)
    i.seek(0)
    i.truncate()
    i.write(init)