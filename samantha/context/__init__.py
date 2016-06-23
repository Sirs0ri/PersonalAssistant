"""Samantha's context module.

 - Handles storing the current context
 - saves/loads it when the program is ended/started.
 - Repeatedly compares the context against a given set of rules to allow basic
   automation"""

###############################################################################
#
# TODO: [ ] finish initialize() and stop()
# TODO: [ ]     Start a new context, then load the last one
# TODO: [ ]     Start context-updater
# TODO: [ ]         Checks if properties are expired
# TODO: [ ]         Compares Context and rules
# TODO: [ ] finish stop()
# TODO: [ ]     Store the current context as JSON
# TODO: [ ] def import_from_file(path="data/context.json"):
# TODO: [ ]     Load a previous context from JSON, then:
# TODO: [ ]     Compare the property's TTLs to the current time and load only
#               valide ones
# TODO: [ ] def setProperty(property, value, ttl):
# TODO: [ ] def getProperty(property):
# TODO: [ ] def addRule(rule):
#
###############################################################################


import logging


__version__ = "0.4.1"


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

    LOGGER.info("Initialisation complete.")
    return True


def stop():
    """Stops the module."""
    global INITIALIZED

    LOGGER.info("Exiting...")
    INITIALIZED = False
    LOGGER.info("Exited.")
    return True


def initialize(InputQueue, OutputQueue):
    """Initialize the module when not yet initialized."""
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init(InputQueue, OutputQueue)
    else:
        LOGGER.info("Already initialized!")
