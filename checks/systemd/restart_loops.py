from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Service restart loops"
LEVEL = 2

def check():
    """
    Checks for services repeatedly restarting.
    """

    if shutil.which("systemctl") is None:
        raise errors.missing_systemctl

    result = subprocess.run(
        [
            "systemctl",
            "--type=service",
            "--state=activating",
            "--no-legend"
        ],
        capture_output=True,
        text=True
    )

    services = result.stdout.lower()

    # Services stuck activating often indicate restart loops
    if services.strip():
        return (False, "Services are repeatedly restarting over and over. Recommend investigation.")

    return True