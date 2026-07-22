from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Service failures"
LEVEL = 2

def check():
    """
    Checks if services have recently failed or crashed.
    """

    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    result = subprocess.run(
        [
            "journalctl",
            "-p",
            "err"
            "--since",
            "30 days ago",
            "--no-pager",
        ],
        capture_output=True,
        text=True
    )

    logs = result.stdout.lower()

    failures = [
        "failed with result",
        "main process exited",
        "entered failed state",
        "dependency failed"
    ]

    for failure in failures:
        if failure in logs:
            return False

    return True