from checks.library.storage.helpers import get_drives
import subprocess

DISPLAY_NAME = "Drive temperature"
MAX_TEMP = 45
LEVEL = 2

TEMP_FIELDS = [
    "Temperature_Celsius",
    "Airflow_Temperature_Cel",
    "Temperature_Internal"
]

def check():
    # Note: This check can misbehave if the drive is measuring in fahrenheit.
    failure_data = []

    for drive in get_drives():
        result = subprocess.run(
            ["smartctl", "-A", drive],
            capture_output=True,
            text=True
        )

        for line in result.stdout.splitlines():
            if any(field in line for field in TEMP_FIELDS):
                try:
                    temp = int(line.split()[-1])
                except (ValueError, IndexError):
                    continue

                if temp >= MAX_TEMP:
                    failure_data.append(
                        (False, f"Drive {drive} is {temp}°C, which is too hot! Consider additional cooling, or removing a side panel for extra air flow.")
                    )

    if not failure_data:
        return True

    return failure_data