from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Failed system services"
LEVEL = 3

def check():
    """
    Checks if systemd has failed services.
    """

    if shutil.which("systemctl") is None:
        raise errors.missing_systemctl

    result = subprocess.run(
        ["systemctl", "--failed", "--no-legend"],
        capture_output=True,
        text=True
    )

    failed = result.stdout.strip()
    has_failed = not failed == ""

    if has_failed:
        return (False, "Systemd services have recently failed. Recommend investigation.")