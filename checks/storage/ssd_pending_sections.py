from checks.library.storage.helpers import get_drives
from checks.library.helpers import is_virtual_machine
import subprocess

DISPLAY_NAME = "SSD Pending Sectors"
LEVEL = 2

def check():
    if is_virtual_machine():
        return (False, "Can't get the pending sectors for your SSDs as this is a virtual machine.")

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