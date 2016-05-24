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
#
###############################################################################


import logging


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

INDEX = {}

UID = 0

LOGGER.debug("I was imported.")


def get_uid():
    global UID
    uid = "d_{0:04d}".format(UID)
    UID += 1
    return uid


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # initialize all devices
    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all devices
    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
