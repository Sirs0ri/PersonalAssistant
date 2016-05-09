"""Samantha's services module.

 - forwards commands to services (like get WEATHER-REPORT)
 - fires events into the INPUT queue when an services's status changes(e.g. if
   it becomes un-/available or if the service itself triggers a command)"""

###############################################################################
#
# TODO: [ ] _init()
# TODO: [ ]     load services
# TODO: [ ] stop()
# TODO: [ ]     stop services if necessary
# TODO: [ ] def process(keyword, params={}):
# TODO: [ ] monitor status changes
#
###############################################################################


import logging


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    """Initializes the module."""
    LOGGER.info("Initializing...")

    # initialize all services
    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all services
    LOGGER.info("Exited.")
    return True


def initialize():
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
