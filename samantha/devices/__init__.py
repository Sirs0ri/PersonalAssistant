"""Samantha's devices module.

- forwards commands to devices (like set property COLOR of LED to GREEN)
- fires events into the INPUT queue when an device's status changes
  (e.g. if it becomes un-/available)
"""

###############################################################################
# pylint: disable=global-statement
#
# TODO: [ ] monitor status changes
#
###############################################################################


# standard library imports
import glob
import imp
import logging
import os.path

# related third party imports

# application specific imports
# pylint: disable=import-error
import core
# pylint: enable=import-error


__version__ = "1.1.3"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """Generate an incrementing UID for each device."""
    global UID
    uid = "d_{0:04d}".format(UID)
    UID += 1
    return uid


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # initialize all devices
    LOGGER.debug("Searching for devices...")
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    files = glob.glob("{}/*_device.py".format(this_dir))
    LOGGER.debug("%d possible devices found.", len(files))

    for device_file in files:
        LOGGER.debug("Trying to import %s...", device_file)

        try:
            name = device_file.replace("samantha/", "") \
                              .replace("/", ".") \
                              .replace("_device.py", "")
            device_source = imp.load_source(name, device_file)
            LOGGER.debug("Successfully imported %s", device_file)
            if hasattr(device_source, "DEVICE"):
                if device_source.DEVICE.is_active:
                    LOGGER.debug("%s is a valid Device.", device_file)
                else:
                    LOGGER.debug("%s is marked as inactive.", device_file)
            else:
                LOGGER.warn("%s is missing the Device-class!", device_file)
        except ImportError:
            LOGGER.warn("%s couldn't be imported successfully!", device_file)

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stop the module and all associated devices."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
