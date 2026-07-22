from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "Boot Drive Life Alert"
LEVEL = 1

def check():
    """
    Checks for predicted drive failure using our own metrics. 
    """    
    # Now. Funny story. Writing this check is what got me to realise my boot SSD has 11% life left.
    # This is why I am writing doctor, nothing warned me of this!
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

        is_degraded = life_left >= 10
        if is_degraded:
            failure_data.append(False, f"The drive {drive} is very worn out, please replace it soon.")
    
    if not failure_data:
        return True
    else:
        return failure_data