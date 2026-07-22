from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "SSD Pending Sectors"
LEVEL = 2

def check():
    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-A", drive],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "Current_Pending_Sector" in line:
                value = int(line.split()[-1])
                if value != 0:
                    failure_data.append(False, f"Drive {drive} currently has pending sectors, please investigate.")

    if failure_data:
        return failure_data

    return True