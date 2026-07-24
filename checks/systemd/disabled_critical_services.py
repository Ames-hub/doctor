from library.settings import settings
from library import errors
import subprocess
import shutil

DISPLAY_NAME = "Disabled critical services"
LEVEL = 1

def check():
    """
    Checks that important system services are enabled.
    """

    if shutil.which("systemctl") is None:
        raise errors.missing_systemctl

    critical_services = [
        "systemd-journald",
        "systemd-logind",
        "NetworkManager",
    ]

    extra_crit_services = settings.extra_critical_services().get()
    critical_services.extend(extra_crit_services)

    problems = []
    for service in critical_services:
        result = subprocess.run(
            [
                "systemctl",
                "is-enabled",
                service
            ],
            capture_output=True,
            text=True
        )

        if result.stdout.strip() not in ["enabled", "static"]:
            problems.append((False, f"Critical system service \"{service}\" is not running!"))

    if problems:
        return problems

    return True