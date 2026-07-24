from checks.library.storage.helpers import get_drives
from checks.library.helpers import is_virtual_machine
import subprocess

DISPLAY_NAME = "Drive Low-Life Alert"
LEVEL = 1

def check():
    """
    Checks for low SSD Health
    """
    # Now. Funny story. Writing this check is what got me to realise my boot SSD has 11% life left.
    # This is why I am writing doctor, nothing warned me of this!

    if is_virtual_machine():
        return (False, "Can't get the Drive's SMART data as this is a virtual machine.")

    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-A", drive],
            capture_output=True,
            text=True
        )

        life_left = None

        for line in result.stdout.splitlines():
            if "Percent_Lifetime_Remain" in line:
                life_left = int(line.split()[-1])
                break

        if life_left is None:
            # This should not happen if the script is running as root.
            return (False, f"We cannot detect the life left for {drive}, as we are not running as root.")

        is_degraded = life_left <= 10
        if is_degraded:
            failure_data.append((False, f"The drive {drive} is very worn out with {life_left}% life remaining, please replace it soon."))
    
    if not failure_data:
        return True
    else:
        return failure_data