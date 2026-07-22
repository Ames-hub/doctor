import subprocess

DISPLAY_NAME = "Failed cron jobs"
LEVEL = 2

def check():
    """
    Checks cron logs for failed jobs.
    """

    result = subprocess.run(
        [
            "journalctl",
            "-u",
            "cron",
            "--since",
            "30 days ago",
            "--no-pager"
        ],
        capture_output=True,
        text=True
    )

    logs = result.stdout.lower()

    failures = [
        "error",
        "failed",
        "exit status",
        "returned"
    ]

    for failure in failures:
        if failure in logs:
            return False

    return True