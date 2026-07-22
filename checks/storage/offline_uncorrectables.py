from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "Offline uncorrectable sectors"
LEVEL = 1

def check():
    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-A", drive],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "Offline_Uncorrectable" in line:
                value = int(line.split()[-1])
                if value > 0:
                    failure_data.append(False, f"The amount offline, uncorrectable sectors in {drive} is not 0. Please investigate, or replace drive.")

    if failure_data:
        return failure_data

    return True