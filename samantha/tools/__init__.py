"""A collection of different tools Samantha might use.

 - Updater, to monitor it's sources on GitHub and automatically update to newer
   versions, if available and if a certain series of tests passes"""

###############################################################################
#
# TODO: [ ] Updater
# TODO: [ ]     Monitor Sources for the modules
# TODO: [ ]     Test new versions
# TODO: [ ]     replace them on-the-go if tests are passed
# TODO: [ ]     keep the old version as backup for a certain time (maybe check
#               every 24h and discard old versions 24h later if nothing's gone
#               wrong?)
#
###############################################################################


import logging

import server


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

LOGGER.debug("I was imported.")


def _init(InputQueue, OutputQueue):
    """Initializes the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = InputQueue
    OUTPUT = OutputQueue

    # initialize all tools
    server.initialize(InputQueue, OutputQueue)

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all tools
    server.stop()

    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
