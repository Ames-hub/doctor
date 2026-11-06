from library.database import create_tables
from library.settings import settings
from library import doctor
from library import hub
from library import ipc
from library import ui
import datetime
import logging
import asyncio
import json
import sys
import os

# Handle a CLI-triggered manual scan before any daemon setup runs
if "--scannow" in sys.argv:
    if not doctor.is_root():
        print("This command must be ran as root.")
        exit(126)
    async def _scannow_client():
        try:
            result = await ipc.send_scannow_request()
            print(json.dumps(result, indent=2))
        except (ConnectionRefusedError, FileNotFoundError):
            print("Could not reach the Doctor daemon. Is the systemd service running?")
            sys.exit(1)

    if not doctor.is_root():
        print("This command must be ran as root.")
        sys.exit(0)

    asyncio.run(_scannow_client())
    sys.exit(0)

# Create the sqlite db
create_tables()

if not settings.pc_uuid4().get():
    settings.pc_uuid4().gen_new_uuid()


LOGGING_PATH = os.path.join(os.getcwd(), f"logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log")
os.makedirs(os.path.join(os.getcwd(), ("logs")), exist_ok=True)
logging.basicConfig(
    filename=LOGGING_PATH,
    level=logging.INFO,
    format=""
)

is_hub = settings.HubMode().get()
is_client = settings.ClientMode().get()

def is_running_under_systemd():
    # systemd sets INVOCATION_ID or JOURNAL_STREAM for its services
    return "INVOCATION_ID" in os.environ or "JOURNAL_STREAM" in os.environ

if not is_running_under_systemd():
    logging.warning("Doctor was built to run as a systemd Daemon, but we have detected we are not running as one, or the Systemd version is older than v231, in which case, please ignore this message.")

async def run_scan():
    """
    Runs a full diagnostic scan, translates the report, and sends a GUI Alert if it can.
    """
    logging.info(f"Beginning a check at timestamp {datetime.datetime.now().timestamp()}")
    system_report = doctor.diagnose()
    translation = ui.translate_report(system_report)
    await ui.send_alert(translation)
    logging.info(f"Check concluded at timestamp {datetime.datetime.now().timestamp()}")
    return translation

async def main_loop():
    HALF_DAY = 43200
    while True:
        await run_scan()
        await asyncio.sleep(HALF_DAY)

async def run_daemon():
    tasks = [
        main_loop(),
        doctor.tasks_loop()
    ]

    if doctor.is_root():
        tasks.append(ipc.run_server(run_scan))
    else:
        logging.warning(
            "Doctor is not running as root, command line commands will not work."
        )

    if is_hub:
        tasks.append(hub.server.run())

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    if "--debug" not in sys.argv:
        if not doctor.is_root():
            logging.warning("This script was designed to be run as root or with sudo.")

    try:
        asyncio.run(run_daemon())
    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Shutting down.")
        sys.exit(0)