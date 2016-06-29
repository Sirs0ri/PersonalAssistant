"""Samantha's services module.

- forwards commands to services (like get WEATHER-REPORT)
- fires events into the INPUT queue when an services's status changes(e.g. if
  it becomes un-/available or if the service itself triggers a command)
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


__version__ = "1.0.13"


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
    """Generate an incrementing UID for each service."""
    global UID
    uid = "s_{0:04d}".format(UID)
    UID += 1
    return uid


def add_to_index(service):
    """Add a device to the indexes."""
    INDEX[service.uid] = service
    for key in service.keywords:
        if key in KEYWORDS:
            KEYWORDS[key].append(service)
        else:
            KEYWORDS[key] = [service]


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # initialize all services
    LOGGER.debug("Searching for services...")
    this_dir = os.path.split(__file__)[0]  # ..[1] would be the filename
    files = glob.glob("{}/*_service.py".format(this_dir))
    LOGGER.debug("%d possible services found.", len(files))

    for service_file in files:
        LOGGER.debug("Trying to import %s...", service_file)

        try:
            name = service_file.replace("samantha/", "") \
                               .replace("/", ".") \
                               .replace("_service.py", "")
            service_source = imp.load_source(name, service_file)
            LOGGER.debug("Successfully imported %s", service_file)
            if hasattr(service_source, "Service"):
                uid = get_uid()
                new_service = service_source.Service(uid)
                if new_service.is_active:
                    add_to_index(new_service)
                    LOGGER.debug("%s is a valid Service.", service_file)
                else:
                    LOGGER.debug("%s is marked as inactive.", service_file)
            else:
                LOGGER.warn("%s is missing the Service-class!", service_file)
        except ImportError:
            LOGGER.warn("%s couldn't be imported successfully!", service_file)

    LOGGER.info("Initialisation complete.")
    service_str = ""
    for i in INDEX:
        service_str += "\n\t%s:\t%r" % (i, INDEX[i])
    LOGGER.debug("Imported %d Services: %s", len(INDEX), service_str)
    core.add_keywords(KEYWORDS)
    return True


def stop():
    """Stop the module and all associated services."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all services
    for uid in INDEX:
        INDEX[uid].stop()

    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
