from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Service startup performance"
LEVEL = 3

def check():
    """
    Checks if services are taking unusually long to start.
    """

    if shutil.which("systemd") is None:
        raise errors.missing_systemd

    result = subprocess.run(
        [
            "systemd-analyze",
            "blame"
        ],
        capture_output=True,
        text=True
    )

    lines = result.stdout.splitlines()

    slow_services = []

    for line in lines:
        try:
            time = line.split()[0]

            if "min" in time:
                slow_services.append(line)

            elif "s" in time:
                seconds = float(time.replace("s", ""))

                if seconds > 10:
                    slow_services.append(line)

        except:
            continue

    return len(slow_services) == 0