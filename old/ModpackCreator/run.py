import argparse
from . import __version__, __doc__
import importlib
from typing import Dict
from .ATask import ATask

from typing import List
import os
import pkgutil
import sys

import ModpackCreator

# Insert the current directory in the path
sys.path.insert(0, os.getcwd())

# Create the parser
parser = argparse.ArgumentParser(description=__doc__, prog='modpack-creator')

# Optional argument: --version. -v. Print the version and exit.
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

# Optional argument: --list-tasks. -l. List all tasks and exit.
parser.add_argument('-l', '--list-tasks', action='store_true', help='List all tasks and exit.')

# Optionals arguments: tasks. -t, --tasks. Each use of this argument will add a task to the list of tasks to execute. If no tasks are passed, list is empty, all tasks will be executed.
parser.add_argument('-t', '--tasks', action='append', help='Each use of this argument will add a task to the list of tasks to execute. All tasks selectioned if no tasks are passed.')

# Optional argument: --setup. If you want to setup the tasks indeed of executing them. False by default.
parser.add_argument('--setup', action='store_true', help='If you want to setup the tasks instead of executing them. False by default.')

def import_all_tasks_in_directory(dir_path: str) -> Dict[str, ATask]:
    # tasksmap: Dict[str, ATask] = {}
    tasks_map: Dict[str, ATask] = {}
    # Verify that the directory exists
    if not os.path.isdir(dir_path):
        raise Exception(f"Directory {dir_path} does not exist")
    # Get the list of directories in the directory
    dirs = os.listdir(dir_path)
    # For each directory
    for dir in dirs:
        # If the directory is a python module and is not nammed common
        if os.path.isdir(dir_path + "/" + dir) and dir != "common":
            # Import the module
            module = importlib.import_module(f"{dir_path}.{dir}", package='')
            # Add the module to the list of modules
            tasks_map[dir] = module.task.Task
    return tasks_map

# Task map

def import_all_built_in_tasks() -> Dict[str, ATask]:
    builtin_tasks_map: Dict[str, ATask] = {}
    builtins_tasks = pkgutil.iter_modules(ModpackCreator.BuiltInTasks.__path__)
    for task in builtins_tasks:
        if task.name != "common":
            builtin_tasks_map[task.name] = importlib.import_module(f"ModpackCreator.BuiltInTasks.{task.name}").task.Task
    return builtin_tasks_map

def list_all_tasks(builtin_tasks_map: Dict[str, ATask], added_tasks_map: Dict[str, ATask]):
    print("Built-in tasks:")
    for task_name in builtin_tasks_map.keys():
        print(f"  {task_name}")
    print("Added tasks:")
    for task_name in added_tasks_map.keys():
        print(f"  {task_name}")

# Run function
def run():
    # Parse the arguments
    args = parser.parse_args()
    # Import all tasks
    builtin_tasks_map = import_all_built_in_tasks()
    added_tasks_map = import_all_tasks_in_directory("tasks")
    # If list-tasks argument is passed
    if args.list_tasks:
        list_all_tasks(builtin_tasks_map=builtin_tasks_map, added_tasks_map=added_tasks_map)
        exit(0)
    # If no tasks argument is passed (list is empty)
    if len(args.tasks) == 0:
        if not args.setup:
            print("You can't execute all tasks at once. Use --setup to setup all tasks, or pass the tasks you want to execute with -t")
            exit(1)
        tasks = builtin_tasks_map.keys()
    # If tasks argument is not passed
    else:
        tasks = args.tasks
    # If setup argument is passed
    if args.setup:
        # Setup the tasks
        for task in tasks:
            print(f"Setting up {task}")
            task: ATask = builtin_tasks_map[task]()
            # Print type
            task.setup()
        pass
    # If setup argument is not passed
    else:
        # Execute the tasks
        for task in tasks:
            print(f"Executing {task}")
            if task in builtin_tasks_map and not task in added_tasks_map:
                print(f"Task {task} is a built-in task")
                task: ATask = builtin_tasks_map[task]()
                task.run()
            elif task in added_tasks_map:
                print(f"Task {task} is an added task")
                task: ATask = added_tasks_map[task]()
                task.run()
            else:
                print(f"Task {task} does not exist")
                exit(1)

# If this file is executed
if __name__ == "__main__":
    # Run the program
    run()
