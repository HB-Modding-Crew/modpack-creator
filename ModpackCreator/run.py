import argparse
from . import __version__, __doc__
import importlib
from typing import Dict, Type
from .ATask import ATask

# Create the parser
parser = argparse.ArgumentParser(description=__doc__, prog='modpack-creator')

# Optionals arguments: tasks. -t, --tasks. List of task to execute in the corresponding order. Empty by default.
parser.add_argument('-t', '--tasks', nargs='*', default=[], help='List of tasks in the corresponding order. All tasks by default.')

# Ptional argument: --setup. If you want to setup the tasks indeed of executing them. False by default.
parser.add_argument('--setup', action='store_true', help='If you want to setup the tasks instead of executing them. False by default.')

# Optionals arguments: --version. -v. Print the version and exit.
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

# Optionals argument: --help. -h. Print the help and exit.
#parser.add_argument('-h', '--help', action='help', help='Print the help and exit.')


# Built-in tasks names
builtins_tasks_names = [
    "CurseForgeToMultiMC",
]

# Task map
tasks_map: Dict[str, ATask] = {}

def import_all_tasks():
    for task_name in builtins_tasks_names:
        module = importlib.import_module(f"ModpackCreator.BuiltInTasks.{task_name}")
        print(f"Imported {task_name}")
        tasks_map[task_name] = module.Task

# Run function
def run():
    # Parse the arguments
    args = parser.parse_args()
    # Temporary
    # print('Hello world!')
    # exit(0)
    # Import all tasks
    import_all_tasks()
    # If tasks argument is passed
    if not args.tasks:
        if not args.setup:
            print("You can't execute all tasks at once. Use --setup to setup all tasks, or pass the tasks you want to execute with -t")
        tasks = args.tasks
    # If tasks argument is not passed
    else:
        tasks = tasks_map.keys()
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
