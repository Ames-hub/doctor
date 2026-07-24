from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Failed Systemd Unit Startups"
LEVEL = 2  # If we got far enough to run this check, its probably not that bad

def check():
    """
    Checks if systemd has any failed units.
    Returns True if healthy, False if any units failed.
    """
    if shutil.which("systemctl") is None:
        raise errors.missing_systemctl
    result = subprocess.run(["systemctl", "--failed", "--no-legend"], capture_output=True, text=True)
    failed_units = result.stdout.strip().splitlines()

    units_have_failed = not len(failed_units) == 0
    if units_have_failed:
        return (False, "Systemctl services have failed. Please investigate.")