"""Samantha's services module.

 - forwards commands to services (like get WEATHER-REPORT)
 - fires events into the INPUT queue when an services's status changes(e.g. if
   it becomes un-/available or if the service itself triggers a command)"""

###############################################################################
#
# TODO: [ ] _init()
# TODO: [ ]     load services & add them to INDEX
# TODO: [ ] stop()
# TODO: [ ]     stop services if necessary
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


__version__ = "1.0.1"


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
    """Generates an incrementing UID for each service."""
    global UID
    uid = "s_{0:04d}".format(UID)
    UID += 1
    return uid


def add_to_index(service):
    """Adds a device to the indexes."""
    global INDEX, KEYWORDS
    INDEX[service.uid] = service
    for key in service.keywords:
        if key in KEYWORDS:
            KEYWORDS[key].append(service)
        else:
            KEYWORDS[key] = [service]


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # initialize all services
    LOGGER.debug("Searching for services...")
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    files = glob.glob("{}/*_service.py".format(this_dir))
    LOGGER.debug("%d possible services found.", len(files))

    for i in range(len(files)):
        LOGGER.debug("Trying to import %s...", files[i])

        try:
            service_source = imp.load_source(
                files[i].replace("samantha/", "")
                        .replace("/", ".")
                        .replace("_service.py", ""),
                files[i])
            LOGGER.debug("Successfully imported %s", files[i])
            if hasattr(service_source, "Service"):
                UID = get_uid()
                new_service = service_source.Service(UID)
                if new_service.is_active:
                    add_to_index(new_service)
                    LOGGER.debug("%s is a valid Service.", files[i])
            else:
                LOGGER.warn("%s is missing the Service-class!", files[i])
        except ImportError:
            LOGGER.warn("%s couldn't be imported successfully!", files[i])
        # except AttributeError:
        #     LOGGER.warn("%s is not a valid service!", files[i])

    LOGGER.info("Initialisation complete.")
    s = ""
    for i in INDEX:
        s += "\n\t%s:\t%r" % (i, INDEX[i])
    LOGGER.debug("Imported %d Services: %s", len(INDEX), s)
    core.add_keywords(KEYWORDS)
    return True


def stop():
    """Stops the module and all associated services."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all services
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
