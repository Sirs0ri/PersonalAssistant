"""A collection of different tools Samantha might use.

- Updater, to monitor it's sources on GitHub and automatically update to newer
  versions, if available and if a certain series of tests passes
"""

###############################################################################
# pylint: disable=global-statement
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


# standard library imports
import logging

# related third party imports

# application specific imports
from . import eventbuilder
from . import server


__version__ = "1.3.8"


# Initialize the logger
LOGGER = logging.getLogger(__name__)

# Set constants
INITIALIZED = False

INPUT = None
OUTPUT = None

LOGGER.debug("I was imported.")


def _init(queue_in, queue_out):
    """Initialize the module."""
    global INPUT, OUTPUT

    LOGGER.info("Initializing...")
    INPUT = queue_in
    OUTPUT = queue_out

    # initialize all tools
    eventbuilder.initialize(queue_in, queue_out)
    server.initialize(queue_in, queue_out)

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stop the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False

    # Stop all tools
    eventbuilder.stop()
    server.stop()

    LOGGER.info("Exited.")
    return True


def initialize(queue_in, queue_out):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(queue_in, queue_out)
    else:
        LOGGER.info("Already initialized!")
