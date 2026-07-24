from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Boot Errors Check"
LEVEL = 1

def check():
    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    errors = str(subprocess.run(["journalctl", "-b", "-p", "err", "--no-pager"], capture_output=True, text=True)).splitlines()
    if not len(errors) == 0:
        return (False, "There were problems during bootup, recommend investigation using `journalctl -b -p err`.")
    else:
        return True