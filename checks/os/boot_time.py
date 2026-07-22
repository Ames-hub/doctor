from datetime import datetime, timedelta
import subprocess

uptime_threshold = 90  # Days

DISPLAY_NAME = "Extended-session check"
LEVEL = 2

def check():
    """
    Checks if the system has been running for more than 90 days.
    """
    boot_time = int(subprocess.run(["awk","'/btime/", "{print $2}'", "/proc/stat"], capture_output=True, text=True))
    boot_time = datetime.fromtimestamp(boot_time)

    if boot_time - datetime.now() >= timedelta(days=90):
        return False
    else:
        return True