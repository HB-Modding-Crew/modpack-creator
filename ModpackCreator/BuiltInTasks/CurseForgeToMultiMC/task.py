from ModpackCreator.ATask import ATask
from ModpackCreator.SetupVarTypes.PathVar import DirectoryAbsolutePathVar 

class Task(ATask):
    


    # Setup configs list
    setup_configs = [
        DirectoryAbsolutePathVar("curseforge_instance", "Path to the curseforge instance folder"),
        DirectoryAbsolutePathVar("mmc_instance", "Path to the MMC instance folder")
    ]

    # Run the task
    def _run(self):
        print("Hello world!")
