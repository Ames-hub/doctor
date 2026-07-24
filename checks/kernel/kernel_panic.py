from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Kernel panic check"
LEVEL = 1  # This checks if the last boot was for a kernel panic.

def check():
    """
    Checks if the previous boot ended due to a kernel panic.
    Returns True if no kernel panic was found, False if detected.
    """

    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    logs = subprocess.run(["journalctl", "-b", "-1", "-k", "--no-pager"], capture_output=True, text=True).stdout.lower()

    panic_indicators = [
        "kernel panic",
        "panic occurred",
        "not syncing",
        "fatal exception",
        "kernel BUG",
    ]

    for indicator in panic_indicators:
        if indicator in logs:
            return False

    return True