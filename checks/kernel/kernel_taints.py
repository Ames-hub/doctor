import subprocess

DISPLAY_NAME = "Kernel taint check"
LEVEL = 4

def check():
    """
    Checks if the kernel is currently tainted.
    """

    result = subprocess.run(
        ["cat", "/proc/sys/kernel/tainted"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False

    taint = int(result.stdout.strip())

    # 0 = clean kernel
    if taint == 0:
        return True

    return False