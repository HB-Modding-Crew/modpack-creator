import argparse
from . import __version__, __doc__
import importlib
from typing import Dict
from .ATask import ATask

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


# Built-in tasks names
builtins_tasks_names = [
    "CurseForgeToMultiMC",
    "BuildMMCPackFromExport",
    "BuildCurseforgePackFromExport",
]

# Task map
tasks_map: Dict[str, ATask] = {}

def import_all_tasks():
    for task_name in builtins_tasks_names:
        module = importlib.import_module(f"ModpackCreator.BuiltInTasks.{task_name}")
        tasks_map[task_name] = module.Task

def list_all_tasks():
    import_all_tasks()
    print("Built-in tasks:")
    for task_name in tasks_map.keys():
        task: ATask = tasks_map[task_name]()
        print(f"  {task_name}")

# Run function
def run():
    # Parse the arguments
    args = parser.parse_args()
    # Import all tasks
    import_all_tasks()
    # If list-tasks argument is passed
    if args.list_tasks:
        list_all_tasks()
        exit(0)
    # If no tasks argument is passed (list is empty)
    if len(args.tasks) == 0:
        if not args.setup:
            print("You can't execute all tasks at once. Use --setup to setup all tasks, or pass the tasks you want to execute with -t")
            exit(1)
        tasks = tasks_map.keys()
    # If tasks argument is not passed
    else:
        tasks = args.tasks
    # If setup argument is passed
    if args.setup:
        # Setup the tasks
        for task in tasks:
            print(f"Setting up {task}")
            task: ATask = tasks_map[task]()
            # Print type
            task.setup()
        pass
    # If setup argument is not passed
    else:
        # Execute the tasks
        for task in tasks:
            print(f"Executing {task}")
            task: ATask = tasks_map[task]()
            task.run()
