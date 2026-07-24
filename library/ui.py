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
    original_user = os.environ.get('SUDO_USER')
    if not original_user:
        logging.info("Not running under sudo, using current user")
        original_user = os.environ.get('USER')
    
    dbus_addr = None
    
    # Try to get it from the user's environment
    if original_user:
        try:
            result = subprocess.run(
                ['sudo', '-u', original_user, 'bash', '-c', 
                 'echo $DBUS_SESSION_BUS_ADDRESS'],
                capture_output=True,
                text=True
            )
            dbus_addr = result.stdout.strip()
            if dbus_addr:
                print(f"Found DBus address from user env: {dbus_addr}")
                return dbus_addr, original_user
        except Exception as err:
            logging.info(f"Could not get DBus from user env", exc_info=err)

    # If that fails, try to find the socket file
    try:
        # Get the user's UID
        uid_result = subprocess.run(
            ['id', '-u', original_user],
            capture_output=True,
            text=True
        )
        uid = uid_result.stdout.strip()
        
        # The socket should be in /run/user/{uid}/bus (maybe)
        socket_path = f"/run/user/{uid}/bus"
        if os.path.exists(socket_path):
            dbus_addr = f"unix:path={socket_path}"
            logging.info(f"Found DBus socket at: {socket_path}")
            return dbus_addr, original_user
            
        # look for sockets in /tmp
        tmp_sockets = glob.glob("/tmp/dbus-*")
        if tmp_sockets:
            # Usually the first one is the right one, but you might need
            # to find the one owned by the user
            for socket in tmp_sockets:
                if os.path.exists(socket):
                    dbus_addr = f"unix:path={socket}"
                    print(f"Found DBus socket at: {socket}")
                    return dbus_addr, original_user
    except Exception as err:
        logging.error("Error finding DBus socket", exc_info=err)

    # It might be in the environment variables
    dbus_addr = os.environ.get('DBUS_SESSION_BUS_ADDRESS')
    if dbus_addr:
        logging.info(f"Using DBus from current env: {dbus_addr}")
        return dbus_addr, original_user
    
    logging.warning("Could not find DBus session address")
    return None, original_user

async def alert_user(report: dict):
    """
    Sends alerts to the user's OS in a form of pop-up notifications.
    """
    if shutil.which("notify-send") is None:
        if not settings.headless().get():
            raise errors.missing_notifysend
        else:
            raise NotImplementedError("HUB mode still needs to be implemented.")
    
    dbus_addr, original_user = find_dbus_socket()
    
    # Get the user's display
    display = os.environ.get('DISPLAY')
    if not display and original_user:
        try:
            result = subprocess.run(
                ['sudo', '-u', original_user, 'bash', '-c', 'echo $DISPLAY'],
                capture_output=True,
                text=True
            )
            display = result.stdout.strip() or ':0'
        except Exception:
            display = ':0'
    
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
            'sudo', '-u', original_user,
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
                    'sudo', '-u', original_user,
                    'env', f'DISPLAY={display}',
                    'notify-send', '-u', 'critical', "Doctor's Report", check_warn_msg
                ]
                subprocess.run(fallback_cmd, check=False, capture_output=True)
            except Exception as err:
                logging.error("Fallback notification also failed", exc_info=err)