from ModpackCreator.ATask import ATask
from ModpackCreator.SetupVarTypes.PathVar import DirectoryRelativeToPathVar 

class Task(ATask):
    


    # Setup configs list
    configs = [
        DirectoryRelativeToPathVar("curseforge_instance", "Path to the curseforge instance folder"),
        DirectoryRelativeToPathVar("mmc_instance", "Path to the MMC instance folder")
    ]

    # Run the task
    def _run(self):
        print("Hello world!")
        