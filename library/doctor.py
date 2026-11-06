from datetime import datetime, timedelta
from library.settings import settings
from library.database import get_db
from sqlalchemy import delete
from library import models 
from library import errors
import importlib
import platform
import logging
import shutil
import os

checks = []
PROJ_ROOT = os.getcwd()

def get_pkg_manager():
    distro = platform.freedesktop_os_release().get("ID", "").lower()

    if distro in ("ubuntu", "debian", "linuxmint"):
        package_manager = "apt"
    elif distro in ("fedora",):
        package_manager = "dnf"
    else:
        raise RuntimeError(f"Unsupported distribution: {distro}")

    if not shutil.which(package_manager):
        raise errors.missing_pkg_manager(f"{package_manager} is not installed.")

def is_root():
    # os.geteuid() returns the effective User ID of the current process
    return os.geteuid() == 0

def register_check(rel_filepath: str):
    module_name = rel_filepath[:-3]
    try:
        module = importlib.import_module(module_name)
    except Exception as err:
        logging.error(f"Error importing a check! Module name: {module_name}", exc_info=err)
        return False
    if hasattr(module, "check"):
        verbosity = settings.Verbosity().get()
        if module.LEVEL > verbosity:
            # This check is too verbose for the user's settings, do not register it.
            raise errors.too_verbose
        try:
            checks.append((module.check, module.DISPLAY_NAME))
        except AttributeError as err:
            logging.error("Error loading check, missing required variables in file", exc_info=err)
    return True

for checks_root, _, files in os.walk("checks"):
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            try:
                path = os.path.join(checks_root, file).replace("/", ".")
                register_check(path)
            except errors.too_verbose:
                logging.info(f"Check at \"{path}\" is too verbose for the user's settings, load skipped.")
            except Exception as err:
                logging.error(f"Error when attempting to load a check at \"{path}\"", exc_info=err)
                continue

def diagnose() -> dict:
    """
    Runs all of the checks in the folder "checks"
    """
    diagnosis = {}

    for check in checks:
        try:
            logging.info(f"Running check '{check[1]}' at timestamp {datetime.now().timestamp()}")
            diagnosis[check[1]] = check[0]()
            logging.info(f"Check ran successfully.")
        except errors.missing_systemd:
            logging.warning(f"Doctor Daemon performance degraded, cannot run check '{check[1]}': SystemD is not present on this device.")
        except errors.missing_journalctl:
            logging.warning(f"Doctor Daemon performance highly degraded, cannot run check '{check[1]}': JournalCTL is not present on this device.")
        except errors.missing_systemctl:  #  Rue the day systemctl is not installed on a device that would have doctor installed
            logging.warning(f"Doctor Daemon performance highly degraded, cannot run check '{check[1]}': SystemCTL is not present on this device.")
        except Exception as err:
            logging.error(f"Error when running check \"{check[1]}\"", exc_info=err)

    diagnosis["pc_uuid4"] = settings.pc_uuid4().get()

    return diagnosis

tasks_list = []

def register_task(rel_filepath: str):
    module_name = rel_filepath[:-3]
    try:
        module = importlib.import_module(module_name)
    except Exception as err:
        logging.error(f"Error importing a task! Module name: {module_name}", exc_info=err)
        return False
    if hasattr(module, "task"):
        try:
            tasks_list.append((module.task, module.CLOCK, module.TASK_ID))
        except AttributeError as err:
            logging.error("Error importing a task! Missing required variables inside file", exc_info=err)
            return False
    return True

for checks_root, _, files in os.walk("tasks"):
    for file in files:
        if file.endswith(".py") and file != "__init__.py":
            try:
                path = os.path.join(checks_root, file).replace("/", ".")
                register_task(path)
            except Exception as err:
                logging.error(f"TASK LOAD ERROR: when attempting to load a task at \"{path}\"", exc_info=err)
                continue

def get_last_exec(func_id) -> datetime:
    with get_db() as session:
        data = (
            session.query(models.task_execution)
            .filter(models.task_execution.uuid == func_id)
            .one_or_none()
        )
        if data:
            return datetime.fromtimestamp(data.time)
        return None

def save_last_exec(func_id: str) -> bool:
    with get_db() as session:
        session.execute(
            delete(models.task_execution)
            .where(models.task_execution.uuid == func_id)
        )
        record = models.task_execution(
            time=int(datetime.now().timestamp()),
            uuid=func_id,
        )
        session.add(record)
        session.commit()
    return True

async def tasks_loop():
    if not is_root():
        logging.warning("Warning, no tasks are running as root. This may cause misbehavior with checks.")
    for task in tasks_list:
        func = task[0]
        clock: timedelta = task[1]
        func_id = task[2]
        last_execution = get_last_exec(func_id)

        do_run = False

        if not last_execution:
            do_run = True
        else:
            time_gap = datetime.now() - last_execution
            if (time_gap.total_seconds() - clock.total_seconds()) <= 0:
                do_run = True

        if do_run:
            func()
            save_last_exec(func_id)