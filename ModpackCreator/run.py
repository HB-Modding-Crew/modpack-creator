import argparse
from . import __version__, __doc__

# Create the parser
parser = argparse.ArgumentParser(description=__doc__, prog='modpack-creator')

# Optionals arguments: tasks. -t, --tasks. List of task to execute in the corresponding order. Empty by default.
parser.add_argument('-t', '--tasks', nargs='*', default=[], help='List of tasks to execute in the corresponding order. All tasks by default.')

# Ptional argument: --setup. If you want to setup the tasks indeed of executing them. False by default.
parser.add_argument('--setup', action='store_true', help='If you want to setup the tasks instead of executing them. False by default.')

# Optionals arguments: --version. -v. Print the version and exit.
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

# Run function
def run():
    # Parse the arguments
    args = parser.parse_args()
    # Temporary
    print('Hello world!')
    exit(0)
    # TODO: Get tasks (task handling) (task in list or all tasks if list is empty)
    # If setup argument is passed
    if args.setup:
        # TODO: Setup the tasks
        pass
    # If setup argument is not passed
    else:
        # TODO: Run the tasks
        pass
