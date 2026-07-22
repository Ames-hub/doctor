import subprocess

DISPLAY_NAME = "Unexpected shutdown check"
LEVEL = 1

def check():
    """
    Checks if the last shutdown was clean.
    Returns True if intentional, False if crash/power loss.
    """

    logs = str(subprocess.run(["last", "-x"], capture_output=True, text=True)).lower()

    if "shutdown" in logs:
        return True

    return False