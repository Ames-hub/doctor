import subprocess

DISPLAY_NAME = "Unexpected shutdown check"
LEVEL = 1

def check():
    """
    Checks if the last shutdown was clean.
    Returns True if intentional, False if crash/power loss.
    """

    result = subprocess.run(["last", "-x"], capture_output=True, text=True)
    logs = result.stdout.lower()

    if "shutdown" in logs:
        return True

    return (False, "Last power-off was not expected.")