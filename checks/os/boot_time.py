from datetime import datetime, timedelta
from library import errors
import subprocess
import shutil

uptime_threshold = 90  # Days

DISPLAY_NAME = "Extended-session check"
LEVEL = 2

def check():
    """
    Checks if the system has been running for more than 90 days.
    """
    if shutil.which("awk") is None:
        raise errors.missing_other_component("awk")

    result = subprocess.run(
        ["awk", "/btime/ {print $2}", "/proc/stat"],
        capture_output=True,
        text=True
    )

    boot_time = result.stdout.strip()

    if not boot_time:
        raise errors.unavailable_sys_info

    boot_time = datetime.fromtimestamp(int(boot_time))

    if boot_time - datetime.now() >= timedelta(days=90):
        return (False, "The system has been online for too long, recommend a full restart.")
    else:
        return True