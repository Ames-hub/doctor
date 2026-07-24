from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Service startup performance"
LEVEL = 4

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

    slow_startups = not len(slow_services) == 0
    if slow_startups:
        return (False, "Systemd services are taking a while to start up. Recommend investigation.")
    else:
        return True