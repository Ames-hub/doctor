from library.doctor import get_pkg_manager
import subprocess
import re

DISPLAY_NAME = "Kernel update available"
LEVEL = 3

def check():
    """
    Checks whether a newer kernel package is available.
    Supports Ubuntu/Debian (APT) and Fedora (DNF).

    Returns:
        True: No kernel updates available.
        False: A kernel update is available.
    """

    package_manager = get_pkg_manager()

    # Refresh package repositories
    if package_manager == "apt":
        update = subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            text=True
        )

        if update.returncode != 0:
            raise RuntimeError(f"Failed to refresh APT repositories: {update.stderr}")

        result = subprocess.run(
            ["apt", "list", "--upgradable"],
            capture_output=True,
            text=True
        )

        # Ubuntu/Debian kernel package names
        kernel_pattern = re.compile(
            r"^linux-(image|generic|modules)(?:[-:]|/)",
            re.IGNORECASE
        )

    else:
        result = subprocess.run(
            ["dnf", "check-update", "--refresh"],
            capture_output=True,
            text=True
        )

        # DNF returns 100 when updates are available
        if result.returncode not in (0, 100):
            raise RuntimeError(f"Failed to check DNF updates: {result.stderr}")

        # Fedora kernel package names
        kernel_pattern = re.compile(
            r"^kernel(?:[-.]|$)",
            re.IGNORECASE
        )

    # Check available updates
    for line in result.stdout.splitlines():
        package = line.strip().split()[0] if line.strip() else ""

        if kernel_pattern.match(package):
            return False

    return True