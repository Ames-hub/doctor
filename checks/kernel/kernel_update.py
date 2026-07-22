import subprocess

DISPLAY_NAME = "Kernel update available"
LEVEL = 3

def check():
    """
    Checks if a newer kernel package is available.
    """

    subprocess.run(
        ["apt", "update"],
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["apt", "list", "--upgradable"],
        capture_output=True,
        text=True
    )

    if "linux-image" in result.stdout.lower():
        return False

    return True