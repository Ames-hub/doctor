from checks.library.storage.helpers import get_drives
import subprocess
import logging
import os

DISPLAY_NAME = "Drive self-test fail"
LEVEL = 1

def check():
    """
    Returns (healthy, message)
    healthy=True means no failed SMART self-tests detected.
    """

    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-l", "selftest", drive],
            capture_output=True,
            text=True
        )

        if result.returncode == 2:  #  Permission denied. Not sudo.
            logging.info(f"Check '{DISPLAY_NAME}' was not run as root, cannot proceed. Check auto-fail.")
            if os.geteuid() != 0:
                return (False, "Cannot check any drives self-test status, as we are not running as root.")
            else:
                return (False, "Cannot check any drives self-test status, the reason for this is unknown, but may be permissions related.")
        elif result.returncode != 0:
            continue  # maybe doesn't have a self-test

        for line in result.stdout.splitlines():
            line = line.strip().lower()

            if "completed" in line:
                if any(failure in line for failure in [
                        "failure",
                        "aborted",
                        "unknown",
                        "fatal",
                        "interrupted"
                    ]):
                    failure_data.append(False, f"SMART self-test failure detected on {drive}. Recommend a replacement drive soon.")

    if failure_data:
        return failure_data

    return True
    