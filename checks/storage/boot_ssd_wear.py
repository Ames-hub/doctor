from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "SSD Wear-out"
LEVEL = 1

def check():
    """
    Checks SSD remaining lifespan.
    """

    failure_data = []
    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-a", drive],
            capture_output=True,
            text=True
        )

        output = result.stdout.lower()

        for line in output.splitlines():
            if "percentage used" in line:
                used = int(line.split()[-1])
                worn_out = used <= 90
                if worn_out:
                    failure_data.append(worn_out, f"Drive {drive} is currently 90% worn out, consider replacing soon.")

    return True