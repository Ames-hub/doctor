from library.settings import settings
from datetime import datetime
from library import errors
import importlib
import logging
import uuid
import os

checks = []
PROJ_ROOT = os.getcwd()

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
        checks.append((module.check, module.DISPLAY_NAME))
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

def gen_pc_uuid():
    return settings.pc_uuid4().set(str(uuid.uuid4()))

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