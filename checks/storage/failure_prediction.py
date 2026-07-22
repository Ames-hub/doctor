from checks.library.storage.life_prediction import drive as drv
from checks.library.storage.helpers import get_drives
import subprocess
from datetime import datetime

DISPLAY_NAME = "Boot Drive Failure Prediction"
LEVEL = 2

def check():
    """
    Checks for predicted drive failure using our own metrics. 
    """    
    # Now. Funny story. Writing this check is what got me to realise my boot SSD has 11% life left.
    # This is why I am writing doctor, nothing warned me of this!
    failure_data = []
    for drive_name in get_drives():
        drive = drv(drive_name)

        data = drive.get_current_life()
        last_record_date = datetime.fromtimestamp(data.timestamp)
        if last_record_date.strftime("%d-%m-%Y") == datetime.now().strftime("%d-%m-%Y"):
            # If a record was already taken today, skip
            return True

        result = subprocess.run(
            ["smartctl", "-A", "/dev/sda"],
            capture_output=True,
            text=True
        )

        life_left = None

        # Gets the line that reads out the lifetime remaining
        for line in result.stdout.splitlines():
            if "Percent_Lifetime_Remain" in line:
                life_left = int(line.split()[-1])
                break

        drive.save_current_life(life_left)
        days_left = drive.predict_life()

        if days_left <= 90:
            failure_data.append((False, f"It is predicted that drive {drive.drive_id} will fail in {days_left} days, we recommend replacement."))

    if not failure_data:
        return True

    return failure_data