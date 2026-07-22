from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "HDD Reallocated Sectors Check"
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
            if "Reallocated_Sector_Ct" in line:
                value = int(line.split()[-1])

                if value > 0:
                    failure_data.append((False, f"HDD Drive '{drive}' is close to failing, please replace it soon, or backup important data."))

    if len(failure_data != 0):
        return failure_data

    return True