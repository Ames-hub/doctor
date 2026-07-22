from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "Drive self-test fail"
LEVEL = 1

def check():
    """
    Returns (healthy, message)
    healthy=True means no failed SMART self-tests detected.
    """

    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-l", "selftest", drive],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            continue  # maybe doesn't have a self-test

        for line in result.stdout.splitlines():
            line_original = line.strip()
            line = line.strip().lower()

            if "completed" in line:
                if any(failure in line for failure in [
                        "failure",
                        "aborted",
                        "unknown",
                        "fatal",
                        "interrupted"
                    ]):
                    failure_data.append(False, f"SMART self-test failure detected on {drive}")

        if failure_data:
            return failure_data

        return True