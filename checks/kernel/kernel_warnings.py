from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Kernel warnings check"
LEVEL = 4  # Its rare a kernel warning will be of concern to the user.

def check():
    """
    Checks the current boot for kernel warnings.
    """

    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    result = subprocess.run(
        ["journalctl", "-k", "-b", "--no-pager"],
        capture_output=True,
        text=True
    )

    logs = result.stdout.lower()

    warnings = [
        "warning",
        "failed",
        "error",
        "timeout"
    ]

    for warning in warnings:
        if warning in logs:
            return False

    return True