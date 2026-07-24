from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Kernel panic/oops history"
LEVEL = 4  

def check():
    """
    Checks the last 30 days for kernel crashes.
    """

    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    result = subprocess.run(
        [
            "journalctl",
            "-k",
            "--since",
            "30 days ago",
            "--no-pager"
        ],
        capture_output=True,
        text=True
    )

    logs = result.stdout.lower()

    failures = [
        "kernel panic",
        "not syncing",
        "kernel bug",
        "oops",
        "fatal exception"
    ]

    for failure in failures:
        if failure in logs:
            return False

    return True