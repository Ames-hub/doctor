from library.database import create_tables
from library.settings import settings
from library import doctor
from library import ui
import datetime
import logging
import asyncio
import sys
import os

# Create the sqlite db
create_tables()

if not settings.pc_uuid4().get():
    settings.pc_uuid4().gen_new_uuid()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=f"logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log",
    level=logging.INFO,
    format=""
)

is_hub = settings.HubMode().get()

def check_root():
    # os.geteuid() returns the effective User ID of the current process
    if os.geteuid() != 0:
        logging.warning("This script was designed to be run as root or with sudo.")

def is_running_under_systemd():
    # systemd sets INVOCATION_ID or JOURNAL_STREAM for its services
    return "INVOCATION_ID" in os.environ or "JOURNAL_STREAM" in os.environ

if not is_running_under_systemd():
    logging.warning("Doctor was built to run as a systemd Daemon, but we have detected we are not running as one, or the Systemd version is older than v231, in which case, please ignore this message.")

async def main_loop():
    HALF_DAY = 43200
    while True:
        logging.info(f"Beginning a check at timestamp {datetime.datetime.now().timestamp()}")
        system_report = doctor.diagnose()
        translation = ui.translate_report(system_report)
        await ui.send_alert(translation)
        logging.info(f"Check concluded at timestamp {datetime.datetime.now().timestamp()}")
        await asyncio.sleep(HALF_DAY)

if is_hub:
    raise NotImplementedError("HUB Mode is not yet finished.")
else:
    if "--debug" not in sys.argv:
        check_root()
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Shutting down.")
        exit(0)