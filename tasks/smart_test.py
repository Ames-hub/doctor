from checks.library.storage.helpers import get_drives
from datetime import timedelta, datetime
import subprocess
import uuid

CLOCK = timedelta(days=15)
UUID = str(uuid.uuid4())

def check():
    # These tests will be collected by check "self-test fail"
    for drive in get_drives():
        if datetime.now().day > 15:
            # Run a, long thorough self-test once per month
            subprocess.run(
                ["smartctl", "-t", "long", drive]
            )
        else:
            # Run short, quick test once per month
            subprocess.run(
                ["smartctl", "-t", "short", drive]
            )