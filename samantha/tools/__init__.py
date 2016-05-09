import logging

# TODO: Add Updater

LOGGER = logging.getLogger(__name__)
INITIALIZED = False

LOGGER.debug("I was imported.")


def _init():
    LOGGER.info("Initializing...")
    return True


def stop():
    global INITIALIZED
    LOGGER.info("Exiting...")
    INITIALIZED = False
    return True


def initialize():
    global INITIALIZED
    if not INITIALIZED:
        INITIALIZED = _init()
    else:
        LOGGER.info("Already initialized!")
