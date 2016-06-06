"""Samantha's devices module.

 - forwards commands to devices (like set property COLOR of LED to GREEN)
 - fires events into the INPUT queue when an device's status changes
   (e.g. if it becomes un-/available)"""

###############################################################################
#
# TODO: [ ] _init()
# TODO: [ ]     load devices & add them to INDEX
# TODO: [ ] stop()
# TODO: [ ]     stop devices if necessary
# TODO: [ ] def process(keyword, params={}):
# TODO: [ ] monitor status changes
# TODO: [ ] comments
#
###############################################################################


import glob
import imp
import logging
import os.path

import core


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

INDEX = {}
KEYWORDS = {}

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    """Generates an incrementing UID for each device."""
    global UID
    uid = "d_{0:04d}".format(UID)
    UID += 1
    return uid


def add_to_index(device):
    """Adds a device to the indexes."""
    global INDEX, KEYWORDS
    INDEX[device.uid] = device
    for key in device.keywords:
        if key in KEYWORDS:
            KEYWORDS[key].append(device)
        else:
            KEYWORDS[key] = [device]


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # initialize all devices
    LOGGER.debug("Searching for devices...")
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    files = glob.glob("{}/*_device.py".format(this_dir))
    LOGGER.debug("%d possible devices found.", len(files))

    for i in range(len(files)):
        LOGGER.debug("Trying to import %s...", files[i])

        try:
            device_source = imp.load_source(
                files[i].replace("samantha/", "")
                        .replace("/", ".")
                        .replace("_device.py", ""),
                files[i])
            LOGGER.debug("Successfully imported %s", files[i])
            if hasattr(device_source, "Device"):
                uid = get_uid()
                new_device = device_source.Device(uid)
                if new_device.is_active:
                    add_to_index(new_device)
                    LOGGER.debug("%s is a valid Device.", files[i])
            else:
                LOGGER.warn("%s is missing the Device-class!", files[i])
        except ImportError:
            LOGGER.warn("%s couldn't be imported successfully!", files[i])
        # except AttributeError:
        #     LOGGER.warn("%s is not a valid device!", files[i])

    LOGGER.info("Initialisation complete.")
    s = ""
    for i in INDEX:
        s += "\n\t%s:\t%r" % (i, INDEX[i])
    LOGGER.debug("Imported %d Devices: %s", len(INDEX), s)
    core.add_keywords(KEYWORDS)
    return True


def stop():
    """Stops the module and all associated devices."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all devices
    for UID in INDEX:
        INDEX[UID].stop()

    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
