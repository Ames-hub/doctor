from library.settings import settings
from library import errors
import subprocess
import logging
import shutil
import glob
import sys
import os

def translate_report(report: dict):
    """
    Takes the raw return data from a doctor.diagnose() call, and translates it into something useable for a user alert. 
    """
    translation = {}
    for item in report.items():
        item: tuple[str, bool|tuple]

        check_name = item[0]
        value = item[1]

        if check_name == "pc_uuid4":
            continue  # that's an identifier for HUB mode, not a check. Ignore it.

        if value is True:
            # Check passed, skip.
            continue

        if isinstance(value, list):
            # It failed, and returned multiple values
            translation[check_name] = []
            for result in value:
                passed = result[0]
                detail = result[1]
                if not passed:
                    translation[check_name].append(detail)
                else:
                    logging.warning(f"'{check_name}' returned a tuple when the check had successfully passed, this is not standard behavior.")
        elif isinstance(value, tuple):
            # It failed, and returned one detail.
            translation[check_name] = value
        elif isinstance(value, bool):
            translation[check_name] = value
        else:
            # Not tuple or bool
            logging.warning(f"'{check_name}' returned neither a boolean or a list of tuple in its result! Got `{value}`")
            continue

    return translation

def find_dbus_socket():
    """
    Find the graphical user's D-Bus session.
    Systemd services run outside the user's desktop session, so we have to locate it.
    """
    try:
        # Find logged in users
        result = subprocess.run(
            ["loginctl", "list-users", "--no-legend"],
            capture_output=True,
            text=True,
            check=True
        )

        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue

            uid = parts[0]
            username = parts[1]

            # Ignore root
            if username == "root":
                continue

            socket_path = f"/run/user/{uid}/bus"

            if os.path.exists(socket_path):
                dbus_addr = f"unix:path={socket_path}"
                logging.info(
                    f"Found desktop user '{username}' DBus socket: {dbus_addr}"
                )
                return dbus_addr, username

    except Exception:
        logging.exception("Failed finding graphical user's DBus session")

    logging.warning("Could not find DBus session address")
    return None, None

def _gui_alert(report: dict):
    dbus_addr, original_user = find_dbus_socket()

    if not original_user:
        logging.warning("No graphical user session found, cannot send notification")
        return
    
    # Systemd does not inherit DISPLAY, assume first X session
    display = os.environ.get("DISPLAY") or ":0"
    
    for check_disp_name in report:
        logging.info(f"Sending notification: {check_disp_name}")

        check_warn_msg = f"'{check_disp_name}' check failed!"
        if type(report[check_disp_name]) is list:
            check_warn_msg += "\n"
            problems = report[check_disp_name]
            for problem in problems:
                check_warn_msg += f"{problem}\n"
        elif type(report[check_disp_name]) is tuple:
            check_warn_msg += "\n"
            check_warn_msg += report[check_disp_name][1]  # Include the detail at the end
        
        # Build command with explicit environment
        cmd = [
            'runuser', '-u', original_user,
            '--',
            'env',
            f'DISPLAY={display}',
            f'DBUS_SESSION_BUS_ADDRESS={dbus_addr}' if dbus_addr else '',
            'notify-send', '-u', 'critical', "Doctor's Report", check_warn_msg
        ]
        # Remove empty strings from cmd
        cmd = [arg for arg in cmd if arg]
        
        try:
            if "--debug" not in sys.argv:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logging.info(f"Notification for check '{check_disp_name}' sent successfully")
        except subprocess.CalledProcessError as err:
            logging.error(f"Notification failed with exit code {err.returncode}, using fallback", exc_info=err)
            logging.error(f"stderr: {err.stderr}")
            logging.error(f"stdout: {err.stdout}")
            
            # Fallback: try without DBUS_SESSION_BUS_ADDRESS
            try:
                fallback_cmd = [
                    'runuser', '-u', original_user,
                    '--',
                    'env',
                    f'DISPLAY={display}',
                    'notify-send', '-u', 'critical', "Doctor's Report", check_warn_msg
                ]
                subprocess.run(fallback_cmd, check=False, capture_output=True)
            except Exception as err:
                logging.error("Fallback notification also failed", exc_info=err)

async def send_alert(report: dict):
    """
    Sends alerts to the user's OS in a form of pop-up notifications.
    """
    if not settings.unattended().get():
        if shutil.which("notify-send") is None:
            raise errors.missing_notifysend
        else:
            _gui_alert(report)
    else:
        raise NotImplementedError("HUB mode still needs to be implemented.")
        