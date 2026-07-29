from checks.library.storage.helpers import get_drives
from datetime import timedelta, datetime
import subprocess
import uuid

CLOCK = timedelta(days=15)
TASK_ID = "c12715e1-e71f-4be8-9e1d-9053e73af258"

def task():
    # These tests will be collected by check "self-test fail"
    for drive in get_drives():
        is_short_test = datetime.now().day > 15
        test_type = "short" if is_short_test else "long"
        
        # Run a, long thorough self-test once per month
        # Run short, quick test once per month
        subprocess.run(
            ["smartctl", "-t", test_type, drive],
            stdout=subprocess.DEVNULL
        )