from typing import List
import json

from ModpackCreator.const import CONFIG_PATH

class AVarDef:
    # Name of the variable. Should be overriden by subclasses. Should be set on init.
    name = "AVarDef"
    # Description of the variable. Should be overriden by subclasses.
    description = "Abstract variable definition. It should be overriden by subclasses."
    # Format, or type explication of the variable. Displayed if the variable is invalid. Should be overriden by subclasses. Not mandatory.
    format_feedback = "Please enter a valid value."
    # Default value of the variable. Not mandatory. Should be overriden by subclasses.
    default = None
    # Type of the variable. Should be overriden by subclasses.
    type = str

    # Init
    def __init__(self, name: str, description: str, default = None):
        self.name = name
        self.description = description
        self.default = default

    # Validate the value of the variable. Should be overriden by the subclasses.
    def _validate(self, value):
        raise NotImplementedError()

    # Prompt the value of the variable. Should not be overriden by subclasses.
    def setup_value(self):
        # Final value
        final_value = None
        # Open the config file as json
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        # If the config is not in the config file
        while final_value is None:
            if self.name not in config.keys():
                # If the config has a default value
                if self.default is not None:
                    # Input with default value prompt
                    value = input(f"{self.name}: {self.description} [{self.default}]: ")
                    # If the value is empty
                    if value.strip() == "":
                        # Set the value to the default value
                        value = self.default
                        print(f"Using default value: {value}")
                # If the config has no default value
                else:
                    # Input prompt
                    value = input(f"{self.name}: {self.description}: ")
                # Verify the type
                if not isinstance(value, self.type):
                    print(f"Invalid type. Expected {self.type}.")
                    continue
                # Validate the value
                if self._validate(value):
                    # Set the final value to the value
                    final_value = value
                # If the value is invalid
                else:
                    # Print the format feedback
                    print(self.format_feedback) 
            else:
                # Explain the user that the value is already set and ask if he wants to change it
                value = input(f"{self.name} is already set to {config[self.name]}. Do you want to change it? [y/N]: ")
                # If the user don't want to change it
                if value.strip().lower() == "n" or value.strip().lower() == "no":
                    final_value = config[self.name]
                    break
                elif value.strip().lower() == "y" or value.strip().lower() == "yes":
                    # If the config has a default value
                    if self.default is not None:
                        # Input with default value prompt
                        value = input(f"{self.name}: {self.description} [{self.default}]: ")
                        # If the value is empty
                        if value.strip() == "":
                            # Set the value to the default value
                            value = self.default
                            print(f"Using default value: {value}")
                    # If the config has no default value
                    else:
                        # Input prompt
                        value = input(f"{self.name}: {self.description}: ")
                    # Verify the type
                    if not isinstance(value, self.type):
                        print(f"Invalid type. Expected {self.type}.")
                        continue
                    # Validate the value
                    if self._validate(value):
                        # Set the final value to the value
                        final_value = value
                    # If the value is invalid
                    else:
                        # Explain the user the format
                        print(self.format_feedback)
        # Set the value in the config file
        config[self.name] = final_value
        # Save the config file
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)



class ATask:
    # Setup configs list: should be overriden by subclasses
    setup_configs: List[AVarDef] = []

    # Public method to setup the action. Should not be overriden by subclasses.
    def setup(self):
        # Setup the config file
        for config in self.setup_configs:
            config.setup_value()

    # Private method to run the action. Should be overriden by subclasses.
    def _run(self):
        raise NotImplementedError()

    # Public method to run the action. Should not be overriden by subclasses.
    def run(self):
        # Run the action
        self._run()
            