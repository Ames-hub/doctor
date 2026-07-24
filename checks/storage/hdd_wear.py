from checks.library.storage.helpers import get_drives, is_hdd
import subprocess

DISPLAY_NAME = "HDD Reallocated Sectors Check"
LEVEL = 1

def check():
    failure_data = []
    for drive in get_drives():
        # Skip non-HDD drives
        if not is_hdd(drive):
            continue
            
        result = subprocess.run(
            ["smartctl", "-A", drive],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if "Reallocated_Sector_Ct" in line:
                value = int(line.split()[-1])

                if value > 100:
                    failure_data.append((False, f"HDD Drive '{drive}' has a lot of bad sectors, please replace it soon, or backup important data."))

    if len(failure_data) != 0:
        return failure_data

    return True